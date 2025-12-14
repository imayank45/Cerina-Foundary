import asyncio
import json
import logging
from datetime import datetime
import uuid
from mcp.server import Server
from mcp.types import Tool, TextContent, ToolResult

from backend.graph import cerina_graph
from backend.state import CerinasState
from backend.database import db

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create MCP server
mcp_server = Server("cerina-foundry")


@mcp_server.tool()
async def generate_cbt_protocol(user_intent: str) -> ToolResult:
    """
    Generate a CBT exercise protocol autonomously.
    
    Args:
        user_intent: The therapeutic goal (e.g., "Exposure hierarchy for agoraphobia")
    
    Returns:
        Complete CBT protocol with safety and empathy metrics
    """
    try:
        thread_id = str(uuid.uuid4())
        
        # Create initial state
        initial_state = CerinasState(
            user_intent=user_intent,
            original_query=user_intent
        )
        
        # Run graph to completion (MCP skips human-in-loop)
        output = cerina_graph.invoke(initial_state)
        
        # Finalize without human approval for MCP
        output.human_approval = True
        output.status = "finalized"
        
        # Synthesize final protocol
        output = cerina_graph.invoke(output)
        
        # Format response
        result = {
            "status": "success",
            "thread_id": thread_id,
            "protocol": output.final_protocol or output.current_draft,
            "metrics": {
                "safety_score": round(output.safety_score, 1),
                "empathy_score": round(output.empathy_score, 1),
                "iterations": output.iteration_count,
                "safety_issues": len(output.safety_flags)
            },
            "timestamp": datetime.utcnow().isoformat()
        }
        
        # Save to DB
        db.save_protocol(thread_id, output)
        
        logger.info(f"Protocol generated: {thread_id}")
        
        return ToolResult(
            content=[TextContent(
                type="text",
                text=json.dumps(result, indent=2)
            )],
            is_error=False
        )
    
    except Exception as e:
        logger.error(f"Error generating protocol: {str(e)}")
        return ToolResult(
            content=[TextContent(
                type="text",
                text=json.dumps({"error": str(e), "status": "failed"})
            )],
            is_error=True
        )


@mcp_server.list_tools()
async def list_tools() -> list[Tool]:
    """List available tools."""
    return [
        Tool(
            name="generate_cbt_protocol",
            description="Generate a CBT exercise protocol based on a therapeutic intent. The system autonomously designs, critiques, and refines the exercise through multi-agent collaboration.",
            inputSchema={
                "type": "object",
                "properties": {
                    "user_intent": {
                        "type": "string",
                        "description": "The therapeutic goal or exercise type (e.g., 'Exposure hierarchy for agoraphobia', 'Sleep hygiene protocol', 'Thought record for anxiety')"
                    }
                },
                "required": ["user_intent"]
            }
        )
    ]


async def main():
    """Run MCP server via stdio."""
    async with mcp_server:
        logger.info("Cerina Foundry MCP server started on stdio")
        while True:
            await asyncio.sleep(1)


if __name__ == "__main__":
    asyncio.run(main())