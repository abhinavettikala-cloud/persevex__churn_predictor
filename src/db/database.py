"""
SQLite Database Connection & Schema Management for Telecom Churn Prediction System.
Provides thread-safe connection pooling and automatic schema migration.
"""

import sqlite3
import os
import logging
from typing import Generator
from contextlib import contextmanager

logger = logging.getLogger(__name__)

DB_PATH = os.getenv("DATABASE_PATH", "churn_predictions.db")


def get_db_connection() -> sqlite3.Connection:
    """Returns a SQLite connection with dict row factory enabled."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


@contextmanager
def db_session() -> Generator[sqlite3.Connection, None, None]:
    """Context manager for managing DB transaction lifespan."""
    conn = get_db_connection()
    try:
        yield conn
        conn.commit()
    except Exception as e:
        conn.rollback()
        logger.error(f"Database transaction error: {e}")
        raise e
    finally:
        conn.close()


def init_db() -> None:
    """Initializes the database schema if not already present."""
    logger.info(f"Initializing SQLite database at '{DB_PATH}'...")
    with db_session() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS prediction_history (
                id TEXT PRIMARY KEY,
                timestamp TEXT NOT NULL,
                prediction TEXT NOT NULL,
                churn_label INTEGER NOT NULL,
                probability REAL NOT NULL,
                confidence_score REAL NOT NULL,
                risk_level TEXT NOT NULL,
                execution_time_ms REAL NOT NULL,
                model_version TEXT NOT NULL,
                gender TEXT,
                SeniorCitizen INTEGER,
                Partner TEXT,
                Dependents TEXT,
                tenure INTEGER,
                PhoneService TEXT,
                MultipleLines TEXT,
                InternetService TEXT,
                OnlineSecurity TEXT,
                OnlineBackup TEXT,
                DeviceProtection TEXT,
                TechSupport TEXT,
                StreamingTV TEXT,
                StreamingMovies TEXT,
                Contract TEXT,
                PaperlessBilling TEXT,
                PaymentMethod TEXT,
                MonthlyCharges REAL,
                TotalCharges REAL,
                top_positive_factors TEXT,
                top_negative_factors TEXT,
                explanation_text TEXT
            );
        """)
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_timestamp ON prediction_history(timestamp);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_prediction ON prediction_history(prediction);")
        cursor.execute("CREATE INDEX IF NOT EXISTS idx_risk_level ON prediction_history(risk_level);")
        logger.info("Database schema initialization complete.")


if __name__ == "__main__":
    init_db()
