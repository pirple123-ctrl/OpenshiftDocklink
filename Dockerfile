# Use Python 3.11 (estable y con compatibilidad completa con PyTorch/Docling)
FROM python:3.11-slim

# Variables de entorno para Python, HuggingFace y OpenShift
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    HOME=/tmp \
    HF_HOME=/tmp/huggingface \
    TORCH_HOME=/tmp/torch \
    STREAMLIT_SERVER_PORT=8501 \
    STREAMLIT_SERVER_ADDRESS=0.0.0.0

WORKDIR /app

# Instalar dependencias del sistema requeridas para OCR y OpenCV
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    curl \
    git \
    libgl1 \
    libglx-mesa0 \
    libglib2.0-0 \
    tesseract-ocr \
    tesseract-ocr-spa \
    && rm -rf /var/lib/apt/lists/*

# Copiar dependencias e instalarlas
COPY requirements.txt .
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt \
    && rm -rf /root/.cache/pip

# Copiar el resto del código
COPY . .

# Ajuste de permisos para OpenShift (SCC de usuario no root arbitrario)
RUN chgrp -R 0 /app && \
    chmod -R g=u /app && \
    mkdir -p /tmp/huggingface /tmp/torch && \
    chmod -R 777 /tmp

EXPOSE 8501

HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.enableCORS=false", "--server.enableXsrfProtection=false"]
