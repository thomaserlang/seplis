FROM --platform=$BUILDPLATFORM node:lts-alpine AS builder
RUN mkdir /app
WORKDIR /app
COPY . .
RUN npm ci; npm run build

FROM nginxinc/nginx-unprivileged:alpine

RUN rm /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/seplis.conf

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
