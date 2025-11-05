FROM nvidia/cuda:13.0.0-devel-ubuntu22.04

# Install Python
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-dev \
    build-essential \
    cmake \
    ninja-build \
    && ln -s /usr/bin/python3 /usr/bin/python

WORKDIR /app

COPY requirements.txt install_llama.py ./
RUN pip install -r requirements.txt && python install_llama.py

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]