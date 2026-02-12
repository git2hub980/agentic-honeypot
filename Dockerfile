FROM python:3.10-slim

WORKDIR /app

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .

RUN pip install --upgrade pip

# Install CPU-only torch FIRST
RUN pip install torch --index-url https://download.pytorch.org/whl/cpu

# Then install other requirements
RUN pip install --no-cache-dir -r requirements.txt

RUN apt-get purge -y build-essential && apt-get autoremove -y

COPY . .

EXPOSE 8080

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8080"]
