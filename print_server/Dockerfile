# syntax=docker/dockerfile:1
# https://hub.docker.com/r/docker/dockerfile

ARG BASE_IMAGE=ubuntu
ARG BASE_TAG=24.04
ARG BASE_DIGEST=sha256:c4a8d5503dfb2a3eb8ab5f807da5bc69a85730fb49b5cfca2330194ebcc41c7b
ARG UV_IMAGE=ghcr.io/astral-sh/uv
ARG UV_TAG=alpine3.23
ARG UV_DIGEST=sha256:73dce5b8dd3b66c536e8b34a60ad76be1eadcab003b7d166deea7b7bffb009a7

FROM $BASE_IMAGE:$BASE_TAG@$BASE_DIGEST AS build

ARG INSTANTLINK_SHA=35e3d18062ccb15be921ac247571b57bc52ea1e6

SHELL ["/bin/bash", "-exo", "pipefail", "-c"]

ENV TZ="Australia/Melbourne"

# Install instantprint build dependencies
RUN apt update --yes
RUN apt upgrade --yes
RUN <<EOF
apt install -q --yes \
    curl \
    git-all \
    build-essential \
    libdbus-1-dev \
    pkg-config \
    rustup
EOF

RUN rustup default stable

RUN <<EOF
mkdir InstantLink
cd InstantLink
git init
git remote add origin https://github.com/wu-hongjun/InstantLink.git
git fetch --depth 1 origin $INSTANTLINK_SHA
git checkout FETCH_HEAD
EOF

RUN <<EOF
cd InstantLink
cargo build --workspace --release
cargo install --path crates/instantlink-cli
EOF

# Install python dependencies
FROM $UV_IMAGE:$UV_TAG@$UV_DIGEST AS uv

ARG PYTHON_VERSION=3.14
COPY uv.lock .
COPY pyproject.toml .
RUN uv sync --frozen --no-cache --python $PYTHON_VERSION

FROM $BASE_IMAGE:$BASE_TAG@$BASE_DIGEST AS final

RUN apt update --yes
RUN apt upgrade --yes
RUN apt install -q --yes libdbus-1-dev

COPY --from=build /InstantLink/target/release/instantlink /bin/
COPY --from=uv /usr/local/bin/uv /bin/
ENV PATH="/bin/:$PATH"

COPY --from=uv /root/.local/share/uv/python /root/.local/share/uv/python
COPY --from=uv /.venv .venv

COPY . .

ENTRYPOINT ["/.venv/bin/fastapi", "run", "/src/main.py", "--port", "80", "--host", "0.0.0.0"]
