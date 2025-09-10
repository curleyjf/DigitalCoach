# ML API

Machine Learning API for video analysis, providing audio sentiment analysis, facial emotion detection, and more.

## Features

- Audio sentiment analysis using AssemblyAI
- Facial emotion detection using DeepFace
- STAR feedback evaluation
- Big Five personality traits analysis
- Task queuing with Redis RQ
- Multiple worker queues for parallel processing

## Getting Started with Docker

The easiest way to run the application is using Docker Compose. Note that the final image size is approximately 4.5GB due to ML dependencies.

### Prerequisites

- Docker and Docker Compose installed on your system
- At least 5GB of free disk space

### Running with Docker

1. Clone the repository
2. Navigate to the project directory
3. Build and start the services:

```bash
docker-compose build  # This may take 5-10 minutes
docker-compose up -d
```

This will start:
- The main API server on port 8000
- Redis database for job queuing
- Multiple workers for processing different priority tasks
- A monitoring service for job status

## Local Development Setup

For local development without Docker:

1. Install Python 3.12 or higher
2. Install UV (faster pip alternative):
   ```bash
   curl -LsSf https://astral.sh/uv/install.sh | sh
   ```

3. Clone and setup the project:
   ```bash
   git clone <repository-url>
   cd mlapi
   uv venv
   source .venv/bin/activate  # On Windows: .venv\Scripts\activate
   uv sync
   ```

4. Install and start Redis:
   ```bash
   # On Ubuntu/Debian
   sudo apt-get install redis-server
   sudo systemctl start redis
   
   # On macOS
   brew install redis
   brew services start redis
   
   # On Windows, download from https://redis.io/download
   ```

5. Start the services (in separate terminals):
   ```bash
   # Terminal 1: API server
   python main.py
   
   
   # Terminal 2: Worker
   python -m redisStore.worker 
   or 
   rq worker high default low
   ```

## Usage

1. Access the API documentation at http://localhost:8000/docs
2. Test the API:
   - Navigate to the `/api/create_answer` endpoint
   - Execute the POST request with an empty body (it will use a default test video)
   - For custom videos, provide a `video_url` in the request body
   - Some YouTube videos are supported (must be publicly accessible)
   - For the Frontend use the signed URL from the Firebase. 

## Linting
- `mypy .`

## Formatting
- `ruff format .`


## Known Issues and Future Improvements

- AssemblyAI API key is currently hardcoded (will be moved to environment variables)
- Queue priority system needs optimization
- Better error handling for video processing failures

## Environment Variables

Configure the application using environment variables:

- `REDIS_HOST`: Redis host (default: "localhost")
- `REDIS_PORT`: Redis port (default: 6379)
- `REDIS_PASSWORD`: Redis password (optional)
- `REDIS_URL`: Complete Redis URL (optional, overrides other Redis settings)
- `WORKERS_COUNT`: Number of worker processes (used in Docker setup)

## Testing

Run tests using pytest:

```bash
pytest
```
