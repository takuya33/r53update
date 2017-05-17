# Dockerfile
FROM alpine:3.5
MAINTAINER Takuya Sawada <takuya@tuntunkun.com>

ARG AWS_ACCESS_KEY
ARG AWS_SECRET_KEY
ARG AWS_REGION

ENV AWS_ACCESS_KEY_ID ${AWS_ACCESS_KEY}
ENV AWS_SECRET_ACCESS_KEY ${AWS_SECRET_KEY}
ENV AWS_DEFAULT_REGION ${AWS_REGION}

RUN apk --update add python py-pip \
        && apk add --virtual .build-deps git gcc python-dev musl-dev linux-headers \

	&& pip install --upgrade pip \
        && pip install git+https://github.com/tuntunkun/r53update@develop \

        && apk del --purge .build-deps \
        && rm -rf /var/apk/cache/*

ENTRYPOINT ["r53update"]
