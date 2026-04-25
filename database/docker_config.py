"""
VedDrishti - Docker Configuration
Handles database connections when running in containers
"""

import os


def get_db_config():
    """Get database configuration based on environment"""

    # Check if running in Docker
    in_docker = os.environ.get("DOCKER_ENV", False)

    if in_docker:
        # Use container hostnames
        config = {
            "postgres_host": "postgres",
            "postgres_port": 5432,
            "postgres_user": "veddrishti_user",
            "postgres_password": "veddrishti_password",
            "postgres_db": "veddrishti",
            "mongodb_host": "mongodb",
            "mongodb_port": 27017,
            "ollama_host": "ollama",
            "ollama_port": 11434,
        }
    else:
        # Local development
        config = {
            "postgres_host": "localhost",
            "postgres_port": 5432,
            "postgres_user": "veddrishti_user",
            "postgres_password": "veddrishti_password",
            "postgres_db": "veddrishti",
            "mongodb_host": "localhost",
            "mongodb_port": 27017,
            "ollama_host": "localhost",
            "ollama_port": 11434,
        }

    return config
