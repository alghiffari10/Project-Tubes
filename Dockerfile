FROM ubuntu:20.04
ENV DEBIAN_FRONTEND=noninteractive

# install semua dependensi paket (library) yang dibutuhkan
RUN apt-get update && apt-get upgrade -y && apt-get install -y \
    tzdata \
    libssl-dev \
    openssl \
    zlib1g-dev \
    build-essential \
    checkinstall \
    libffi-dev \
    libsqlite3-dev \
    vim \
    curl \
    make \
    sudo \
    python3-pip \
    python3-pygame \
    libsdl1.2-dev \
    libsdl-image1.2-dev \
    libsdl-mixer1.2-dev \
    libsdl-sound1.2-dev \
    libsdl-ttf2.0-dev \
    libsdl2-dev \
    libsdl2-image-dev \
    libsdl2-mixer-dev \
    libsdl2-ttf-dev \
    libsdl2-gfx-dev \
    libsdl2-net-dev

# install x11
RUN apt install -qqy x11-apps

# install pygame
RUN pip3 install pygame 


# menambahkan parameter build argument
ARG USER=docker
ARG UID=1000
ARG GID=1000

# menambahkan default password untuk user
ARG PW=docker
RUN useradd -m ${USER} --uid=${UID} --shell /bin/bash && echo "${USER}:${PW}" | chpasswd \
    && adduser docker sudo

# Setup default user, ketika memasuki kontainer
USER ${UID}:${GID}
WORKDIR /home/${USER}