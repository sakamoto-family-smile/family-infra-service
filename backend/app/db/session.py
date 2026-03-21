from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from app.config import settings


def _build_db_url() -> str:
    if settings.CLOUD_SQL_INSTANCE:
        # Cloud SQL via Unix socket (production)
        return (
            f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}"
            f"@/{settings.DB_NAME}"
            f"?host=/cloudsql/{settings.CLOUD_SQL_INSTANCE}"
        )
    # Local development
    return (
        f"postgresql+asyncpg://{settings.DB_USER}:{settings.DB_PASSWORD}"
        f"@localhost:5432/{settings.DB_NAME}"
    )


engine = create_async_engine(
    _build_db_url(),
    echo=settings.DEBUG,
    pool_pre_ping=True,
    pool_size=5,
    max_overflow=10,
)

async_session_factory = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
)
