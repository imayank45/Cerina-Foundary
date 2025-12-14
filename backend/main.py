# from fastapi import FastAPI, HTTPException
# from fastapi.middleware.cors import CORSMiddleware
# from pydantic import BaseModel
# from typing import Optional
# import uuid
# from backend.graph import cerina_graph
# from backend.state import CerinasState
# from backend.database import db
# import logging

# logger = logging.getLogger(__name__)


# app = FastAPI(title="Cerina Protocol Foundry")

# # CORS for React frontend
# app.add_middleware(
#     CORSMiddleware,
#     allow_origins=["http://localhost:3000"],
#     allow_credentials=True,
#     allow_methods=["*"],
#     allow_headers=["*"],
# )

# class ProtocolRequest(BaseModel):
#     user_intent: str
#     original_query: str

# class StateUpdateRequest(BaseModel):
#     thread_id: str
#     human_approval: bool
#     human_edits: Optional[str] = ""

# class ProtocolResponse(BaseModel):
#     thread_id: str
#     status: str
#     current_draft: str
#     safety_flags: list
#     clinical_feedback: str
#     empathy_score: float
#     safety_score: float

# @app.post("/generate")
# async def generate_protocol(request: ProtocolRequest) -> dict:
#     thread_id = str(uuid.uuid4())
#     logger.info(f"Generating protocol: {thread_id} - {request.user_intent}")

#     # 1) Build initial state
#     initial_state = CerinasState(
#         user_intent=request.user_intent,
#         original_query=request.original_query,
#     )
#     # REQUIRED for checkpointer: thread_id inside `configurable`
#     config = {"configurable": {"thread_id": thread_id}}

#     try:
#         # 2) Run graph
#         output = cerina_graph.invoke(initial_state, config=config)

#         # 3) Normalize to CerinasState
#         if isinstance(output, dict):
#             state = CerinasState(**output)
#         else:
#             state = output

#         # 4) Persist
#         db.save_protocol(thread_id, state)

#         # 5) Return response built from state (NOT from raw output)
#         return {
#             "thread_id": thread_id,
#             "status": state.status,
#             "current_draft": state.current_draft,
#             "safety_flags": [
#                 {
#                     "line": f.line_num,
#                     "severity": f.severity,
#                     "issue": f.issue,
#                     "suggestion": f.suggestion,
#                 }
#                 for f in state.safety_flags
#             ],
#             "clinical_feedback": state.clinical_feedback,
#             "empathy_score": state.empathy_score,
#             "safety_score": state.safety_score,
#             "agent_notes": state.agent_notes,
#             "iteration_count": state.iteration_count,
#         }
#     except Exception as e:
#         logger.exception("Error in /generate")
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/approve")
# async def approve_and_finalize(request: StateUpdateRequest) -> dict:
#     """
#     Human approves and optionally edits the draft.
#     """
#     config = {"configurable": {"thread_id": request.thread_id}}
    
#     # Load previous state from checkpoint
#     try:
#         # Retrieve state from checkpointer
#         checkpoint = db.checkpointer.get(request.thread_id, None)
#         if not checkpoint:
#             raise ValueError("Thread not found")
        
#         # Reconstruct state (or reload from database)
#         # For simplicity: re-load and update
#         state = CerinasState(
#             user_intent="",  # Reload from DB
#             original_query=""
#         )
#         state.human_approval = request.human_approval
#         state.human_edits = request.human_edits
        
#         # Resume graph
#         output = cerina_graph.invoke(state, config=config)
        
        
#     except Exception as e:
#         raise HTTPException(status_code=500, detail=str(e))
    
#     # Save updated protocol
#     db.save_protocol(request.thread_id, output)
    
#     return {
#         "thread_id": request.thread_id,
#         "status": output.status,
#         "final_protocol": output.final_protocol
#     }

# @app.get("/status/{thread_id}")
# async def get_status(thread_id: str) -> dict:
#     """
#     Get current state of a protocol generation.
#     """
#     config = {"configurable": {"thread_id": thread_id}}
    
#     # Fetch from checkpoint
#     try:
#         checkpoint = db.checkpointer.get(thread_id, None)
#         if not checkpoint:
#             raise ValueError("Thread not found")
        
