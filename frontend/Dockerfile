# syntax=docker/dockerfile:1
# Build context: the frontend/ directory.
FROM node:22-slim AS build

WORKDIR /app
RUN corepack enable && corepack prepare pnpm@10 --activate

COPY package.json pnpm-lock.yaml ./
RUN pnpm install --frozen-lockfile

COPY . ./
RUN pnpm build

FROM nginx:1.27-alpine AS runtime

# Defaults suit the local compose stack; override BACKEND_ORIGIN (and PORT, which
# Render injects) in the cloud. The base image runs envsubst over this template
# at container start and writes /etc/nginx/conf.d/default.conf.
ENV PORT=80 \
    BACKEND_ORIGIN=http://backend:8000

COPY nginx.conf.template /etc/nginx/templates/default.conf.template
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80
