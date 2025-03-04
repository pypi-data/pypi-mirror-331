# Responsible for converting the docker-compose style manifests to a k8s kustomize project
import tempfile
import shutil
import subprocess
from pathlib import Path

from different_wrapping.ingress import generate_ingress
from different_wrapping.gateway import generate_gateway, generate_tcp_gateway

import yaml

import logging

logger = logging.getLogger(__name__)


def tempdir():
    """Debugging purposes"""
    import uuid

    directory = Path("/tmp") / str(uuid.uuid4())
    directory.mkdir(parents=True)
    return directory


def build_challenge_kustomize(files, out_file):
    """Builds the kustomize manifest for a challenge"""
    logger.info("Building for %s" % files)
    manifest = {
        "apiVersion": "kustomize.config.k8s.io/v1beta1",
        "kind": "Kustomization",
        "resources": [f.name for f in files],
    }

    with out_file.open("w") as f:
        yaml.dump(manifest, f)


def build_kustomize_manifest(challenges, folder):
    """Builds the topmost kustomize manifest which includes all challenges"""
    manifest = {
        "apiVersion": "kustomize.config.k8s.io/v1beta1",
        "kind": "Kustomization",
        "resources": [
            "./%s" % challenge.relative_path()
            for challenge in filter(
                lambda challenge: challenge.has_containers
                and challenge.has_static_challenges(),
                challenges,
            )
        ],
    }

    out_file = folder / Path("kustomization.yml")

    with out_file.open("w") as f:
        yaml.dump(manifest, f)


def build_k8s_manifests(challenge, output, filter_lambda, args):
    """Builds k8s manifests to a given base directory(organized by challenge type).
    selector_lambda allows filtering of what containers to use"""
    logger.info("Processing %s" % challenge.relative_path())

    # with tempfile.TemporaryFile() as compose_file:
    # with tempfile.TemporaryDirectory() as workdir:
    workdir = Path(tempdir())

    service_dict = {
        key: value.container_dict
        for key, value in filter(filter_lambda, challenge.containers.items())
    }
    if len(service_dict.keys()) == 0:
        logger.info(
            "Challenge %s has no services valid for %s - skipping"
            % (challenge.relative_path(), str(output))
        )
        return

    compose_file = workdir / "docker-compose.yml"

    logger.info("Writing to %s" % compose_file)
    compose_data = {"version": "3", "services": service_dict}
    with compose_file.open("w") as f:
        yaml.dump(compose_data, f)

    kompose_args = ["kompose", "-f", "docker-compose.yml", "convert"]

    result = subprocess.run(kompose_args, cwd=workdir, capture_output=True)

    if result.returncode != 0:
        logger.error("Failed to run kompose! stderr: \n%s" % result.stderr)

    logger.info(
        "Kompose returned %d\nstdout %s\nstderr %s"
        % (result.returncode, result.stdout, result.stderr)
    )

    # Generate ingress
    generate_challenge_ingresses(challenge, workdir, args)

    # Manifest files to be copied
    files = list(
        filter(lambda file: not ("docker-compose" in file.name), workdir.iterdir())
    )
    logger.info("Files: %s" % len(files))
    if not args.dry:
        # Create the output folder
        output_dir = output / Path(challenge.relative_path())
        output_dir.mkdir(parents=True, exist_ok=True)

        # Build kustomize file
        kustomize_file = output_dir / Path("kustomization.yml")
        build_challenge_kustomize(files, kustomize_file)

        # Copy over files
        for file in files:
            dest = output_dir / Path(file.name)
            logger.debug("%s -> %s" % (file, dest))
            shutil.copyfile(file, dest)

        logger.debug("Done copying files")


def generate_challenge_ingresses(challenge, outdir, args):
    outfile = outdir / "different-wrapping-ingress.yaml"

    ingresses = []

    for service_name, service in challenge.containers.items():
        logger.debug(service_name)
        if service.has_label("no.cyberlandslaget.http"):
            logger.info("Container has http label, creating ingress")
            if args.ingress_type == "ingress":
                ingresses.append(
                    generate_ingress(service_name, service, challenge, args)
                )
            else:
                ingresses.append(
                    generate_gateway(service_name, service, challenge, args)
                )
        elif service.has_label("no.cyberlandslaget.tcp"):
            logger.info("Container has TCP ingress, creating TCP route")
            if args.ingress_type == "ingress":
                raise RuntimeError(
                    "Ingress type ingress not supported with TCP challenges"
                )
            else:
                ingresses = ingresses + generate_tcp_gateway(
                    service_name, service, challenge, args
                )
        else:
            logger.info("Container has no ingress requirement")

    if len(ingresses) > 0:
        with outfile.open("w") as f:
            f.write("\n---\n".join([yaml.dump(ingress) for ingress in ingresses]))
