from langchain_openai import ChatOpenAI
from backend.state import CerinasState
from dotenv import load_dotenv
load_dotenv()

def clinical_critic_node(state: CerinasState) -> CerinasState:
    """
    Clinical Critic: Evaluates tone, empathy, and CBT alignment.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
    critique_prompt = f"""
    As a clinical psychologist, critique this CBT exercise:
    
    {state.current_draft}
    
    Evaluate:
    1. Empathy: Does it feel supportive without being patronizing?
    2. Clarity: Is it easy to understand and follow?
    3. CBT Alignment: Does it follow cognitive-behavioral principles?
    4. Tone: Is it warm and non-judgmental?
    5. Actionability: Can someone actually do this?
    
    Provide:
    - Overall empathy score (0-100)
    - Top 3 tone issues (if any)
    - Specific suggestions for improvement
    
    Be constructive. Format as:
    EMPATHY_SCORE: [number]
    TONE_ISSUES: [comma-separated list]
    SUGGESTIONS: [detailed paragraph]
    """
    
    response = llm.invoke(critique_prompt).content
    
    # Parse response
    try:
        lines = response.split("\n")
        for line in lines:
            if line.startswith("EMPATHY_SCORE:"):
                state.empathy_score = float(line.split(":").strip())
            elif line.startswith("TONE_ISSUES:"):
                issues_str = line.split(":", 1).strip()
                state.tone_issues = [i.strip() for i in issues_str.split(",") if i.strip()]
            elif line.startswith("SUGGESTIONS:"):
                state.clinical_feedback = line.split(":", 1).strip()
    except:
        state.empathy_score = 75
        state.clinical_feedback = "Review for tone and clarity improvements."
    
    state.agent_notes.setdefault("clinical_critic", []).append(
        f"Empathy score: {state.empathy_score}. Issues: {len(state.tone_issues)}"
    )
    
    return state
