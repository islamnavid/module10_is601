# IS601 Module 10 — Secure User Model

## Project Overview

This project is a FastAPI application developed for IS601 Module 10. It focuses on secure user management, automated testing, containerization, security scanning, and continuous integration and deployment.

The project uses GitHub Actions to test the application, scan the Docker image for vulnerabilities, and publish the image to Docker Hub.

## Technologies Used

- Python 3.11
- FastAPI
- PostgreSQL
- Docker and Docker Compose
- Git and GitHub
- GitHub Actions
- pytest
- Playwright
- Trivy
- Docker Hub

## GitHub Repository

https://github.com/islamnavid/module10_is601

## Docker Hub Repository

https://hub.docker.com/r/navidislam/module10_is601

## Installation

Clone the repository:

```bash
git clone https://github.com/islamnavid/module10_is601.git
cd module10_is601
```

Create and activate a virtual environment:

```bash
python3.11 -m venv venv
source venv/bin/activate
```

Install dependencies:

```bash
python -m pip install -r requirements.txt
```

## Running the Application

Start the application using Uvicorn:

```bash
python -m uvicorn main:app --reload
```

Open the application at:

http://127.0.0.1:8000

FastAPI interactive documentation is available at:

http://127.0.0.1:8000/docs

**Database configuration:** PostgreSQL must be running and the application must have a valid `DATABASE_URL` environment variable configured before using database-dependent features.

## Automated Testing

The project includes unit, integration, and end-to-end tests.

Run unit tests:

```bash
python -m pytest tests/unit/ -v
```

Run integration tests:

```bash
python -m pytest tests/integration/ -v
```

Run end-to-end tests:

```bash
python -m pytest tests/e2e/ -v
```

End-to-end testing requires the FastAPI server and the appropriate Playwright browser dependencies.

## Docker

Build the Docker image:

```bash
docker build -t module10_is601 .
```

Run the Docker container:

```bash
docker run --rm -p 8000:8000 module10_is601
```

For database-dependent functionality, provide the required database configuration and ensure the container can reach PostgreSQL.

Alternatively, pull the published Docker Hub image:

```bash
docker pull navidislam/module10_is601:latest
```

Run the published image:

```bash
docker run --rm -p 8000:8000 navidislam/module10_is601:latest
```

## Continuous Integration and Deployment

The GitHub Actions workflow is located at:

`.github/workflows/test.yml`

The workflow contains three jobs:

### 1. Test

- Configures Python 3.11
- Starts PostgreSQL
- Installs application dependencies
- Runs unit tests
- Runs integration tests
- Starts the FastAPI application
- Runs end-to-end tests

### 2. Security

- Builds the Docker image
- Scans dependencies using Trivy
- Checks for HIGH and CRITICAL vulnerabilities with available