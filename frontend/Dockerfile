# syntax=docker/dockerfile:1
#
# Production image for the React single page application.
#
# The bundle is built in the first stage and then served by nginx in the second
# stage, so the runtime image carries no Node.js toolchain (Section 9.4 - cloud
# deployment and the optional Docker bonus of the capstone brief).
#
# The API base URL is baked into the bundle at build time because Vite inlines
# `import.meta.env.*`. docker-compose passes the local backend URL; on a hosting
# platform the same argument points at the deployed Render service.

FROM node:20-alpine AS build

WORKDIR /app

COPY package.json package-lock.json ./
RUN npm ci

COPY . .

ARG VITE_API_URL=http://localhost:8000
ENV VITE_API_URL=${VITE_API_URL}

RUN npm run build

FROM nginx:1.27-alpine AS runtime

COPY nginx.conf /etc/nginx/conf.d/default.conf
COPY --from=build /app/dist /usr/share/nginx/html

EXPOSE 80

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
    CMD wget --quiet --tries=1 --spider http://127.0.0.1/ || exit 1

CMD ["nginx", "-g", "daemon off;"]
