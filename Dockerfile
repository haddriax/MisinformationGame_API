# Set the Python version for the base image using a Docker argument.
ARG PYTHON_VERSION=3.12

FROM python:${PYTHON_VERSION}-slim as base

# Install the necessary dependencies.
RUN apt-get update && apt-get install -y \
    unixodbc \
    unixodbc-dev \
    freetds-dev \
    freetds-bin \
    tdsodbc \
    --reinstall build-essential \
    && rm -rf /var/lib/apt/lists/*

# Add the ODBC driver configuration.
RUN echo "[FreeTDS]\n\
Description = FreeTDS unixODBC Driver\n\
Driver = /usr/lib/x86_64-linux-gnu/odbc/libtdsodbc.so\n\
Setup = /usr/lib/x86_64-linux-gnu/odbc/libtdsS.so" >> /etc/odbcinst.ini

# Set the working directory in the container.
WORKDIR /app

# Copy the requirements.txt file to the container
COPY requirements.txt .

# Install Python packages using pip
RUN python -m pip install --no-cache-dir -r requirements.txt

# Copy the application source code into the Docker image.
COPY /app /app

# Create a non-privileged user as best practices for Docker.
ARG UID=10001
RUN adduser \
    --disabled-password \
    --gecos "" \
    --home "/nonexistent" \
    --shell "/sbin/nologin" \
    --no-create-home \
    --uid "${UID}" \
    appuser 

# Switch to the non-privileged user.
USER appuser

# Expose port for the application.
EXPOSE 8080

# Start the Python application.
CMD ["python", "main.py"]