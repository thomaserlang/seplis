FROM --platform=$BUILDPLATFORM node:lts-alpine AS builder
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8
RUN mkdir /app
WORKDIR /app
COPY . .
RUN npm ci; npm run build

FROM nginxinc/nginx-unprivileged:alpine
ENV LANG=C.UTF-8
ENV LC_ALL=C.UTF-8

RUN rm /etc/nginx/conf.d/default.conf
COPY --from=builder /app/dist /usr/share/nginx/html
COPY --from=builder /app/nginx.conf /etc/nginx/conf.d/seplis.conf

EXPOSE 8080
CMD ["nginx", "-g", "daemon off;"]
