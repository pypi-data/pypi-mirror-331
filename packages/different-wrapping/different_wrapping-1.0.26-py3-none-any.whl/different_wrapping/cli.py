from pathlib import Path

import logging
import argparse
import itertools
import json
import sys

logger = logging.getLogger(__name__)

from different_wrapping.challenge import enumerate_challenges
from different_wrapping.metadata import make_metadata
from different_wrapping.yamlyaml import build_k8s_manifests, build_kustomize_manifest


def run_lint(args):
    challenges = enumerate_challenges(Path(args.folder))
    failed_validation = any(map(lambda challenge: not challenge.lint(), challenges))
    if failed_validation:
        logger.error("One or more challenges failed validation")
        sys.exit(1)


def run_converter(args):
    if args.dry:
        logger.info("Running a dry run")
    else:
        destination_directory = Path(args.destdir)
        if not destination_directory.exists():
            destination_directory.mkdir(parents=True)
        elif destination_directory.is_file():
            raise RuntimeError("%s already exists and is a file" % args.destdir)

    challenges = enumerate_challenges(Path(args.folder))
    failed_validation = any(map(lambda challenge: not challenge.lint(), challenges))
    if failed_validation:
        logger.error("One or more challenges failed validation - not proceeding")
        sys.exit(1)

    # Patch docker-compose so they convert correctly
    for challenge in challenges:
        challenge.patch()

    # Get all docker containers to be built for every challenge and reduce it to a single array
    images = list(
        itertools.chain.from_iterable(
            [challenge.get_images_to_be_built(args) for challenge in challenges]
        )
    )
    logger.debug("Got %d images to build" % len(images))
    # ..and write it to file
    buildlist = destination_directory / Path("image_buildlist.json")
    with buildlist.open("w") as f:
        json.dump([image.serialize() for image in images], f, indent=4)

    # Build k8s manifests
    static_folder = destination_directory / Path("static")
    static_folder.mkdir(parents=True, exist_ok=True)
    for challenge in challenges:
        # https://stackoverflow.com/questions/11328312/python-lambda-does-not-accept-tuple-argument
        # Ugly
        build_k8s_manifests(
            challenge, static_folder, lambda kv: "dynamic" not in kv[0], args
        )
    # Special for static: Build a kustomize file that pulls everything together
    build_kustomize_manifest(challenges, static_folder)

    dynamic_folder = destination_directory / Path("dynamic")
    dynamic_folder.mkdir(parents=True, exist_ok=True)
    for challenge in challenges:
        # https://stackoverflow.com/questions/11328312/python-lambda-does-not-accept-tuple-argument
        # Ugly
        build_k8s_manifests(
            challenge, dynamic_folder, lambda kv: "dynamic" in kv[0], args
        )

    if args.dry:
        logger.info("Skipping metadata writing due to dry run")
    else:
        make_metadata(
            challenges,
            Path(args.destdir) / Path("challenge_container_metadata.json"),
            args,
        )


def main():
    logger.info("Different wrapping starting")

    parser = argparse.ArgumentParser(
        description="different_wrapping - CTF tool for converting docker-compose files to k8s manifests that can be deployed in a CTF setting, either statically or dynamically."
    )
    subparsers = parser.add_subparsers(required=True)

    # create the parser for the "foo" command
    parser_convert = subparsers.add_parser("convert")
    parser_convert.add_argument("folder", type=str)
    parser_convert.add_argument("destdir", type=str)

    parser_convert.add_argument(
        "--ingress_type",
        choices=["ingress", "gateway"],
        default="ingress",
        help="Controls what k8s primitive is used to configure http ingress",
    )
    parser_convert.add_argument(
        "--tcp_gateway_openstack_lb_id",
        help="If there are any TCP services(exposed using no.cyberlandslaget.tcp), specify the openstack LB id to be used"
    )
    parser_convert.add_argument(
        "--gateway_parent_name",
        help="If ingress-type gateway is used, controls the name of the parent ref",
    )
    parser_convert.add_argument(
        "--gateway_parent_namespace",
        help="If ingress-type gateway is used, controls the namespace of the parent ref",
    )

    parser_convert.add_argument(
        "--dry",
        action="store_true",
        help="Does not write anything to the destination directory. Note that it will write to a temporary directory, in order to test out running kustomize",
    )
    parser_convert.add_argument(
        "--dns_host",
        type=str,
        default="chal.cyberlandslaget.no",
        help="The DNS host to be used for challenge ingresses",
    )
    parser_convert.add_argument(
        "--docker_tag",
        type=str,
        default="latest",
        help="The tag to use for docker images",
    )
    parser_convert.add_argument(
        "--docker_image_repo",
        type=str,
        default="docker.cyberlandslaget.no",
        help="The docker registry the images will reside in",
    )
    parser_convert.set_defaults(func=run_converter)

    parser_lint = subparsers.add_parser(
        "lint",
        description="Runs validation checks on a challenge folder so you can detect errors before build time. The tests being ran are the same ones as during built, but kubernetes manifests are never made.",
    )
    parser_lint.add_argument("folder", type=str)
    parser_lint.add_argument(
        "--dry",
        action="store_true",
        help="Does not write anything to the destination directory. Note that it will write to a temporary directory, in order to test out running kustomize",
    )
    parser_lint.set_defaults(func=run_lint)

    args = parser.parse_args()
    args.func(args)
