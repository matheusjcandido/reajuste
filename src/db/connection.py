"""
Database connection management using SQLAlchemy with Streamlit caching.

This module provides database engine, session management, and initialization
functions optimized for Streamlit's execution model.
"""

import streamlit as st
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool
import os

# Database file path
DATABASE_DIR = "data"
DATABASE_FILE = "reajuste.db"
DATABASE_PATH = os.path.join(DATABASE_DIR, DATABASE_FILE)
DATABASE_URL = f"sqlite:///{DATABASE_PATH}"


@st.cache_resource
def get_engine():
    """
    Create and cache SQLAlchemy engine for SQLite.

    Uses StaticPool to avoid threading issues with SQLite in Streamlit's
    multi-threaded environment.

    Returns:
        Engine: SQLAlchemy engine instance
    """
    # Ensure data directory exists
    os.makedirs(DATABASE_DIR, exist_ok=True)

    return create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,  # Required for SQLite with Streamlit
        echo=False  # Set to True for SQL debugging
    )


@st.cache_resource
def get_session_local():
    """
    Create and cache session factory.

    Returns:
        sessionmaker: Session factory for creating database sessions
    """
    engine = get_engine()
    return sessionmaker(autocommit=False, autoflush=False, bind=engine)


def get_db() -> Session:
    """
    Get a new database session.

    Returns:
        Session: SQLAlchemy session for database operations

    Usage:
        db = get_db()
        try:
            # Perform database operations
            db.commit()
        except Exception:
            db.rollback()
            raise
        finally:
            db.close()
    """
    SessionLocal = get_session_local()
    return SessionLocal()


def init_db():
    """
    Initialize database by creating all tables.

    This function should be called once at application startup.
    It's safe to call multiple times - existing tables won't be affected.
    """
    from src.db.models import Base

    engine = get_engine()
    Base.metadata.create_all(bind=engine)


def reset_db():
    """
    Drop all tables and recreate them.

    WARNING: This will delete all data! Only use for development/testing.
    """
    from src.db.models import Base

    engine = get_engine()
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
