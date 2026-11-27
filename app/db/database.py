import os
from collections.abc import Iterator

from sqlalchemy import create_engine
from sqlalchemy.orm import DeclarativeBase, Session, sessionmaker

DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./docintel.db")

# SQLite به‌طور پیش‌فرض اجازه نمی‌ده یه اتصال بین چند thread استفاده بشه.
# چون endpointهای def معمولی FastAPI توی thread جدا اجرا می‌شن، این محدودیت رو برمی‌داریم.
connect_args = {"check_same_thread": False} if DATABASE_URL.startswith("sqlite") else {}

engine = create_engine(DATABASE_URL, connect_args=connect_args)
SessionLocal = sessionmaker(bind=engine, autoflush=False)


class Base(DeclarativeBase):
    """کلاس پایه همه مدل‌های دیتابیس."""


def get_db() -> Iterator[Session]:
    """برای هر درخواست یه session می‌سازه و بعدش می‌بنده."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()