#         # Reconstruct state from checkpoint (requires deserialization)
#         # This is a simplified version; full implementation needs proper checkpoint parsing
#         return {
#             "thread_id": thread_id,
#             "status": "unknown"  # TODO: implement proper deserialization
#         }
#     except Exception as e:
#         raise HTTPException(status_code=404, detail=str(e))

# if __name__ == "__main__":
#     import uvicorn
#     uvicorn.run(app, host="0.0.0.0", port=8000)


from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from pydantic import BaseModel
from typing import Optional, Dict, List
import uuid
import logging

from backend.graph import cerina_graph
from backend.state import CerinasState
from backend.database import db, ProtocolQueryRecord

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Cerina Protocol Foundry",
    description="Autonomous multi-agent system for designing CBT exercises",
    version="1.0.0"
)

# ⚠️ CRITICAL: CORSMiddleware FIRST, then GZIPMiddleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["*"],
    max_age=3600,
)
app.add_middleware(GZipMiddleware, minimum_size=1000)

# Request/Response models
class ProtocolRequest(BaseModel):
    user_intent: str
    original_query: str


class ApprovalRequest(BaseModel):
    thread_id: str
    human_approval: bool
    human_edits: Optional[str] = ""


class SafetyFlagResponse(BaseModel):
    line: int
    severity: str
    issue: str
    suggestion: str


class ProtocolResponse(BaseModel):
    thread_id: str
    status: str
    current_draft: str
    safety_flags: List[SafetyFlagResponse]
    clinical_feedback: str
    empathy_score: float
    safety_score: float
    agent_notes: Dict[str, List[str]]


# Routes
@app.get("/health")
async def health():
    """Health check."""
    return {"status": "ok", "service": "cerina-foundry"}


# @app.post("/generate", response_model=dict)
# async def generate_protocol(request: ProtocolRequest):
#     """
#     Trigger protocol generation.
    
#     Returns initial state after agents process until halt point.
#     """
#     thread_id = str(uuid.uuid4())
#     logger.info(f"Generating protocol: {thread_id} - {request.user_intent}")
    
#     # Initial state
#     initial_state = CerinasState(
#         user_intent=request.user_intent,
#         original_query=request.original_query
#     )
    
#     try:
#         # Run graph
#         # output = cerina_graph.invoke(initial_state)
#         output = cerina_graph.invoke(
#             initial_state,
#             config={"configurable": {"thread_id": thread_id}}
#         )
        

        
#         # Save to database
#         db.save_protocol(thread_id, output)
        
#         logger.info(f"Protocol generation halted for review: {thread_id}")
        
#         return {
#             "thread_id": thread_id,
#             "status": output.status,
#             "current_draft": output.current_draft,
#             "safety_flags": [
#                 {
#                     "line": f.line_num,
#                     "severity": f.severity,
#                     "issue": f.issue,
#                     "suggestion": f.suggestion
#                 }
#                 for f in output.safety_flags
#             ],
#             "clinical_feedback": output.clinical_feedback,
#             "empathy_score": round(output.empathy_score, 1),
#             "safety_score": round(output.safety_score, 1),
#             "agent_notes": output.agent_notes,
#             "iteration_count": output.iteration_count
#         }
    
#     except Exception as e:
#         logger.error(f"Error in protocol generation: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/approve", response_model=dict)
# async def approve_and_finalize(request: ApprovalRequest):
#     """
#     Human approves and optionally edits the draft.
    
#     Finalizes the protocol for delivery.
#     """
#     logger.info(f"Approving protocol: {request.thread_id}")
    
#     try:
#         # Step 1: Retrieve protocol from database
#         record = db.get_protocol(request.thread_id)
#         if not record:
#             logger.error(f"Protocol not found: {request.thread_id}")
#             raise HTTPException(status_code=404, detail="Protocol not found")
        
#         logger.info(f"Retrieved protocol from DB: {request.thread_id}")
        
#         # Step 2: Reconstruct full state with all fields from database
#         state = CerinasState(
#             user_intent=record.user_intent,
#             original_query=record.original_query
#         )
        
#         logger.info(f"Reconstructed state for approval: intent={state.user_intent[:50]}")
        
