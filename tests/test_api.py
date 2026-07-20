import os
import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from backend.app.core.database import Base
from backend.app.core.security import hash_password, verify_password, create_access_token, verify_access_token
from backend.app.services.file_service import suggest_clean_name, detect_outliers_iqr

# Setup test DB (in-memory SQLite)
TEST_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(TEST_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


@pytest.fixture(scope="module")
def setup_db():
    Base.metadata.create_all(bind=engine)
    yield
    Base.metadata.drop_all(bind=engine)


def test_password_security():
    """Verify that password hashing and verification works correctly."""
    password = "supersecurepassword123"
    hashed = hash_password(password)
    assert hashed != password
    assert verify_password(password, hashed) is True
    assert verify_password("wrongpassword", hashed) is False


def test_jwt_generation():
    """Verify that access token creation and decoding maps the subject correctly."""
    email = "tester@company.com"
    token = create_access_token(email)
    assert token is not None
    decoded = verify_access_token(token)
    assert decoded == email


def test_column_name_normalizer():
    """Verify renaming suggestion conversions for database friendly columns."""
    assert suggest_clean_name("Revenue (USD)") == "revenue_usd"
    assert suggest_clean_name("  Gross profit - margin %  ") == "gross_profit_margin"
    assert suggest_clean_name("Date/Time") == "date_time"


def test_outlier_detection_iqr():
    """Verify outliers computation via IQR method."""
    # Data without outliers
    clean_data = [10, 12, 11, 13, 12, 10, 11, 12]
    outlier_info = detect_outliers_iqr(clean_data)
    assert outlier_info["count"] == 0

    # Data with outlier
    dirty_data = [10, 12, 11, 13, 12, 10, 11, 12, 100]
    outlier_info_dirty = detect_outliers_iqr(dirty_data)
    assert outlier_info_dirty["count"] == 1
    assert outlier_info_dirty["thresholds"]["upper"] < 100
