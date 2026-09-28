FROM python:3.12-slim-bookworm

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

WORKDIR /app

# 1. Install native Tesseract OCR and English traineddata from official Debian 12 repositories
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       tesseract-ocr \
       tesseract-ocr-eng \
    && tesseract --version \
    && rm -rf /var/lib/apt/lists/*

# 2. Copy dependencies and install via pip
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 3. Copy application codebase and database migration definitions
COPY app ./app
COPY alembic.ini .
COPY migrations ./migrations

# 4. Verify Tesseract presence and Python pytesseract integration during image build
RUN python -c "import pytesseract; print('Tesseract detected by pytesseract:', pytesseract.get_tesseract_version())"

# 5. Start production FastAPI application with Render PORT binding
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-10000}"]
