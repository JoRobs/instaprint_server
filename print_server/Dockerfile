# syntax=docker/dockerfile:1
# https://hub.docker.com/r/docker/dockerfile

ARG BASE_IMAGE=ubuntu
ARG BASE_TAG=24.04
ARG BASE_DIGEST=sha256:c4a8d5503dfb2a3eb8ab5f807da5bc69a85730fb49b5cfca2330194ebcc41c7b

ARG PYTHON_VERSION=3.14
ARG UV_VERSION=0.11.32
ARG UV_IMAGE=ghcr.io/astral-sh/uv
ARG UV_TAG=${UV_VERSION}-alpine3.23
ARG UV_DIGEST=sha256:73dce5b8dd3b66c536e8b34a60ad76be1eadcab003b7d166deea7b7bffb009a7

# Install python dependencies
FROM $UV_IMAGE:$UV_TAG@$UV_DIGEST AS uv
ARG PYTHON_VERSION

FROM $BASE_IMAGE:$BASE_TAG@$BASE_DIGEST AS build
ARG PYTHON_VERSION

RUN apt update -q --yes
RUN apt upgrade -q --yes
RUN apt install -q --yes --no-install-recommends \
    git \
    openssh-client
RUN apt clean -q

# Add GitHub host key to known_hosts to avoid interactive prompts.
RUN mkdir -p -m 0600 ~/.ssh && ssh-keyscan -H github.com >> ~/.ssh/known_hosts

COPY --from=uv /usr/local/bin/uv /bin/

COPY uv.lock .
COPY pyproject.toml .

RUN uv python install ${PYTHON_VERSION}

# Use SSH mount to privated shared dependencies during build.
RUN --mount=type=ssh uv sync --frozen --no-cache --python ${PYTHON_VERSION}

FROM $BASE_IMAGE:$BASE_TAG@$BASE_DIGEST AS final

ARG PYTHON_VERSION

RUN apt update --yes
RUN apt upgrade --yes
RUN apt install -q --yes libdbus-1-dev

COPY --from=uv /usr/local/bin/uv /bin/
COPY --from=build /root/.local/share/uv/python /root/.local/share/uv/python
COPY --from=build /root/.local/bin/ /bin/

ENV PATH="/bin/:$PATH"
ENV TZ="Australia/Melbourne"

COPY --from=build /.venv .venv

COPY . .

ENTRYPOINT ["uv", "run", "fastapi", "run", "/src/main.py", "--port", "80", "--host", "0.0.0.0"]
