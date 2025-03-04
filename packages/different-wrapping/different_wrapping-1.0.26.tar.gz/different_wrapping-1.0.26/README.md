# Different wrapping

Basically a glorified YAML converter aimed at [CTFs](https://en.wikipedia.org/wiki/Capture_the_flag_(cybersecurity)). The goal is that tasks can be written using `docker-compose`, such that they can be easily quality tested. The `docker-compose` files are then converted to k8s manifests using [kompose](https://kompose.io/), organized neatly in folders by challenge type and challenge name.

Metadata files are also generated:

* `image_buildlist.json` is a list of what containers need to be built
* `challenge_container_metadata.json` explains what challenges have what kind of containers, so the frontend can show this to the user. It also contains information on what challenges have dynamic containers.

The intention of this tool is to run it in CI to generate metadata files to inform the rest of the platform. You can also run it locally, even just as a challenge linter. Run `different_wrapping --help` for more info.

`Different wrapping` is a component in an approach we are taking where instead of writing an elaborate system for deploying dynamic challenges, we try to re-use as much infrastructure between static and dynamic challenges as possible. We do this by creating "argocd-ready" kustomize projects - with the static project being actually hosted by argo and the dynamic ones being managed by a custom daemon.

## Design goals

* Use standard k8s manifests where practical
* KISS

## Requirements

* Python
* The requirements in pyproject.toml (`pip install -e .` to install the system and all dependencies so you can run it using `python -m`)
* Kompose, if you are building yaml
  - Note that running `different_wrapping lint <directory>` is possible without installing kompose

## Configuration

### CLI

See `different_wrapping --help`. Here is a possible out of date output:

```
$ different_wrapping convert --help
INFO:different_wrapping.cli:Different wrapping starting
usage: different_wrapping convert [-h] [--dry] [--dns_host DNS_HOST] folder destdir

positional arguments:
  folder
  destdir

options:
  -h, --help           show this help message and exit
  --dry                Does not write anything to the destination directory. Note that it will write to a
                       temporary directory, in order to test out running kustomize
  --dns_host DNS_HOST
  --docker_image_repo DOCKER_IMAGE_REPO
```