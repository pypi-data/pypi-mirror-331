# Task writer's guide

`different_wrapping` is used as it streamlines deployment and QA of challenges. We do this by forcing all containers to be defined in a `docker-compose.yml` file in the root of the CTF challenge folder. This way, the same docker-compose manifest you use for testing will be the one pushed to production.

## Writing and testing manifests

If you are not familiar with `docker-compose`, looking at other challenges in the same repository is probably the easiest way of familiarizing yourself with the system. Basically, you want something like this:

```yaml
version: '3'
services:
  # Will be exposed as a http server
  http-server:
    build:
      context: .
      dockerfile: http.Dockerfile
    ports:
    - 80:80
    labels:
      no.cyberlandslaget.http: yes
  # The port will be exposed on an IP address
  tcp-server:
    build:
      context: .
      dockerfile: tcpserver.Dockerfile
    ports:
    - 1337:1337
    labels:
      kompose.service.type: loadbalancer # This is required if you want to expose a TCP port to the internet
  # This pod is identical to the one above, but is ran on an on-demand basis.
  # That is, users have to "request" the pod to start, and it is spun up for them only.
  dynamic-tcp-server:
    build:
      context: .
      dockerfile: tcpserver.Dockerfile
    ports:
    - 1337:1337
    labels:
      kompose.service.type: loadbalancer
```

The docker-compose reference, https://docs.docker.com/compose/compose-file/compose-file-v3/, is a great place to Ctrl+F for the info you need about the format. If you are proficient in k8s and want to do custom stuff, you could also consult https://kompose.io/user-guide/ to see what options are available for yaml-to-yaml conversion

Challenge servers are deployed in Kubernetes. We use `Kompose` to convert `docker-compose` manifests to kubernetes. If you already have experience with `Kompose` you may have to re-learn some aspects, as we do not support(and in some cases completely block) unwanted kompose features. Especially consider this:
 * We do not use kompose's inbuilt ingress generation feature. This is to avoid errors. 
   * Instead, by labeling a service `no.cyberlandslaget/http` (with any value), you mark the pod as being a HTTP server, which will automatically generate a ingress resource compatible with our system.
   * You may still want to expose port 80 for testing, but our linter will disallow deploying such a service.
   * Always use port 80. We handle SSL termination.
   * If you need the IP of the requester, use `X-Forwarded-For`
 * We do not allow volume mounts. At all.
   * You are free to use volume mounts for testing, but before committing, please ensure the Docker container is 100% self-sufficient and that everything that needs to be inside the container is copied in using the `COPY` directive.

Some other things to note:

* Kustomize renames `foo_bar` to `foo-bar` so we enforce this regex when naming docker-compose services: `[a-zA-Z\-]+`.

The CI system has inbuilt validators that will validate your `docker-compose` file and spot potential issues relating to our platform, so don't worry too much.

## Exposing containers to the internet.

As shown in the previous examples, the following rules apply:

* For HTTP servers, we ingest all traffic through a HTTP load balancer that also handles SSL termination.
  * Use the label `no.cyberlandslaget.http` to automatically configure an ingress for the container. The name will be auto-generated from the service name and challenge name
* For Other TCP/UDP servers, we use [services](https://kubernetes.io/docs/concepts/services-networking/service/). `LoadBalancer` is the correct service type
  * To use it, set the `kompose.service.type` label to `loadbalancer`.
  * Static challenges will get their own load balancer IP. **It is up to someone in infrastructure to create a DNS record that points to the correct load balancer IP.**
  * Dynamic challenges will determine their own IP and inform the frontend.

For on-demand pods, the same rules apply. When the pods are created, the UI will be informed of the DNS names and IPs of ingresses and services that are created. The label `no.cyberlandslaget.frontendName` can be used to control the service name shown to users.

## Supported service labels

We use the `labels` feature of docker-compose to pass additional configuration parameters regarding docker containers to be spun up in kubernetes. This is a full list of all labels we care about:

* `no.cyberlandslaget.frontendName` - Specifies the name of the server as shown to the user in the frontend. If not set, defaults to the `docker-compose` service name.
* `no.cyberlandslaget.http` - If set, creates an [ingress](https://kubernetes.io/docs/concepts/services-networking/ingress/) resource for the purpose of exposing a HTTP server(and performing TLS termination)
* `no.cyberlandslaget.dns_challenge_name` - If set, specifies a custom dns prefix to be used together with the `--dns_host` CLI argument(which defaults to `chal.cyberlandslaget.no`).
  * Setting it to `foo-bar` would generate `foo-bar.chal.cyberlandslaget.no`
* `no.cyberlandslaget.autogenerated_password` - Specify an existing environment variable that will receive an random value every time the pod is deployed. Requires that the service is deployed by **Nina**.