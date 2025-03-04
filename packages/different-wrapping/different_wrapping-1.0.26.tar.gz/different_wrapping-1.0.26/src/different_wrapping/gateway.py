from different_wrapping.utils import docker_port_string_get_external_port


def generate_gateway(service_name, service, challenge, args):
    # First we need to determine the port that the ingress is supposed to be pointed towards
    if "ports" not in service.container_dict:
        raise RuntimeError(
            f"Tried to create gateway for {service_name} but it has no ports exposed(and therefore no k8s service to point to)"
        )

    external_ports = service.ports()

    if len(external_ports) == 0:
        raise RuntimeError(
            f"Unable to create gateway for {service_name} as there are no ports"
        )
    elif len(external_ports) > 1:
        raise RuntimeError(
            f"Unable to determine external port for {service_name} as there are more than one ports exposed"
        )

    # Determine DNS name
    host = service.get_dns_name(args.dns_host)

    return {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "HTTPRoute",
        "metadata": {
            "name": f"gateway-{challenge.safe_name()}-{service_name}",
        },
        "spec": {
            "parentRefs": [
                {
                    "name": args.gateway_parent_name,
                    "namespace": args.gateway_parent_namespace,
                    "sectionName": "https",
                    "kind": "Gateway",
                    "group": "gateway.networking.k8s.io",
                }
            ],
            "hostnames": [host],
            "rules": [
                {
                    "matches": [{"path": {"type": "PathPrefix", "value": "/"}}],
                    "backendRefs": [
                        {
                            "name": service_name,
                            "port": int(external_ports[0]),
                            "weight": 1,
                            "group": "",
                            "kind": "Service",
                        }
                    ],
                }
            ],
        },
    }


def generate_tcp_gateway(service_name, service, challenge, args):
    # First we need to determine the port that the ingress is supposed to be pointed towards
    if "ports" not in service.container_dict:
        raise RuntimeError(
            f"Tried to create TCP gateway for {service_name} but it has no ports exposed(and therefore no k8s service to point to)"
        )

    external_ports = service.ports()

    if len(external_ports) == 0:
        raise RuntimeError(
            f"Unable to create TCP gateway for {service_name} as there are no ports"
        )
    elif len(external_ports) > 1:
        raise RuntimeError(
            f"Unable to determine external port for {service_name} as there are more than one ports exposed"
        )

    # Determine DNS name
    host = service.get_dns_name(args.dns_host)

    if args.tcp_gateway_openstack_lb_id is None:
        raise RuntimeError("Unable to create TCP gateway - no LB id is set")

    gateway = {
        "apiVersion": "gateway.networking.k8s.io/v1",
        "kind": "Gateway",
        "metadata": {"name": "challenge-tcp-gateway"},
        "spec": {
            "gatewayClassName": "envoy-tcp-chall",
            "infrastructure": {
                "annotations": {
                    "external-dns.alpha.kubernetes.io/hostname": host,
                    "external-dns.alpha.kubernetes.io/ttl": "60",
                    "loadbalancer.openstack.org/enable-health-monitor": "true",
                    "loadbalancer.openstack.org/proxy-protocol": "false",
                    "loadbalancer.openstack.org/load-balancer-id": args.tcp_gateway_openstack_lb_id
                }
            },
            "listeners": [
                {
                    "protocol": "TCP",
                    "port": int(external_ports[0]),
                    "name": "challenge",
                    "allowedRoutes": {
                        "namespaces": {"from": "Same"},
                        "kinds": [
                            {"kind": "TCPRoute", "group": "gateway.networking.k8s.io"}
                        ],
                    },
                }
            ],
        },
    }

    tcproute = {
        "apiVersion": "gateway.networking.k8s.io/v1alpha2",
        "kind": "TCPRoute",
        "metadata": {
            "name": f"gateway-{challenge.safe_name()}-{service_name}",
        },
        "spec": {
            "parentRefs": [
                {
                    "name": "challenge-tcp-gateway",
                    "sectionName": "challenge",
                    "group": "gateway.networking.k8s.io",
                    "kind": "Gateway",
                }
            ],
            "rules": [
                {
                    "backendRefs": [
                        {
                            "name": service_name,
                            "port": int(external_ports[0]),
                            "weight": 1,
                            "group": "",
                            "kind": "Service",
                        }
                    ]
                }
            ],
        },
    }

    return [gateway, tcproute]
