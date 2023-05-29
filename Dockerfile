FROM python:3.11-slim-bullseye AS build

# Upgrade all packages
RUN set -eu;\
    export DEBIAN_FRONTEND='noninteractive';\
    apt-get -q update; apt-get -qy upgrade;\
    rm -rf /var/cache/* /var/log/* /var/lib/apt/lists/*

# Install required Python packages
RUN set -eu;\
    pip_install="pip install --no-cache-dir --no-compile";\
    $pip_install --upgrade pip setuptools wheel;\
    $pip_install nox

# Build Python wheel
WORKDIR /tmp/build
COPY . ./
RUN set -eu;\
    nox --sessions lint;\
    nox --sessions test;\
    nox --sessions build


FROM python:3.11-slim-bullseye AS app

# OCI Image Annotations
# See https://github.com/opencontainers/image-spec/blob/main/annotations.md#pre-defined-annotation-keys
LABEL org.opencontainers.image.title="Random XML to CSV"
LABEL org.opencontainers.image.description="NGENIX test task: generate random XML files and convert them to CSV files"
LABEL org.opencontainers.image.version="0.1.0"
LABEL org.opencontainers.image.licenses="GPL-3.0-or-later"
LABEL org.opencontainers.image.authors="Vasiliy Polyakov <job@invasy.dev>"
LABEL org.opencontainers.image.vendor="Vasiliy Polyakov <job@invasy.dev>"
LABEL maintainer="Vasiliy Polyakov <job@invasy.dev>"

ARG container_user=user
ENV PYTHONDONTWRITEBYTECODE=1 PYTHONUNBUFFERED=1

# Upgrade all packages
RUN set -eu;\
    export DEBIAN_FRONTEND='noninteractive';\
    apt-get -q update; apt-get -qy upgrade;\
    rm -rf /var/cache/* /var/log/* /var/lib/apt/lists/*

# Create user and group
RUN set -eu;\
    useradd --create-home --user-group --comment="Test task user" "$container_user";\
    yes "$container_user" | passwd "$container_user";\
    mkdir -p /media/xml /media/csv;\
    chown "$container_user": /media/xml /media/csv
USER "$container_user"

# Install required Python packages
COPY --from=build --chown="$container_user:$container_user" /tmp/build/dist/*.whl /tmp/
RUN set -eu;\
    pip_install="pip install --user --no-cache-dir --no-compile";\
    $pip_install --upgrade pip setuptools;\
    $pip_install /tmp/*.whl;\
    rm -rf /tmp/*
ENV PATH="/home/$container_user/.local/bin:$PATH"

VOLUME ["/media/xml", "/media/csv"]

ENTRYPOINT ["random-xml-csv"]
CMD ["--xml-dir", "/media/xml", "--csv-dir", "/media/csv"]
