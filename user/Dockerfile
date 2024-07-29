FROM python:3.10

WORKDIR /app

# Install poppler-utils
# RUN apt-get update && apt-get install -y poppler-utils

COPY requirements.txt /app/

RUN pip install --no-cache-dir -r requirements.txt

COPY ./app  /app

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]