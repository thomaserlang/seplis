FROM node:16-alpine as builder
COPY . .
RUN npm ci; npm run build


FROM python:3.9-bullseye
RUN apt-get update; apt-get upgrade -y; apt-get install curl -y
ENV \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH="${PYTHONPATH}:./src" \
    UID=10000 \
    GID=10001

COPY . .

RUN pip install -r requirements.txt
RUN pip install mysqlclient==2.1.0

COPY --from=builder /src/seplis/web/static/dist /src/seplis/web/static/dist
COPY --from=mwader/static-ffmpeg:5.0 /ffmpeg /usr/local/bin/
COPY --from=mwader/static-ffmpeg:5.0 /ffprobe /usr/local/bin/

RUN addgroup --gid $GID --system seplis; adduser --uid $UID --system --gid $GID seplis
USER $UID:$GID
ENTRYPOINT ["python", "src/seplis/runner.py"]

# sudo docker build -t seplis/seplis --rm . 
# sudo docker push seplis/seplis:latest 