#         # Step 3: Set approval flags
#         state.human_approval = request.human_approval
#         state.human_edits = request.human_edits or ""
#         state.halted_for_human = True
#         state.status = "halted"
        
#         logger.info(f"State prepared: human_approval={state.human_approval}, edits_provided={len(state.human_edits) > 0}")
        
#         # Step 4: Run graph (routes to synthesizer based on halted_for_human flag)
#         logger.info("Invoking graph for synthesis...")
#         # output = cerina_graph.invoke(state)
        
#         output = cerina_graph.invoke(
#             state,
#             config={"configurable": {"thread_id": request.thread_id}}
#         )
#         logger.info(f"Graph execution complete: status={output.status}")
        
#         # Step 5: Save updated protocol to database
#         db.save_protocol(request.thread_id, output)
#         logger.info(f"Protocol finalized: {request.thread_id}")
        
#         return {
#             "thread_id": request.thread_id,
#             "status": output.status,
#             "final_protocol": output.final_protocol or output.current_draft
#         }
    
#     except HTTPException:
#         raise
#     except Exception as e:
#         logger.error(f"Error approving protocol: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))


# @app.post("/generate", response_model=dict)
# async def generate_protocol(request: ProtocolRequest):
#     thread_id = str(uuid.uuid4())
#     logger.info(f"Generating protocol: {thread_id} - {request.user_intent}")

#     initial_state = CerinasState(
#         user_intent=request.user_intent,
#         original_query=request.original_query,
#     )

#     try:
#         result = cerina_graph.invoke(
#             initial_state,
#             config={"configurable": {"thread_id": thread_id}},
#         )

#         # IMPORTANT: if result is a dict, try typical LangGraph keys
#         if isinstance(result, dict):
#             # If the compiled graph returns {"state": CerinasState, ...}
#             possible_state = result.get("state") or result.get("checkpoint") or result.get("values")
#             if isinstance(possible_state, CerinasState):
#                 state = possible_state
#             else:
#                 # As a last resort, keep initial_state but log clearly
#                 logger.warning(f"Graph returned dict without CerinasState, using initial_state for {thread_id}")
#                 state = initial_state
#         else:
#             state = result

#         db.save_protocol(thread_id, state)
#         logger.info(f"Protocol generation halted for review: {thread_id}")
#         print(result)

#         return {
#             "thread_id": thread_id,
#             "status": getattr(state, "status", "unknown"),
#             "current_draft": getattr(state, "current_draft", ""),
#             "safety_flags": [
#                 {
#                     "line": f.line_num,
#                     "severity": f.severity,
#                     "issue": f.issue,
#                     "suggestion": f.suggestion,
#                 }
#                 for f in getattr(state, "safety_flags", [])
#             ],
#             "clinical_feedback": getattr(state, "clinical_feedback", ""),
#             "empathy_score": round(getattr(state, "empathy_score", 0.0), 1),
#             "safety_score": round(getattr(state, "safety_score", 0.0), 1),
#             "agent_notes": getattr(state, "agent_notes", {}),
#             "iteration_count": getattr(state, "iteration_count", 0),
#         }

#     except Exception as e:
#         logger.error(f"Error in protocol generation: {str(e)}", exc_info=True)
#         raise HTTPException(status_code=500, detail=str(e))

