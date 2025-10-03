# SPDX-License-Identifier: Apache-2.0
FROM node:20-bookworm-slim
ENV DEBIAN_FRONTEND=noninteractive
RUN apt-get update && apt-get install -y --no-install-recommends \
    python3 python3-pip python3-venv git jq patch ca-certificates \
 && rm -rf /var/lib/apt/lists/*
WORKDIR /workspace
ENTRYPOINT ["/bin/bash"]
