# Base image with Python
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Set environment variables
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PYTHONPATH=/app

# Copy project files
COPY ./app /app/app/
COPY ./requirements.txt /app/

# Install dependencies
RUN pip install --upgrade pip && \
    pip install -r requirements.txt

# Expose required ports
EXPOSE 8000 50051

# Install supervisord for running multiple processes
ARG DEBIAN_MIRROR=http://deb.debian.org/debian
RUN sed -i "s|http://deb.debian.org/debian|$DEBIAN_MIRROR|" /etc/apt/sources.list && \
    apt-get update && \
    apt-get install -y supervisor vim && \
    rm -rf /var/lib/apt/lists/*


# Copy Supervisor configuration
COPY supervisord.conf /etc/supervisor/conf.d/supervisord.conf

# Create log directories for supervisor
RUN mkdir -p /var/log/supervisor

# Set permissions for logs (important for container runtime)
RUN chmod -R 0777 /var/log/supervisor

# Command to run supervisor in the foreground
CMD ["/usr/bin/supervisord", "-n", "-c", "/etc/supervisor/conf.d/supervisord.conf"]