@app.post("/generate", response_model=dict)
async def generate_protocol(request: ProtocolRequest):
    """
    Trigger protocol generation.

    Returns initial state after agents process until halt point.
    """
    thread_id = str(uuid.uuid4())
    logger.info(f"Generating protocol: {thread_id} - {request.user_intent}")

    # Initial state as plain dict for LangGraph
    initial_state = CerinasState(
        user_intent=request.user_intent,
        original_query=request.original_query,
    )
    initial_state_dict = initial_state.model_dump()

    try:
        # LangGraph returns a dict[str, Any]
        result = cerina_graph.invoke(
            initial_state_dict,
            config={"configurable": {"thread_id": thread_id}},
        )

        if not isinstance(result, dict):
            raise RuntimeError(f"Graph returned non-dict result: {type(result)}")

        # Build a CerinasState from the dict so rest of backend stays the same
        state = CerinasState(**result)

        # Persist
        db.save_protocol(thread_id, state)
        logger.info(f"Protocol generation halted for review: {thread_id}")

        # Shape must match your ProtocolResponse type
        return {
            "thread_id": thread_id,
            "status": state.status,
            "current_draft": state.current_draft,
            "safety_flags": [
                {
                    "line": f.line_num,
                    "severity": f.severity,
                    "issue": f.issue,
                    "suggestion": f.suggestion,
                }
                for f in state.safety_flags
            ],
            "clinical_feedback": state.clinical_feedback,
            "empathy_score": round(state.empathy_score, 1),
            "safety_score": round(state.safety_score, 1),
            "agent_notes": state.agent_notes,
            "iteration_count": state.iteration_count,
        }

    except Exception as e:
        logger.error(f"Error in protocol generation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



@app.post("/approve", response_model=dict)
async def approve_and_finalize(request: ApprovalRequest):
    """
    Human approves and optionally edits the draft.
    
    Finalizes the protocol for delivery.
    """
    logger.info(f"Approving protocol: {request.thread_id}")

    try:
        # Retrieve protocol from DB using SQLAlchemy directly
        session = db.Session()
        record = session.query(ProtocolQueryRecord).filter_by(
            thread_id=request.thread_id
        ).first()
        session.close()

        if not record:
            logger.error(f"Protocol not found: {request.thread_id}")
            raise HTTPException(status_code=404, detail="Protocol not found")

        logger.info(f"Retrieved protocol from DB: {request.thread_id}")

        # Reconstruct minimal state needed for synthesis
        state = CerinasState(
            user_intent=record.user_intent,
            original_query=record.original_query,
        )
        state.human_approval = request.human_approval
        state.human_edits = request.human_edits or ""
        state.halted_for_human = True
        state.status = "halted"

        logger.info(
            f"State prepared: human_approval={state.human_approval}, "
            f"edits_provided={len(state.human_edits) > 0}"
        )

        # Run graph so Synthesizer finalizes the protocol
        logger.info("Invoking graph for synthesis...")
        result = cerina_graph.invoke(
            state,
            config={"configurable": {"thread_id": request.thread_id}},
        )

        # If your graph returns a dict, wrap it back into CerinasState
        if isinstance(result, dict):
            output = CerinasState(**result)
        else:
            output = result

        logger.info(f"Graph execution complete: status={output.status}")

        # Save updated protocol
        db.save_protocol(request.thread_id, output)
        logger.info(f"Protocol finalized: {request.thread_id}")

        return {
            "thread_id": request.thread_id,
            "status": output.status,
            "final_protocol": output.final_protocol or output.current_draft,
        }

    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error approving protocol: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))



@app.get("/protocol/{thread_id}", response_model=dict)
async def get_protocol(thread_id: str):
    """Retrieve a protocol by thread ID."""
    try:
        record = db.get_protocol(thread_id)
        if not record:
            raise HTTPException(status_code=404, detail="Protocol not found")
        
        return {
            "thread_id": record.thread_id,
            "user_intent": record.user_intent,
            "status": record.status,
            "final_protocol": record.final_protocol,
            "safety_score": record.safety_score,
            "empathy_score": record.empathy_score,
            "created_at": record.created_at.isoformat()
        }
    
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error retrieving protocol: {str(e)}", exc_info=True)
        raise HTTPException(status_code=404, detail=str(e))


@app.get("/protocols", response_model=dict)
async def list_protocols(limit: int = 10):
    """List recent protocols."""
    try:
        session = db.Session()
        records = session.query(db.__class__.__dict__['ProtocolQueryRecord']).order_by(
            db.__class__.__dict__['ProtocolQueryRecord'].created_at.desc()
        ).limit(limit).all()
        session.close()
        
        return {
            "count": len(records),
            "protocols": [
                {
                    "thread_id": r.thread_id,
                    "user_intent": r.user_intent,
                    "status": r.status,
                    "safety_score": r.safety_score,
                    "empathy_score": r.empathy_score,
                    "created_at": r.created_at.isoformat()
                }
                for r in records
            ]
        }
    
    except Exception as e:
        logger.error(f"Error listing protocols: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        app,
        host="0.0.0.0",
        port=8000,
        log_level="info"
    )