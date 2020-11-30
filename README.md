![PyPI](https://img.shields.io/pypi/v/alertmanager-gchat-integration)
![PyPI - License](https://img.shields.io/pypi/l/alertmanager-gchat-integration)
![PyPI - Downloads](https://img.shields.io/pypi/dm/alertmanager-gchat-integration)
[![docker-image-version](https://img.shields.io/docker/v/julb/alertmanager-gchat-integration.svg?sort=semver)](https://hub.docker.com/r/julb/alertmanager-gchat-integration)
[![docker-image-size](https://img.shields.io/docker/image-size/julb/alertmanager-gchat-integration.svg?sort=semver)](https://hub.docker.com/r/julb/alertmanager-gchat-integration)
[![docker-pulls](https://img.shields.io/docker/pulls/julb/alertmanager-gchat-integration.svg)](https://hub.docker.com/r/julb/alertmanager-gchat-integration)

# alertmanager-gchat-integration

## Description

The application provides a Webhook integration for Prometheus AlertManager to push alerts to Google Chat rooms.

The application expects a `config.toml` file like this:

```toml
[app.notification]
# Helpful to indicate the origin of the message. Default to HOSTNAME.
# origin = "custom-origin"

# Optional Jinja2 custom template to print message to GChat.
# custom_template_path = "<file>.json.j2"

[app.room.<room-name>]
notification_url = "https://chat.googleapis.com/v1/spaces/<space-id>/messages?key=<key>&token=<token>&threadKey=<threadId>"
```

The file may be:

- Located in the current directory and named `config.toml`.
- Placed in the directory of your choice with `CONFIG_FILE_LOCATION` environment variable set.

Also, the application provides a built-in template for GChat notification located [here](./alertmanager_gchat_integration/default-notification-template.json.j2).
If you wish to customize it, create a custom version and use `app.notification.custom_template_path`.

When the application is started, the following endpoints are available:

- `/alerts?room=<room-name>` : Endpoint used by AlertManager to send messages to GChat. The `room-name` should match the value indicated in the config.toml file. HTTP expected methods are: `POST`.
- `/healthz` : return 200 OK if the service is running. HTTP expected methods are: `GET`.
- `/metrics` : return Prometheus metrics regarding HTTP requests. HTTP expected methods are: `GET`.

## Using the python module

```
$ pip install alertmanager-gchat-integration
$ CONFIG_FILE_LOCATION=config.toml python -m alertmanager_gchat_integration
```

## Using the container

To execute the container, you should have a ~/.kube/config with the context pointing to the cluster.
The user defined in the context should have the appropriate rights in th cluster to manage configmaps.

## Starts the service

- Run container as root:

```bash
$ docker run -ti \
    --user 65534:65534                      \
    -p 80:8080                              \
    -v $(pwd)/config.toml:/app/config.toml  \
    julb/alertmanager-gchat-integration:latest
```

The following environment variables are also available:

| Environment var      | Description                             | Default Value      |
| -------------------- | --------------------------------------- | ------------------ |
| PORT                 | The listening port for the application. | `8080`             |
| CONFIG_FILE_LOCATION | The config.toml file path.              | `/app/config.toml` |

## Helm chart

A [Helm chart](https://github.com/julb/helm-charts/blob/main/julb/alertmanager-gchat-integration/README.md) is available to install this runtime.

## Contributing

This project is totally open source and contributors are welcome.

When you submit a PR, please ensure that the python code is well formatted and linted.

```
$ make install.dependencies
$ make format
$ make lint
```
