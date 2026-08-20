"""Unit tests for Docker containerization and Docker Compose configuration."""

import os
import pytest


def test_dockerfile_exists_and_valid():
    """Verify backend Dockerfile exists and contains multi-stage directives."""
    path = os.path.join("Dockerfile")
    assert os.path.exists(path), "Dockerfile missing"

    with open(path, "r") as f:
        content = f.read()
        assert "FROM python:3.11-slim AS builder" in content
        assert "FROM python:3.11-slim AS runner" in content
        assert "EXPOSE 8000" in content
        assert "HEALTHCHECK" in content
        assert "USER appuser" in content


def test_dockerfile_frontend_exists():
    """Verify frontend Dockerfile exists and exposes port 8501."""
    path = os.path.join("Dockerfile.frontend")
    assert os.path.exists(path), "Dockerfile.frontend missing"

    with open(path, "r") as f:
        content = f.read()
        assert "EXPOSE 8501" in content
        assert "HEALTHCHECK" in content
        assert "streamlit" in content


def test_docker_compose_validity():
    """Verify docker-compose.yml contains backend, frontend, ports, and volumes."""
    path = os.path.join("docker-compose.yml")
    assert os.path.exists(path), "docker-compose.yml missing"

    with open(path, "r") as f:
        content = f.read()
        assert "backend:" in content
        assert "frontend:" in content
        assert "8000:8000" in content
        assert "8501:8501" in content
        assert "edusense_data:" in content
        assert "healthcheck:" in content


def test_dockerignore_exists():
    """Verify .dockerignore excludes virtualenv and cache."""
    path = os.path.join(".dockerignore")
    assert os.path.exists(path), ".dockerignore missing"

    with open(path, "r") as f:
        content = f.read()
        assert ".venv" in content
        assert "__pycache__" in content
