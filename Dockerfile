FROM python:3.12-slim

# Install system dependencies
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        libgl1 libglib2.0-0 ffmpeg && \
    rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /usr/src/app

# Install Python dependencies
COPY requirements.txt ./
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY . .

# Create required directories in the container
RUN mkdir -p /usr/src/app/uploads /usr/src/app/output

# Expose port
EXPOSE 6014

# Run the Flask app with gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:6014", "app:app"]
