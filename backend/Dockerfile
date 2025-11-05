FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt install_llama.py ./
RUN apt-get update && apt-get install -y build-essential \
    && pip install -r requirements.txt \
    && python install_llama.py

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]