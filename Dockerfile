# Base image: a small, official Python 3.12 image
FROM python:3.12-slim

WORKDIR /code

# Install dependencies first (before copying app code) so Docker can cache
# this layer — rebuilds are much faster if requirements.txt hasn't changed.
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Now copy the actual application code
COPY app ./app

EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
