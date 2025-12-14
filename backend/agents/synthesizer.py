from langchain_openai import ChatOpenAI
from backend.state import CerinasState
from dotenv import load_dotenv
load_dotenv()
def synthesizer_node(state: CerinasState) -> CerinasState:
    """
    Synthesizer: Finalizes the protocol with all feedback incorporated.
    """
    if not state.human_approval:
        # Not yet approved, skip
        return state
    
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.5)
    
    # Incorporate human edits
    draft_to_finalize = state.human_edits if state.human_edits else state.current_draft
    
    finalize_prompt = f"""
    Finalize this CBT exercise for delivery to a client. 
    Polish for tone, clarity, and formatting.
    
    Current draft:
    {draft_to_finalize}
    
    Guidelines:
    - Keep it warm and accessible
    - Use clear headers
    - Add a closing affirmation
    - Ensure it's printable
    
    Return the final protocol only.
    """
    
    final = llm.invoke(finalize_prompt).content
    state.final_protocol = final
    state.status = "finalized"
    state.agent_notes.setdefault("synthesizer", []).append("Protocol finalized")
    
    return state
