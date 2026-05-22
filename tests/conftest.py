import os

# Must be set before any tech_ziwei module is imported (config.py initialises
# Settings at module level). This block runs during conftest import, which
# precedes test-file collection.
os.environ.setdefault("DATABASE_URL", "postgresql+asyncpg://test:test@localhost/tech_ziwei_test")
os.environ.setdefault("SECRET_KEY", "test-secret-key-32-chars-minimum!!")
os.environ.setdefault("ANTHROPIC_API_KEY", "test-anthropic-key")
