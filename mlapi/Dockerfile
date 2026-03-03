# --- Stage 1: Build Stage ---
# To make the Docker image smaller, we use a multi-stage build process that separates the build environment from the runtime environment.
FROM python:3.12-slim AS builder

# Install uv from GitHub Container Registry and add it to /bin so the container recognizes the uv command
COPY --from=ghcr.io/astral-sh/uv:latest /uv /bin/uv

# Set working directory to the container's /app directory
WORKDIR /app

# Set environment variable to compile Python bytecode for faster startup times (optional)
ENV UV_COMPILE_BYTECODE=1

# Install build-essential in case a library needs to be compile
RUN apt-get update && apt-get install -y --no-install-recommends \
    # required for compiling some Python packages
    build-essential \ 
    # clean up apt cache to reduce image size
    && rm -rf /var/lib/apt/lists/*


# Copy requirements.txt to the container's /app directory
COPY requirements.txt .

# Create a virtual environment using uv and install dependencies. 
# UV will make the venv at /app/.venv so it can be used in the next stage
RUN uv venv /app/.venv && \ 
    # install dependencies within the virtual environment
    uv pip install --no-cache -r requirements.txt

# --- Stage 2: Runtime Stage ---
# Runtime image based on slim Python image that will run the application using the dependencies installed in the build stage
FROM python:3.12-slim

# Set working directory to the container's /app directory
WORKDIR /app

# Install runtime dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    # used for audio processing, e.g. with AssemblyAI
    ffmpeg \
    # clean up apt cache to reduce image size
    && rm -rf /var/lib/apt/lists/*

# Add a non-root user to run the application and set ownership of the /app directory (best practice for security)
RUN useradd -m appuser && chown appuser /app  
# Switch to the non-root user
USER appuser

# Copy the dependencies from the builder image to the runtime image
COPY --from=builder --chown=appuser:appuser /app/.venv /app/.venv
# Copy everything in the current directory, i.e. the backend's folder into the runtime image's current working directory (/app)
# Set ownership of the copied files to the non-root user
COPY --chown=appuser:appuser . .

# Update the PATH environment variable to include the path ofor our Python's dependencies
ENV PATH="/app/.venv/bin:$PATH"

# Forces Python to print logs to the terminal immediately
ENV PYTHONUNBUFFERED=1

# Export port 8000 for the application
EXPOSE 8000

# Execute the application using uvicorn when the container starts
# Uvicorn is the web server program that will run the FastAPI application defined in main.py
# main:app Tells Uvicorn to look for the "app" instance in the main.py file
# --host 0.0.0.0 tells the server to listen on all network addresses meaning it will be accessible from outside of the container, e.g. your browser
# --port 8000 tells the server to listen on port 8000
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
