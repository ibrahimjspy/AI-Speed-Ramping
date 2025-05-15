FROM python:3.12-slim

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 ffmpeg && \
    rm -rf /var/lib/apt/lists/*

WORKDIR /usr/src/app

COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

EXPOSE 6014

CMD ["gunicorn", "-b", "0.0.0.0:6014", "app:app"]
