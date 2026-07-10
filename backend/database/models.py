from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker
import datetime

Base = declarative_base()

class AuditLog(Base):
    __tablename__ = 'audit_logs'

    id = Column(Integer, primary_key=True, index=True)
    timestamp = Column(DateTime, default=datetime.datetime.utcnow)
    goal = Column(String)
    agent = Column(String)
    action = Column(String)
    policy_decision = Column(String)
    approval_event = Column(String, nullable=True)
    retry_count = Column(Integer, default=0)
    execution_time_ms = Column(Integer)
    final_status = Column(String)

# Initialize engine
engine = create_engine('sqlite:///./vaultguard.db', connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def init_db():
    Base.metadata.create_all(bind=engine)
