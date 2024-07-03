FROM ubuntu:22.04
RUN apt-get -y update && apt-get -y install \
    cmake \
    gcc \
    g++ \
    python3 \
    python3-pip \
    git \
    wget \
    libomp-dev \
    zip unzip \
    parallel 

RUN useradd -ms /bin/bash oopsla

WORKDIR /home/oopsla

COPY tensor-schedules/requirements.txt .

RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

COPY . .

ENTRYPOINT ["bash"]
