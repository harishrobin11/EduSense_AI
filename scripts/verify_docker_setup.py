"""Verification script for EduSense AI Docker infrastructure."""

import os
import sys


def verify_docker_files():
    """Verify existence and syntax patterns of Docker configuration files."""
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    errors = []

    # 1. Dockerfile
    dockerfile_path = os.path.join(base_dir, "Dockerfile")
    if not os.path.exists(dockerfile_path):
        errors.append("Dockerfile missing")
    else:
        with open(dockerfile_path, "r") as f:
            content = f.read()
            if "FROM python:3.11-slim AS builder" not in content:
                errors.append("Dockerfile missing multi-stage builder stage")
            if "EXPOSE 8000" not in content:
                errors.append("Dockerfile missing EXPOSE 8000")
            if "HEALTHCHECK" not in content:
                errors.append("Dockerfile missing HEALTHCHECK directive")
            if "USER appuser" not in content:
                errors.append("Dockerfile missing non-root user execution")

    # 2. Dockerfile.frontend
    frontend_dockerfile_path = os.path.join(base_dir, "Dockerfile.frontend")
    if not os.path.exists(frontend_dockerfile_path):
        errors.append("Dockerfile.frontend missing")
    else:
        with open(frontend_dockerfile_path, "r") as f:
            content = f.read()
            if "EXPOSE 8501" not in content:
                errors.append("Dockerfile.frontend missing EXPOSE 8501")

    # 3. docker-compose.yml
    compose_path = os.path.join(base_dir, "docker-compose.yml")
    if not os.path.exists(compose_path):
        errors.append("docker-compose.yml missing")
    else:
        with open(compose_path, "r") as f:
            content = f.read()
            if "backend:" not in content or "frontend:" not in content:
                errors.append("docker-compose.yml missing backend or frontend service")
            if "edusense_data:" not in content:
                errors.append("docker-compose.yml missing persistent volume edusense_data")
            if "8000:8000" not in content or "8501:8501" not in content:
                errors.append("docker-compose.yml missing port mappings")

    # 4. .dockerignore
    ignore_path = os.path.join(base_dir, ".dockerignore")
    if not os.path.exists(ignore_path):
        errors.append(".dockerignore missing")

    if errors:
        print("❌ Docker Infrastructure Validation Failed:")
        for err in errors:
            print(f"  - {err}")
        sys.exit(1)
    else:
        print("✅ Docker Infrastructure Validation Passed!")
        print("  - Dockerfile (Multi-stage backend)")
        print("  - Dockerfile.frontend (Streamlit UI)")
        print("  - docker-compose.yml (Orchestration & healthchecks)")
        print("  - .dockerignore (Clean build contexts)")


if __name__ == "__main__":
    verify_docker_files()
