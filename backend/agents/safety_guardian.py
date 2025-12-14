from langchain_openai import ChatOpenAI
from backend.state import CerinasState, SafetyFlag
import re
from dotenv import load_dotenv
load_dotenv()

def safety_guardian_node(state: CerinasState) -> CerinasState:
    """
    Safety Guardian: Audits draft for harmful content.
    """
    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
    audit_prompt = f"""
    Review this CBT exercise for safety concerns:
    
    {state.current_draft}
    
    Check for:
    1. Self-harm encouragement
    2. Dangerous medical advice
    3. Pressure or coercion
    4. Victim-blaming language
    5. Overly complex for someone in crisis
    
    For each issue found:
    - Specify the line/section
    - Severity: critical, moderate, or low
    - Explanation
    - Suggestion for fix
    
    Format as JSON array:
    [
      {{"line": "...", "severity": "critical", "issue": "...", "suggestion": "..."}},
      ...
    ]
    
    If no issues, return: []
    """
    
    response = llm.invoke(audit_prompt).content
    
    # Parse response (with error handling)
    try:
        import json
        issues = json.loads(response)
        
        state.safety_flags = [
            SafetyFlag(
                line_num=i,
                severity=issue.get("severity", "low"),
                issue=issue.get("issue", ""),
                suggestion=issue.get("suggestion", "")
            )
            for i, issue in enumerate(issues)
        ]
        
        # Calculate safety score
        critical_count = sum(1 for f in state.safety_flags if f.severity == "critical")
        moderate_count = sum(1 for f in state.safety_flags if f.severity == "moderate")
        state.safety_score = max(0, 100 - (critical_count * 30 + moderate_count * 10))
        
    except json.JSONDecodeError:
        state.safety_flags = []
        state.safety_score = 100
    
    state.agent_notes.setdefault("safety_guardian", []).append(
        f"Audit complete. Safety score: {state.safety_score}. Issues: {len(state.safety_flags)}"
    )
    
    return state
