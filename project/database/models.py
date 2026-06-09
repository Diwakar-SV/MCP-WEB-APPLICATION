from sqlalchemy import Column, Integer, String, Text, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database.db import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True, index=True, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password = Column(String, nullable=False)
    role = Column(String, default="User", nullable=False)  # "User" or "Admin"

    tickets = relationship("Ticket", back_populates="creator")

class Ticket(Base):
    __tablename__ = "tickets"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String, index=True, nullable=False)
    description = Column(Text, nullable=False)
    status = Column(String, default="OPEN", nullable=False)  # OPEN, IN_PROGRESS, RESOLVED, CLOSED
    priority = Column(String, default="LOW", nullable=False)  # LOW, MEDIUM, HIGH, CRITICAL
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)
    updated_at = Column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now(), nullable=False)
    created_by = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    creator = relationship("User", back_populates="tickets")
    comments = relationship("Comment", back_populates="ticket", cascade="all, delete-orphan")

class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    ticket_id = Column(Integer, ForeignKey("tickets.id", ondelete="CASCADE"), nullable=False)
    comment = Column(Text, nullable=False)
    author = Column(String, nullable=False)  # Storing username for simplicity
    created_at = Column(DateTime(timezone=True), server_default=func.now(), nullable=False)

    ticket = relationship("Ticket", back_populates="comments")

class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"

    id = Column(Integer, primary_key=True, index=True)
    question = Column(String, index=True, nullable=False)
    answer = Column(Text, nullable=False)
    category = Column(String, index=True, nullable=False)
