import pytest
import os
import sys

# 将 src 加入路径，方便导入
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

@pytest.fixture
def app():
    """Create and configure a new app instance for each test."""
    # from src.app_factory import create_app
    # app = create_app({"TESTING": True})
    # yield app
    pass

@pytest.fixture
def client(app):
    """A test client for the app."""
    # return app.test_client()
    pass

@pytest.fixture
def runner(app):
    """A test runner for the app's CLI commands."""
    # return app.test_cli_runner()
    pass
