"""Unit tests verifying Sprint 12 documentation artifacts and portfolio files."""

import os
import pytest


def test_readme_and_doc_files_exist():
    """Verify README.md, ARCHITECTURE.md, and DEPLOYMENT_AWS.md exist and are non-empty."""
    readme_p = "README.md"
    arch_p = os.path.join("docs", "ARCHITECTURE.md")
    deploy_p = os.path.join("docs", "DEPLOYMENT_AWS.md")

    assert os.path.exists(readme_p), "README.md missing"
    assert os.path.exists(arch_p), "ARCHITECTURE.md missing"
    assert os.path.exists(deploy_p), "DEPLOYMENT_AWS.md missing"

    assert os.path.getsize(readme_p) > 500
    assert os.path.getsize(arch_p) > 500
    assert os.path.getsize(deploy_p) > 500


def test_readme_contains_quickstart_and_badges():
    """Verify README.md contains badges, quickstart, and API endpoints."""
    with open("README.md", "r") as f:
        content = f.read()
        assert "EduSense AI" in content
        assert "docker-compose up" in content
        assert "/auth/register" in content
        assert "/predict/struggle" in content


def test_architecture_doc_contains_diagrams():
    """Verify ARCHITECTURE.md contains Mermaid system diagrams."""
    with open(os.path.join("docs", "ARCHITECTURE.md"), "r") as f:
        content = f.read()
        assert "mermaid" in content
        assert "Presentation Layer" in content
        assert "Service Orchestration Layer" in content
