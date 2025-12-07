FROM ghcr.io/gem5/ubuntu-24.04_all-dependencies:latest@sha256:f5d3da14f068cd01bae26fc54830cd4e11c5349765a827b154f57df968a8e8fd

ARG UID=1234
ARG GID=1234

RUN useradd -m -u ${UID} -s /bin/bash user && \
    echo "user:user" | chpasswd && \
    usermod -aG sudo user

# Create kvm group (host group)
RUN groupadd -g ${GID} kvm || true
RUN usermod -aG kvm user   

USER user
WORKDIR /gem5