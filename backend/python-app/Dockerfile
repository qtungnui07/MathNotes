FROM python:3.7-slim

# Install system dependencies all in one RUN command to reduce layers
RUN apt-get update && apt-get install -y \
    wget \
    ca-certificates \
    git \
    build-essential \
    curl \
    pandoc \
    libgl1 \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    libgstreamer1.0-0 \
    gstreamer1.0-tools \
    gstreamer1.0-plugins-base \
    gstreamer1.0-plugins-good \
    && rm -rf /var/lib/apt/lists/*

# Install Miniconda and initialize
RUN wget https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O /miniconda.sh && \
    bash /miniconda.sh -b -p /opt/conda && \
    rm /miniconda.sh

# Add conda to path
ENV PATH=/opt/conda/bin:$PATH

# Create conda environment with specific packages
# Combining commands to reduce layers and avoid activation issues
RUN conda create -y -n CoMER python=3.7 && \
    conda install -n CoMER -y pytorch==1.8.1 torchvision==0.9.1 cpuonly -c pytorch && \
    conda install -n CoMER -y pytorch-lightning=1.4.9 torchmetrics=0.6.0 -c conda-forge && \
    conda clean -afy

# Set up conda activation on container startup
SHELL ["/bin/bash", "-c"]
RUN echo "conda activate CoMER" >> ~/.bashrc

# Make RUN commands use the conda environment
ENV PATH /opt/conda/envs/CoMER/bin:$PATH

# Install additional Python dependencies via pip
RUN pip install \
    einops==0.3.0 \
    editdistance==0.5.3 \
    deepsparse[yolov8] \
    jsonargparse[signatures]==3.17.0 \
    flake8==3.9.0 \
    black==22.3.0 \
    isort==5.8.0 \
    jupyter==1.0.0 \
    opencv-python==4.5.4.60 \
    matplotlib==3.5.1 \
    typer==0.4.1 \
    beautifulsoup4==4.10.0 \
    fastapi \
    uvicorn \
    lxml>=4.9.1 

WORKDIR /app
COPY . /app

# Set default command to use bash
CMD ["uvicorn", "server:app", "--host", "0.0.0.0", "--port", "8000"]