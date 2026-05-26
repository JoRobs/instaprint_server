# syntax=docker/dockerfile:1
# https://hub.docker.com/r/docker/dockerfile

ARG BASE_IMAGE=ubuntu
ARG BASE_TAG=24.04
ARG BASE_DIGEST=sha256:c4a8d5503dfb2a3eb8ab5f807da5bc69a85730fb49b5cfca2330194ebcc41c7b

FROM $BASE_IMAGE:$BASE_TAG@$BASE_DIGEST AS base
WORKDIR /usr/local/instaprint

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

ARG INSTANTLINK_SHA=35e3d18062ccb15be921ac247571b57bc52ea1e6

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

# Build server package
RUN <<EOF 
apt install -q --yes \
    ca-certificates \
    curl \
    python3 \
EOF

ADD https://astral.sh/uv/0.11.16/install.sh /uv-installer.sh
RUN sh /uv-installer.sh && rm /uv-installer.sh
ENV PATH="/root/.local/bin/:$PATH"
RUN uv init
RUN uv build --no-cache

FROM $BASE_IMAGE:$BASE_TAG@$BASE_DIGEST AS final
WORKDIR /usr/local/instaprint

COPY --from=base /usr/local/instaprint/InstantLink/target/release/instantlink /usr/bin/
ENV PATH="/usr/bin/:$PATH"

ENTRYPOINT ["tail", "-f", "/dev/null"]
