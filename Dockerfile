FROM python:3.12-slim

WORKDIR /app

# System dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    git \
    wget \
    ca-certificates \
    libgl1 \
    libglib2.0-0 \
    fonts-dejavu-core \
    && rm -rf /var/lib/apt/lists/*

# Install LAMMPS
RUN git clone --depth 1 https://github.com/lammps/lammps.git /tmp/lammps && \
    cmake -S /tmp/lammps/cmake -B /tmp/lammps/build \
    -D BUILD_MPI=OFF \
    -D BUILD_OMP=ON \
    -D PKG_MANYBODY=ON \
    -D PKG_MOLECULE=ON \
    -D PKG_KSPACE=ON \
    -D PKG_EXTRA-FIX=ON \
    -D CMAKE_BUILD_TYPE=Release && \
    cmake --build /tmp/lammps/build --parallel 2 && \
    cp /tmp/lammps/build/lmp /usr/local/bin/lmp && \
    rm -rf /tmp/lammps

# Python dependencies
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Project
COPY . .

EXPOSE 10000

CMD ["sh", "-c", "uvicorn API.main:app --host 0.0.0.0 --port ${PORT:-10000}"]