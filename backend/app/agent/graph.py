from langgraph.graph import StateGraph, END
from langgraph.constants import Send
from app.agent.state import AgentState
from app.agent.nodes import (
    loader_node, 
    extractor_node, 
    decision_node, 
    fill_pdf_node, 
    wait_node
)

def continue_to_extract(state: AgentState):
    """
    Map step: Generates a Send object for each document in the state.
    This triggers parallel execution of the 'extractor' node.
    """
    documents = state.get("documents", [])
    # We map the 'extractor' node to each document
    # The 'extractor' node expects a dict with a 'doc' key
    return [Send("extractor", {"doc": d}) for d in documents]

def decide_next_step(state: AgentState):
    """
    Determines the next node based on the decision state.
    """
    decision = state.get("decision")
    if decision == "REQUEST_MORE":
        return "wait_for_input"
    return "fill_pdf"

# Initialize Graph
workflow = StateGraph(AgentState)

# Add Nodes
workflow.add_node("loader", loader_node)
workflow.add_node("extractor", extractor_node)
workflow.add_node("decision", decision_node)
workflow.add_node("fill_pdf", fill_pdf_node)
workflow.add_node("wait_for_input", wait_node)

# Set Entry Point
workflow.set_entry_point("loader")

# Add Edges

# 1. Loader -> [Map] -> Extractor
# The conditional edge returns a list of Send objects, creating parallel branches
workflow.add_conditional_edges("loader", continue_to_extract, ["extractor"])

# 2. Extractor -> Decision
# All parallel extractor branches merge back into 'decision'.
# The 'extracted_data' state is aggregated automatically via operator.add
workflow.add_edge("extractor", "decision")

# 3. Decision -> [Branch] -> Wait OR Fill
workflow.add_conditional_edges("decision", decide_next_step, {
    "wait_for_input": "wait_for_input",
    "fill_pdf": "fill_pdf"
})

# 4. Wait -> Loader (Cycle)
# When the user provides input (resumes), we loop back to loader
workflow.add_edge("wait_for_input", "loader")

# 5. Fill -> End
workflow.add_edge("fill_pdf", END)

from langgraph.checkpoint.memory import MemorySaver

# Compile the graph
# We use a MemorySaver to persist state between steps (critical for the wait_for_input cycle)
checkpointer = MemorySaver() 
graph = workflow.compile(checkpointer=checkpointer)
