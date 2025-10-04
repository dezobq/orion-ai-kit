# SPDX-License-Identifier: Apache-2.0
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates git procps python3 python3-pip python3-venv \
 && rm -rf /var/lib/apt/lists/*
ENV NODE_VERSION=20
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
 && apt-get update && apt-get install -y nodejs && rm -rf /var/lib/apt/lists/*
RUN python3 -m pip install --break-system-packages --no-cache-dir requests tqdm
WORKDIR /workspace
ENTRYPOINT ["/bin/bash"]
