# from langchain_openai import ChatOpenAI
# from backend.state import CerinasState, DraftVersion
# from datetime import datetime
# from dotenv import load_dotenv
# load_dotenv()

# def drafter_node(state: CerinasState) -> CerinasState:
#     """
#     Drafter: Creates or improves CBT exercise drafts.
#     """
#     llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.7)
    
#     # Build context from feedback
#     feedback_context = ""
#     if state.safety_flags:
#         feedback_context += "\n## Safety Issues to Address:\n"
#         for flag in state.safety_flags:
#             feedback_context += f"- Line {flag.line_num}: {flag.issue}\n  Suggestion: {flag.suggestion}\n"
    
#     if state.clinical_feedback:
#         feedback_context += f"\n## Clinical Feedback:\n{state.clinical_feedback}\n"
    
#     # Prompt
#     prompt = f"""
#     User therapeutic goal: {state.user_intent}
    
#     {feedback_context}
    
#     Generate or improve a CBT exercise that:
#     1. Is structured (has clear sections: context, steps, reflection)
#     2. Is empathetic and non-judgmental
#     3. Is safe (no self-harm encouragement, no medical advice)
#     4. Directly addresses the therapeutic goal
    
#     Previous draft (if any):
#     {state.current_draft}
    
#     Provide the improved draft only, no explanations.
#     """
    
#     draft = llm.invoke(prompt).content
    
#     # Track version
#     version = DraftVersion(
#         version_num=len(state.draft_history) + 1,
#         content=draft,
#         created_at=datetime.utcnow(),
#         created_by="drafter",
#         notes=f"Iteration {state.iteration_count}"
#     )
#     state.draft_history.append(version)
#     state.current_draft = draft
#     state.agent_notes.setdefault("drafter", []).append(f"Draft v{version.version_num} created")
    
#     return state


from langchain_openai import ChatOpenAI
from backend.state import CerinasState, DraftVersion
from datetime import datetime


def drafter_node(state: CerinasState) -> CerinasState:
    """
    Drafter: Creates or improves CBT exercise drafts.
    
    Incorporates feedback from Safety Guardian and Clinical Critic.
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0.7
    )
    
    # Build context from feedback
    feedback_context = ""
    if state.safety_flags:
        feedback_context += "\n## Safety Issues to Address (CRITICAL):\n"
        for flag in state.safety_flags:
            feedback_context += f"- {flag.issue}\n  → Fix: {flag.suggestion}\n"
    
    # FIXED: Safely handle feedback as list or string
    clinical_feedback = state.clinical_feedback or ""
    if isinstance(clinical_feedback, list):
        clinical_feedback = " ".join([str(item) for item in clinical_feedback if item])
    if clinical_feedback and isinstance(clinical_feedback, str) and clinical_feedback.strip():
        feedback_context += f"\n## Clinical Feedback from Reviewer:\n{clinical_feedback}\n"
    
    previous_draft_context = ""
    if state.current_draft:
        previous_draft_context = f"\n\nPrevious draft (iteration {len(state.draft_history)}):\n{state.current_draft}\n\nImprove upon this, addressing all feedback above."
    
    prompt = f"""You are the Drafter Agent. Your role is to create safe, empathetic, and evidence-based CBT exercises.

THERAPEUTIC GOAL: {state.user_intent}

{feedback_context}

{previous_draft_context}

Generate a CBT exercise that:
1. ✓ Directly addresses the therapeutic goal
2. ✓ Is structured with clear sections (Context, Steps, Reflection)
3. ✓ Is warm and empathetic (non-judgmental tone)
4. ✓ Is safe (no self-harm encouragement, no medical advice)
5. ✓ Is actionable (client can actually do it)
6. ✓ Is evidence-based (follows CBT principles)

Return ONLY the exercise, no explanations or metadata."""
    
    draft = llm.invoke(prompt).content
    
    # Track version
    version = DraftVersion(
        version_num=len(state.draft_history) + 1,
        content=draft,
        created_at=datetime.utcnow(),
        created_by="drafter",
        notes=f"Iteration {state.iteration_count}"
    )
    state.draft_history.append(version)
    state.current_draft = draft
    
    state.agent_notes.setdefault("drafter", []).append(
        f"✍ Draft v{version.version_num} created (iteration {state.iteration_count})"
    )
    
    return state