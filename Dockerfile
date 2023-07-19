ARG PYTHON=python3
ARG PYTHON_VERSION=3.8.13

# PyTorch Binaries
ARG PT_TORCHVISION_URL=https://download.pytorch.org/whl/cpu/torchvision-0.13.1%2Bcpu-cp38-cp38-linux_x86_64.whl
ARG PT_TORCHAUDIO_URL=https://download.pytorch.org/whl/cpu/torchaudio-0.12.1%2Bcpu-cp38-cp38-linux_x86_64.whl
ARG PT_TORCHDATA_URL=https://download.pytorch.org/whl/test/torchdata-0.4.1-cp38-cp38-manylinux_2_17_x86_64.manylinux2014_x86_64.whl

FROM ubuntu:20.04

RUN apt-get update \
    && apt-get upgrade -y \
    && apt-get autoremove -y \
    && apt-get clean \
    && apt-get install -y python3-pip \
    && rm -rf /var/lib/apt/lists/*

RUN pip install --upgrade pip

WORKDIR /app

COPY app /app

COPY requirements.txt /app

RUN pip install -r /app/requirements.txt

EXPOSE 8080

CMD exec uvicorn main:app --port 8080 --host 0.0.0.0