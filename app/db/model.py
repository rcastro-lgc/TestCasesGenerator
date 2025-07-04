import os
from sqlalchemy import Column, String, Text, DateTime, Boolean, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import ForeignKey, LargeBinary
from sqlalchemy.orm import relationship

Base = declarative_base()

# RUTA ABSOLUTA a la base
base_dir = os.path.abspath(os.path.dirname(__file__))
db_path = os.path.join(base_dir, '../../data/proref.db')
engine = create_engine(f'sqlite:///{db_path}', echo=False)

SessionLocal = sessionmaker(bind=engine)

class Ticket(Base):
    __tablename__ = 'tickets'
    id = Column(String, primary_key=True)
    jira_key = Column(String, unique=True, nullable=False)
    title = Column(Text)
    description = Column(Text)
    status = Column(String)
    issue_type = Column(String)
    updated_at = Column(DateTime)
    fetched_at = Column(DateTime)
    questions_generated = Column(Boolean, default=False)
    test_cases_generated = Column(Boolean, default=False)
    posted_to_jira = Column(Boolean, default=False)

    # Relationship to the test cases
    test_cases = relationship("TestCase", back_populates="ticket", cascade="all, delete-orphan")

class TestCase(Base):
    __tablename__ = 'test_cases'
    id = Column(String, primary_key=True)
    ticket_id = Column(String, ForeignKey('tickets.id'), nullable=False)
    scenario = Column(Text, nullable=False)
    action = Column(Text, nullable=False)
    expected_behavior = Column(Text, nullable=False)
    created_at = Column(DateTime)
    edited = Column(Boolean, default=False)

    # Relationship to the parent ticket
    ticket = relationship("Ticket", back_populates="test_cases")

class TicketEmbedding(Base):
    __tablename__ = 'ticket_embeddings'

    ticket_id = Column(String, ForeignKey('tickets.id'), primary_key=True)
    embedding = Column(LargeBinary, nullable=False)

    ticket = relationship("Ticket")

def init_db():
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    Base.metadata.create_all(engine)
