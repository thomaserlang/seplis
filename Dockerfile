FROM node:16-alpine as jsbuilder
COPY . .
RUN npm install -g npm; npm ci; npm run build


FROM python:3.9-bullseye as pybuilder
COPY . .
RUN pip wheel -r requirements.txt --wheel-dir=/wheels
RUN pip wheel mysqlclient==2.1.0 --wheel-dir=/wheels


FROM python:3.9-slim-bullseye
RUN apt-get update; apt-get upgrade -y; apt-get install curl fontconfig -y
ENV \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PYTHONPATH="${PYTHONPATH}:./src" \
    UID=10000 \
    GID=10001

COPY . .

COPY --from=pybuilder /wheels /wheels
RUN pip install --no-index --find-links=/wheels -r requirements.txt

COPY --from=jsbuilder /src/seplis/web/static/dist /src/seplis/web/static/dist
COPY --from=mwader/static-ffmpeg:5.0 /ffmpeg /usr/local/bin/
COPY --from=mwader/static-ffmpeg:5.0 /ffprobe /usr/local/bin/

RUN addgroup --gid $GID --system seplis; adduser --uid $UID --system --gid $GID seplis
USER $UID:$GID
ENTRYPOINT ["python", "src/seplis/runner.py"]

# docker build -t seplis/seplis --rm . 
# docker push seplis/seplis:latest 