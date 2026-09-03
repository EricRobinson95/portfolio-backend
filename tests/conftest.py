import os


os.environ["DATABASE_URL"] = "sqlite+pysqlite:///:memory:"
os.environ["SECRET_KEY"] = "test-only-secret-key"
os.environ["PROJECT_NAME"] = "Portfolio API Tests"
os.environ["API_VERSION"] = "test"
os.environ["ADMIN_USERNAME"] = "test-admin"
os.environ["ADMIN_PASSWORD"] = "test-only-password"
os.environ["ENVIRONMENT"] = "test"