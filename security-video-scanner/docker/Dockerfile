# vscan - on-premise appliance image.
# Build from the project root:  docker build -f docker/Dockerfile -t vscan:0.1.0 .
FROM python:3.11-slim

# ffmpeg does every decode, cut and transcode; tini reaps the ffmpeg children.
RUN apt-get update \
 && apt-get install -y --no-install-recommends ffmpeg tini \
 && rm -rf /var/lib/apt/lists/*

ENV PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    VSCAN_MODEL_DIR=/opt/vscan-models \
    VSCAN_DATA_DIR=/data \
    VSCAN_FOOTAGE_DIRS=/footage \
    VSCAN_PORT=8080 \
    VSCAN_IN_CONTAINER=1

WORKDIR /app
COPY pyproject.toml README.md ./
COPY vscan ./vscan
COPY vscan_server ./vscan_server
RUN pip install ".[server,ask]"

# Bake the detection models into the image so the appliance needs no internet
# at runtime - many sites run these machines on an isolated camera VLAN.
RUN mkdir -p "$VSCAN_MODEL_DIR" && python -m vscan.cli models fetch

RUN useradd --system --uid 10001 --create-home vscan \
 && mkdir -p /data /footage && chown -R vscan:vscan /data /opt/vscan-models
USER vscan

EXPOSE 8080
VOLUME ["/data"]
HEALTHCHECK --interval=30s --timeout=5s --start-period=20s --retries=3 \
  CMD python -c "import urllib.request,sys; sys.exit(0 if urllib.request.urlopen('http://127.0.0.1:8080/api/health', timeout=4).status==200 else 1)"

ENTRYPOINT ["/usr/bin/tini", "--"]
CMD ["vscan-server"]
