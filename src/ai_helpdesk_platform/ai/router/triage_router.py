from ai_helpdesk_platform.ai.service.triage_service import run_workflow
from ai_helpdesk_platform.ai.schema.triage_schemas import TriageAgentRequestSchema
from fastapi import APIRouter, HTTPException

triage_router = APIRouter(prefix="/ai", tags=["AI"])

@triage_router.post("/tickets/")
async def execute_run_workflow(
    data : TriageAgentRequestSchema
):
    result = await run_workflow(data=data)
    return result