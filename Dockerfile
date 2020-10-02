FROM ubuntu:18.04

# Root-folder and system variables
RUN apt-get clean && apt-get update &&  \
    apt-get install --no-install-recommends -y locales && locale-gen en_US.UTF-8 && \
    rm -rf /var/lib/apt/lists/*

# Environment variables
ENV LANG=en_US.UTF-8

ENV PKG_CONFIG_PATH=${PKG_CONFIG_PATH}:/usr/local/lib/pkgconfig/

COPY requirements.txt /server-requirements.txt
RUN apt-get update && \
    apt-get install --no-install-recommends -y python3.7 curl ca-certificates python3-distutils && \
    curl https://bootstrap.pypa.io/get-pip.py -o get-pip.py && \
    python3.7 get-pip.py && \
    rm get-pip.py && \
    update-alternatives --install /usr/bin/python python /usr/bin/python3.7 1 && \
    DEBIAN_FRONTEND=noninteractive apt-get install --no-install-recommends -y nginx make && \
    pip install --no-cache-dir -r server-requirements.txt && \
    rm server-requirements.txt && \
    apt-get purge -y curl ca-certificates && \
    apt-get autoremove -y && \
    rm /etc/nginx/sites-enabled/default && \
    rm -rf /var/lib/apt/lists/*

# Nginx
COPY nginx.conf  /etc/nginx/sites-enabled/pyronear.conf
COPY src /src
COPY docker-entrypoint.sh /
RUN chmod -R 777 /docker-entrypoint.sh

# Tag
ARG DOCKER_TAG
ENV DOCKER_TAG ${DOCKER_TAG}

EXPOSE 80 8000
CMD ["/bin/bash", "-c",  "/docker-entrypoint.sh"]
