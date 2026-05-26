#!/bin/bash

# Docker

# Add Docker's official GPG key:
sudo apt update
sudo apt install ca-certificates curl
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc

# Add the repository to Apt sources:
sudo tee /etc/apt/sources.list.d/docker.sources <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF

sudo apt update

 sudo apt install \
 docker-ce \
 docker-ce-cli \
 containerd.io \
 docker-buildx-plugin \
 docker-compose-plugin

# Others

apt install build-essential
apt install libdbus-1-dev pkg-config
apt install rustup
rustup default stable

git clone https://github.com/wu-hongjun/InstantLink.git
cd InstantLink
cargo build --workspace --release
# Install the CLI
cargo install --path crates/instantlink-cli
