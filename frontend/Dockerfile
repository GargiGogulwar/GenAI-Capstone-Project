FROM node:24-alpine@sha256:ebfe2f90462722a7a4de65e91990e97fe0d401c70e0e762c5b53302f905ec1c1 AS builder

WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

FROM node:24-alpine@sha256:ebfe2f90462722a7a4de65e91990e97fe0d401c70e0e762c5b53302f905ec1c1
WORKDIR /app
RUN addgroup -g 1001 appgroup && \
    adduser -u 1001 -G appgroup -h /home/appuser -D appuser
COPY --chown=1001:1001 --from=builder /app/.next /app/.next
COPY --from=builder /app/public /app/public
COPY --from=builder /app/package*.json /app/
COPY --from=builder /app/next.config.ts /app/next.config.ts
RUN npm ci --omit=dev
# Next loads next.config.ts at startup; keep its compiler available without
# installing dependencies dynamically as the unprivileged runtime user.
COPY --from=builder /app/node_modules/typescript /app/node_modules/typescript

# Alpine ships busybox rather than shadow-utils, so groupadd/useradd,
# --create-home and /bin/bash do not exist on this base image. addgroup and
# adduser are the Alpine equivalents; busybox provides no bash.
USER appuser

EXPOSE 3000
CMD ["npm", "start"]
