from sqlalchemy import create_engine, Column, String, Text, DateTime, Boolean
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from langgraph.checkpoint.sqlite import SqliteSaver  # or PostgresSaver
from datetime import datetime
import json
from backend.state import CerinasState
import sqlite3
from typing import Union
from backend.state import CerinasState


Base = declarative_base()

class ProtocolQueryRecord(Base):
    __tablename__ = "protocol_queries"
    
    id = Column(String, primary_key=True)
    user_intent = Column(String)
    original_query = Column(Text)
    created_at = Column(DateTime, default=datetime.utcnow)
    thread_id = Column(String)
    status = Column(String)
    final_protocol = Column(Text)
    human_approved = Column(Boolean)
    metadata_json = Column("metadata", Text)  # JSON stored in 'metadata' column


class Database:
    def __init__(self, db_url: str = "sqlite:///cerina.db"):
        self.engine = create_engine(db_url)
        Base.metadata.create_all(self.engine)
        self.Session = sessionmaker(bind=self.engine)
        
        # LangGraph checkpointer
        # self.checkpointer = SqliteSaver(connection=self.engine.raw_connection())
        conn = sqlite3.connect("checkpoints.sqlite", check_same_thread=False)
        self.checkpointer = SqliteSaver(conn)

    
#     def save_protocol(self, thread_id: str, state: Union[CerinasState, dict]):
#         """Save protocol to database."""
#         if isinstance(state, dict):
#             state = CerinasState(**state)
#         session = self.Session()
#         record = ProtocolQueryRecord(
#         id=thread_id,
#         thread_id=thread_id,
#         user_intent=state.user_intent,
#         original_query=state.original_query,
#         status=state.status,
#         final_protocol=state.final_protocol,
#         human_approved=state.human_approval,
#         metadata_json=json.dumps({
#             "safety_score": state.safety_score,
#             "empathy_score": state.empathy_score,
#             "iteration_count": state.iteration_count,
#             "agent_notes": state.agent_notes
#         })
# )
        
#         session.add(record)
#         session.commit()
#         session.close()

    def save_protocol(self, thread_id: str, state: Union[CerinasState, dict]):
        """Insert or update a protocol in the database."""
        if isinstance(state, dict):
            state = CerinasState(**state)

        session = self.Session()
        try:
            # Try to load existing record for this thread_id
            record = session.query(ProtocolQueryRecord).filter_by(
                thread_id=thread_id
            ).first()

            if record is None:
                # Create new record
                record = ProtocolQueryRecord(
                    id=thread_id,
                    thread_id=thread_id,
                    created_at=datetime.utcnow(),
                )

            # Update all mutable fields
            record.user_intent = state.user_intent
            record.original_query = state.original_query
            record.status = state.status
            record.final_protocol = state.final_protocol
            record.human_approved = state.human_approval
            record.metadata_json = json.dumps(
                {
                    "safety_score": state.safety_score,
                    "empathy_score": state.empathy_score,
                    "iteration_count": state.iteration_count,
                    "agent_notes": state.agent_notes,
                }
            )

            session.add(record)
            session.commit()
        except Exception:
            session.rollback()
            raise
        finally:
            session.close()


db = Database()
