FROM nvidia/cuda:11.8.0-devel-ubuntu22.04

LABEL maintainer="caleb.li.wheeler@gmail.com"

ENV DEBIAN_FRONTEND=noninteractive
ENV CONDA_DIR=/opt/conda
ENV PATH=$CONDA_DIR/bin:$PATH

# System dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    wget curl git ca-certificates \
    cmake ninja-build build-essential \
    libboost-program-options-dev libboost-graph-dev libboost-system-dev \
    libeigen3-dev libflann-dev libfreeimage-dev \
    libmetis-dev libgoogle-glog-dev \
    libgtest-dev libgmock-dev libsqlite3-dev \
    libglew-dev qtbase5-dev libqt5opengl5-dev \
    libcgal-dev libceres-dev unzip && \
    rm -rf /var/lib/apt/lists/*

# Install Miniconda
RUN wget --quiet https://repo.anaconda.com/miniconda/Miniconda3-latest-Linux-x86_64.sh -O ~/miniconda.sh && \
    bash ~/miniconda.sh -b -p $CONDA_DIR && \
    rm ~/miniconda.sh && \
    conda clean -afy

SHELL ["/bin/bash", "-c"]
RUN echo ". $CONDA_DIR/etc/profile.d/conda.sh" >> ~/.bashrc

# Create and activate conda env
RUN conda create -y -n matrix3d python=3.10
ENV CONDA_DEFAULT_ENV=matrix3d
ENV PATH=$CONDA_DIR/envs/matrix3d/bin:$PATH

# Clone Matrix3D repo
WORKDIR /workspace
RUN git clone --branch main --single-branch https://github.com/apple/ml-matrix3d.git
WORKDIR /workspace/ml-matrix3d

# Install CUDA + Torch dependencies
RUN pip install torch==2.4.0 torchvision==0.19.0 xformers==0.0.27.post2 --index-url https://download.pytorch.org/whl/cu118 && \
    pip install --extra-index-url https://miropsota.github.io/torch_packages_builder pytorch3d==0.7.7+pt2.4.0cu118 && \
    pip install -r requirements.txt && \
    pip install timm==1.0.11 boto3

# Copy entrypoint (no checkpoints)
COPY process_job.py /workspace/ml-matrix3d/

CMD ["python", "process_job.py"]
