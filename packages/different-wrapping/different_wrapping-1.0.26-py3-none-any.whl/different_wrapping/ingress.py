from different_wrapping.utils import docker_port_string_get_external_port


def generate_ingress(service_name, service, challenge, args):
    # First we need to determine the port that the ingress is supposed to be pointed towards
    if "ports" not in service.container_dict:
        raise RuntimeError(
            f"Tried to create ingress for {service_name} but it has no ports exposed(and therefore no k8s service to point to)"
        )

    external_ports = [
        docker_port_string_get_external_port(port)
        for port in service.container_dict["ports"]
    ]

    if len(external_ports) == 0:
        raise RuntimeError(
            f"Unable to create ingress for {service_name} as there are no ports"
        )
    elif len(external_ports) > 1:
        raise RuntimeError(
            f"Unable to determine external port for {service_name} as there are more than one ports exposed"
        )

    # Determine DNS name
    host = service.get_dns_name(args.dns_host)

    return {
        "apiVersion": "networking.k8s.io/v1",
        "kind": "Ingress",
        "metadata": {
            "name": f"ingress-{challenge.name()}-{service_name}",
        },
        "spec": {
            "ingressClassName": "TODO",
            "rules": [
                {
                    "host": host,
                    "http": {
                        "paths": [
                            {
                                "path": "/",
                                "pathType": "Prefix",
                                "backend": {
                                    "service": {
                                        "name": service_name,
                                        "port": {"number": int(external_ports[0])},
                                    }
                                },
                            }
                        ]
                    },
                }
            ],
        },
    }
