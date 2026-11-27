import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

from app.db import models  # noqa: F401  (برای اینکه مدل‌ها ثبت بشن)
from app.db.database import Base, get_db
from app.main import app


@pytest.fixture()
def session_factory():
    """یه دیتابیس موقت داخل حافظه با جدول‌های تازه برای هر تست."""
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(engine)
    yield sessionmaker(bind=engine, autoflush=False)
    engine.dispose()


@pytest.fixture()
def client(session_factory):
    """TestClient که به‌جای دیتابیس واقعی از دیتابیس موقت استفاده می‌کنه."""

    def override_get_db():
        db = session_factory()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    yield TestClient(app)
    app.dependency_overrides.clear()