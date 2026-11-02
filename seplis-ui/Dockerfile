FROM --platform=$BUILDPLATFORM node:lts-alpine AS builder
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
RUN npm install --global corepack && corepack enable
WORKDIR /app
COPY . .
RUN pnpm install --frozen-lockfile \
    && pnpm run build

FROM nginx/nginx-unprivileged:alpine
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/seplis.conf

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
