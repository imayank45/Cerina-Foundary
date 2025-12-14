from langgraph.graph import StateGraph, END
from backend.state import CerinasState
from backend.agents.supervisor import supervisor_node
from backend.agents.drafter import drafter_node
from backend.agents.safety_guardian import safety_guardian_node
from backend.agents.clinical_critic import clinical_critic_node
from backend.agents.synthesizer import synthesizer_node
from backend.database import db


def build_graph():
    graph = StateGraph(CerinasState)

    graph.add_node("supervisor", supervisor_node)
    graph.add_node("drafter", drafter_node)
    graph.add_node("safety_guardian", safety_guardian_node)
    graph.add_node("clinical_critic", clinical_critic_node)
    graph.add_node("synthesizer", synthesizer_node)

    graph.add_edge("supervisor", "drafter")
    graph.add_edge("drafter", "safety_guardian")
    graph.add_edge("safety_guardian", "clinical_critic")

    def route_after_critique(state: CerinasState) -> str:
        if state.halted_for_human:
            return "synthesizer"
        else:
            return "supervisor"

    graph.add_conditional_edges(
        "clinical_critic",
        route_after_critique,
        {"synthesizer": "synthesizer", "supervisor": "supervisor"},
    )

    graph.add_edge("synthesizer", END)
    graph.set_entry_point("supervisor")

    # IMPORTANT: compile with db.checkpointer
    return graph.compile(checkpointer=db.checkpointer)


cerina_graph = build_graph()
