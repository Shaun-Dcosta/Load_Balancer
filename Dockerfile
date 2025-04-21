# File: url-shortener/Dockerfile

FROM python:3.9
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir --trusted-host pypi.python.org -r requirements.txt
COPY app.py .
EXPOSE 5000
CMD ["python", "app.py"]