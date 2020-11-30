FROM python:3.8-alpine

ENV PORT=8080

ENV CONFIG_FILE_LOCATION=/app/config.toml

RUN mkdir /app

WORKDIR /app

ADD scripts/entrypoint.sh /app

ARG PACKAGE_VERSION

RUN pip --no-cache-dir install alertmanager-gchat-integration==$PACKAGE_VERSION

CMD ["./entrypoint.sh"]
