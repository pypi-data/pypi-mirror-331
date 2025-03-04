from pathlib import Path

from dataclasses import dataclass

import re
import os

import logging

logger = logging.getLogger(__name__)

IMAGE_REPO = os.environ.get("IMAGE_REPO", "docker.cyberlandslaget.no/2024")

from different_wrapping.utils import docker_port_string_get_external_port


def normalize(text):
    return re.sub(r"-*$", "", re.sub(r"[^a-zA-Z0-9\-]", "-", text))


@dataclass
class DockerImage:
    dockerfile: Path
    context: Path
    url: str
    tags: list[str]

    def serialize(self):
        return {
            "dockerfile": str(self.dockerfile.absolute()),
            "context": str(self.context.absolute()),
            "url": self.url,
            "tags": self.tags,
        }


# Docker-compose linters
def service_name_requirement(container, svc_name):
    if re.match(r"^[a-zA-Z0-9\-]+$", svc_name) is None:
        return "Docker-compose service name must be in the form [a-zA-Z0-9\-]+ due to kompose renaming them otherwise."
    return None


def no_volumes(container, svc_name):
    if "volumes" in container.container_dict:
        return "No volumes are allowed. Build data into the docker container instead using COPY!"
    return None


def no_long_format_ports(container, svc_name):
    if "ports" in container.container_dict:
        for port in container.container_dict["ports"]:
            if isinstance(port, dict):
                return "Long-format port declarations are not allowed as they are not necessary"

    return None


docker_compose_linters = [service_name_requirement, no_volumes, no_long_format_ports]


class Container:
    def __init__(self, name: str, challenge, container_dict: dict):
        self.name = name
        self.challenge = challenge
        self.container_dict = container_dict

    def is_built(self):
        return "build" in self.container_dict

    def lint(self, name):
        success = True

        for linter in docker_compose_linters:
            status = linter(self, name)
            if status is not None:
                logger.error("Validation failed for %s: %s" % (name, status))
                success = False

        return success

    def patch_build(self, args, challenge_dir: Path, version_tag: str):
        """Patches the build part of a docker-compose service, turning it into an image URL"""
        # Extract necessary info
        dockerfile_name = self.container_dict["build"]["dockerfile"]

        context = (
            challenge_dir
            if not ("context" in self.container_dict["build"])
            else (challenge_dir / Path(self.container_dict["build"]["context"]))
        )

        dockerfile = context / Path(dockerfile_name)

        image_name = normalize(dockerfile_name.lower().replace("dockerfile", ""))
        if len(image_name) > 0:
            image_url = "%s/%s/%s" % (
                args.docker_image_repo,
                normalize(challenge_dir.name),
                image_name,
            )
        else:
            image_url = "%s/%s" % (
                args.docker_image_repo,
                normalize(challenge_dir.name),
            )

        image_url = image_url.lower()

        logger.info(f"Determined docker image URL {image_url} for {challenge_dir.name}")
        del self.container_dict["build"]
        self.container_dict["image"] = "%s:%s" % (image_url, version_tag)

        return DockerImage(dockerfile, context, image_url, [version_tag])

    def patch(self):
        """Perform misc cleanups to the service"""
        if "ports" in self.container_dict:
            ports = self.container_dict["ports"]
            for idx, port in enumerate(ports):
                components = port.split(":")
                if len(components) == 1:
                    # No external port, nothing to do
                    continue
                elif len(components) == 2:
                    ports[idx] = components[1]
                elif len(components) == 3:
                    ports[idx] = components[2]

    def has_label(self, target_label):
        logger.debug(self.container_dict)
        if "labels" not in self.container_dict:
            return False
        labels = self.container_dict["labels"]

        if isinstance(labels, dict):
            return target_label in labels
        elif isinstance(labels, list):
            for label in self.container_dict["labels"]:
                logger.debug(label.split("=")[0])
                if label.split("=")[0] == target_label:
                    return True
        else:
            raise RuntimeError("Lable is of invalid type")
        return False

    def get_label(self, target_label):
        logger.debug(self.container_dict)

        if "labels" not in self.container_dict:
            raise RuntimeError("Container does not have labels")

        labels = self.container_dict["labels"]

        # The label list can be both a dictionary or a list
        if isinstance(labels, dict):
            return labels[target_label]
        elif isinstance(labels, list):
            for label in self.container_dict["labels"]:
                split = label.split("=")
                if split[0] == target_label:
                    return split[1]

    def get_dns_name(self, dns_host):
        host = f"{self.name}-{self.challenge.safe_name()}.{dns_host}"
        if self.has_label("no.cyberlandslaget.dns_challenge_name"):
            logger.debug(
                f"Challenge {self.name()} service {self.name} has custom DNS name - using it"
            )
            host = (
                f"{self.get_label('no.cyberlandslaget.dns_challenge_name')}.{dns_host}"
            )

        return host

    def ports(self):
        return [
            docker_port_string_get_external_port(port)
            for port in self.container_dict["ports"]
        ]

    def serialize(self, dns_host):
        access_type = "none"

        access = None

        if self.has_label("no.cyberlandslaget.http"):
            access = f"https://{self.get_dns_name(dns_host)}"
        elif self.has_label("no.cyberlandslaget.tcp"):
            port = self.ports()[0]
            access = f"{self.get_dns_name(dns_host)}:{port}"

        if self.has_label("no.cyberlandslaget.http"):
            access_type = "http"

        elif "ports" in self.container_dict and len(self.container_dict["ports"]) > 0:
            access_type = "tcpudp"

        base_dict = {
            "deploy_type": "dynamic" if "dynamic" in self.name else "static",
            "access_type": access_type,
            "access": access,
            "random_password_env": self.get_label(
                "no.cyberlandslaget.autogenerated_password"
            )
            if self.has_label("no.cyberlandslaget.autogenerated_password")
            else None,
            "name": self.get_label("no.cyberlandslaget.frontendName")
            if self.has_label("no.cyberlandslaget.frontendName")
            else self.name,
            "svc_name": self.name,
        }

        return base_dict
