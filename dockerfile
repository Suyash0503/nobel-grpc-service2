
FROM python:3.12-slim


WORKDIR /app

# Copy dependency list and install
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy everything else
COPY . .


EXPOSE 50051


CMD ["python", "gateway.py"]
