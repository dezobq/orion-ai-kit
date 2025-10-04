# SPDX-License-Identifier: Apache-2.0
FROM debian:bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl ca-certificates git procps \
 && rm -rf /var/lib/apt/lists/*
ENV NODE_VERSION=20
RUN curl -fsSL https://deb.nodesource.com/setup_20.x | bash - \
 && apt-get update && apt-get install -y nodejs && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
ENTRYPOINT ["/bin/bash"]
