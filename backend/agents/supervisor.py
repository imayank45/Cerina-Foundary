# from langchain_openai import ChatOpenAI
# from backend.state import CerinasState
# from dotenv import load_dotenv
# load_dotenv()

# def supervisor_node(state: CerinasState) -> CerinasState:
#     """
#     Supervisor: Routes tasks to agents, decides on halts and loops.
#     """
#     llm = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    
#     if state.iteration_count == 0:
#         # Initial parse
#         response = llm.invoke(f"""
#         User intent: {state.user_intent}
        
#         Understand the user's therapeutic goal. Set the stage for drafting.
#         Respond with: READY_TO_DRAFT
#         """)
#         state.agent_notes.setdefault("supervisor", []).append(f"Parsed intent: {state.user_intent}")
#         state.status = "drafting"
#     else:
#         # Decision point: loop or halt?
#         has_critical_safety_issues = any(
#             flag.severity == "critical" for flag in state.safety_flags
#         )
#         has_clinical_feedback = bool(state.clinical_feedback)
        
#         if (has_critical_safety_issues or has_clinical_feedback) and state.iteration_count < state.max_iterations:
#             # Route back to drafter for improvements
#             state.agent_notes.setdefault("supervisor", []).append(
#                 f"Iteration {state.iteration_count}: Routing back to Drafter"
#             )
#             state.status = "drafting"
#         else:
#             # Halt for human
#             state.halted_for_human = True
#             state.status = "halted"
#             state.agent_notes.setdefault("supervisor", []).append(
#                 f"Halting for human review at iteration {state.iteration_count}"
#             )
    
#     state.iteration_count += 1
#     return state


from langchain_openai import ChatOpenAI
from backend.state import CerinasState


def supervisor_node(state: CerinasState) -> CerinasState:
    """
    Supervisor: Orchestrates task routing and halts.
    
    Decides:
    - On iteration 0: Parse intent and route to drafter
    - On subsequent iterations: Decide to loop or halt
    """
    llm = ChatOpenAI(
        model="gpt-4o-mini",
        temperature=0
    )
    
    if state.iteration_count == 0:
        # Initial parse
        prompt = f"""
You are the Supervisor Agent for a CBT exercise generation system.

User therapeutic goal: {state.user_intent}

Your role is to:
1. Understand the therapeutic intent
2. Ensure the goal is clear and achievable
3. Set the stage for a thorough drafting process

Respond with: READY_TO_DRAFT

User intent: {state.user_intent}
"""
        response = llm.invoke(prompt)
        
        state.agent_notes.setdefault("supervisor", []).append(
            f"✓ Parsed intent: '{state.user_intent}' - Ready to draft"
        )
        state.status = "drafting"
    else:
        # Decision point: loop or halt?
        has_critical_safety_issues = any(
            flag.severity == "critical" for flag in state.safety_flags
        )
        
        # FIXED: Safely handle clinical_feedback (list or string)
        clinical_feedback = state.clinical_feedback or ""
        if isinstance(clinical_feedback, list):
            clinical_feedback = " ".join([str(item) for item in clinical_feedback if item])
        elif not isinstance(clinical_feedback, str):
            clinical_feedback = ""
        
        # Strip safely only if it's a string
        has_clinical_feedback = bool(clinical_feedback.strip()) if clinical_feedback else False
        
        if (has_critical_safety_issues or has_clinical_feedback) and state.iteration_count < state.max_iterations:
            # Route back to drafter for improvements
            state.agent_notes.setdefault("supervisor", []).append(
                f"↻ Iteration {state.iteration_count}: Critical issues found. Routing to Drafter for improvements"
            )
            state.status = "drafting"
        else:
            # Halt for human review
            state.halted_for_human = True
            state.status = "halted"
            state.agent_notes.setdefault("supervisor", []).append(
                f"⏸ Max iterations ({state.iteration_count}) reached or no further improvements needed. Halting for human review"
            )
    
    state.iteration_count += 1
    return state