
import os

from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL
from sqlalchemy.orm import sessionmaker

# Load database credentials from .env
load_dotenv()

required_settings = [
    "DB_HOST",
    "DB_PORT",
    "DB_NAME",
    "DB_USER",
    "DB_PASSWORD",
]

missing_settings = [
    key for key in required_settings if not os.getenv(key)
]

if missing_settings:
    raise RuntimeError(
        f"Missing database settings in .env: {', '.join(missing_settings)}"
    )

# Build the connection URL safely, even if the password
# contains special characters.
database_url = URL.create(
    drivername="postgresql+psycopg",
    username=os.getenv("DB_USER"),
    password=os.getenv("DB_PASSWORD"),
    host=os.getenv("DB_HOST"),
    port=int(os.getenv("DB_PORT")),
    database=os.getenv("DB_NAME"),
)

# Create the database engine.
engine = create_engine(
    database_url,
    pool_pre_ping=True,
)

# Create database sessions for future API operations.
SessionLocal = sessionmaker(
    bind=engine,
    autoflush=False,
    autocommit=False,
)


def get_db():
    """Provide a database session and close it after use."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def test_connection():
    """Verify that PostgreSQL is reachable."""
    with engine.connect() as connection:
        result = connection.execute(
            text("SELECT current_database(), current_user")
        )
        database_name, username = result.one()

    return {
        "database": database_name,
        "user": username,
        "status": "connected",
    }


if __name__ == "__main__":
    print(test_connection())
