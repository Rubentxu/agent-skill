# Build explicitly with user approval: podman build -f assets/markmap.Containerfile -t cognicode-markmap:0.18.12 assets
# npm dependency download happens at image BUILD time; NO project source is copied.
FROM node:22-alpine
RUN npm install --global --ignore-scripts markmap-cli@0.18.12
WORKDIR /data/navigation
ENTRYPOINT ["markmap"]
