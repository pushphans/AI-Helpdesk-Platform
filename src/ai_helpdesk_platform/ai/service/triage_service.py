from ai_helpdesk_platform.ai.schema.triage_schemas import TriageAgentResponseSchema
from ai_helpdesk_platform.ai.ticket_triage_agent.workflow import workflow
from ai_helpdesk_platform.ai.ticket_triage_agent.state import AgentState
from ai_helpdesk_platform.ai.schema.triage_schemas import TriageAgentRequestSchema
async def run_workflow(
    data : TriageAgentRequestSchema
):

    initial_state : AgentState = {
        "title" : data.title,
        "description" : data.description,
        "status" : data.status,
        "priority" : data.priority
    }

    final_state : AgentState = await workflow.ainvoke(initial_state)

    return TriageAgentResponseSchema(
        category=final_state["category"],
        suggested_priority=final_state["suggested_priority"],
        summary=final_state["summary"],
        suggested_reply=final_state["suggested_reply"]
    ) 
