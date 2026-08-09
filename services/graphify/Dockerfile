# Graphify — Knowledge Graph serve layer (Phase 14.4)
#
# Builds the graphify MCP HTTP server from the pinned upstream source so the
# Streamable HTTP transport (and --json-response) is included. The graph.json is
# mounted at runtime — never baked into the image.
#
# Build:  docker build -t graphify .
# Run:    docker run -p 8080:8080 -v /mnt/monarch/appdata/kora:/data graphify \
#             /data/graph.json --transport http --host 0.0.0.0 --api-key "$SECRET"
FROM python:3.12-slim

# Pin the upstream revision (graphify 0.9.37 / v8) for reproducible builds.
ARG GRAPHIFY_REF=09a34ad

RUN apt-get update \
    && apt-get install -y --no-install-recommends git \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /src
RUN git clone --depth 1 https://github.com/Graphify-Labs/graphify.git . \
    && git checkout ${GRAPHIFY_REF}

RUN pip install --no-cache-dir ".[mcp]"

RUN useradd --create-home --uid 10001 graphify
USER graphify

EXPOSE 8080

ENTRYPOINT ["python", "-m", "graphify.serve"]
CMD ["/data/graph.json", "--transport", "http", "--host", "0.0.0.0", "--port", "8080", "--json-response"]
