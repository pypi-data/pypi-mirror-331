from pathlib import Path

import yaml
import re

try:
    from yaml import CLoader as Loader
except ImportError:
    from yaml import Loader

import logging

logger = logging.getLogger(__name__)

from different_wrapping.compose import Container


class Challenge:
    def __init__(self, path: Path):
        self.path = path
        self.has_containers = True

        self.containers = {}
        logger.info("Loading challenge: %s" % self.relative_path())

        docker_compose = path / Path("docker-compose.yml")
        if docker_compose.exists():
            logger.debug("Docker-compose file found, parsing")
            self._read_docker_compose(docker_compose)
        else:
            compose = path / Path("compose.yml")
            if compose.exists():
                logger.debug("compose.yml found, parsing")
                self._read_compose(compose)
            else:
                self.has_containers = False

    def _read_docker_compose(self, compose_file):
        with compose_file.open() as f:
            compose = yaml.load(f, Loader)

        if compose["version"] != "3":
            raise RuntimeError(
                "Error parsing %s - only version 3 of compose is supported. See https://docs.docker.com/compose/compose-file/compose-file-v3/"
                % compose_file
            )

        for key, service in compose["services"].items():
            self.containers[key] = Container(key, self, service)

    def _read_compose(self, compose_file):
        with compose_file.open() as f:
            compose = yaml.load(f, Loader)

        for key, service in compose["services"].items():
            self.containers[key] = Container(key, self, service)

    def category(self):
        return self.path.parent.name

    def name(self):
        return self.path.name

    def cyber_name(self):
        # Cyberlandslaget hack
        with open(self.path / "challenge.yaml", "r") as f:
            parsed = yaml.safe_load(f)
            return parsed["title"]

    def safe_name(self):
        return re.sub(r"[^a-zA-Z0-9]", "-", self.name()).lower()

    def relative_path(self):
        return "%s/%s" % (self.category(), self.name())

    def challenge_id(self):
        # Cyberlandslaget hack
        return ("%s/%s" % (self.category(), self.cyber_name())).lower()

    def determine_version(self, args):
        """Determine some docker tag-friendly version label for the containers to be built"""
        # For now use latest. Once we are in production we will switch to using semver using git describe
        return args.docker_tag

    def get_images_to_be_built(self, args):
        version = self.determine_version(args)

        containers = []
        for key, container in self.containers.items():
            if container.is_built():
                containers.append(container.patch_build(args, self.path, version))
        return containers

    def patch(self):
        for key, container in self.containers.items():
            container.patch()

    def lint(self):
        # Was there any failures?
        success = not any(
            map(lambda kv: not kv[1].lint(kv[0]), self.containers.items())
        )

        if not success:
            logger.error("Failed to validate %s" % self.relative_path())

        return success

    def has_containers(self):
        return len(self.containers.keys()) > 0

    def has_dynamic_challenges(self):
        return any(["dynamic" in name for name in self.containers.keys()])

    def has_static_challenges(self):
        return any(["dynamic" not in name for name in self.containers.keys()])

    def serialize(self, args):
        return {
            "relative_path": self.relative_path(),
            "challenge_id": self.challenge_id(),
            "has_containers": len(self.containers.keys()) > 0,
            "has_dynamic_containers": self.has_dynamic_challenges(),
            "has_static_containers": self.has_static_challenges(),
            "services": [
                self.containers[key].serialize(args.dns_host)
                for key in self.containers.keys()
            ],
        }


def enumerate_challenges(challengeroot: Path):
    logger.info("Enumerating challenges...")

    challenges = []

    for folder in challengeroot.glob("*/*"):
        if folder.is_file():
            logger.info(f"{folder} is file - skipping")
            continue
        if folder.parent.name in [".git", ".github"]:
            logger.info("Skipping %s" % folder)
            continue
        challenges.append(Challenge(folder))

    logger.info("Found %d challenges" % len(challenges))

    return challenges
