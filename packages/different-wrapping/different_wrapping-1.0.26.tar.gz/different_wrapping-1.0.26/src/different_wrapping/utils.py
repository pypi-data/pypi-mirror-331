def docker_port_string_get_external_port(port):
    # Extracts external ports from a docker port string
    # See https://docs.docker.com/compose/compose-file/compose-file-v3/#ports
    if isinstance(port, int):
        return port
    components = port.split(":")
    if len(components) == 1:
        return components[0]
    elif len(components) == 2:
        return components[0]
    elif len(components) == 3:
        return components[1]
    else:
        raise RuntimeError("Unable to parse external port")
