from ai_helpdesk_platform.notifications.router.notification_router import notification_router
from fastapi import status
from fastapi.responses import JSONResponse
from ai_helpdesk_platform.tickets.router.ticket_router import ticket_router
from ai_helpdesk_platform.auth.router.auth_router import auth_router
from fastapi import FastAPI

app = FastAPI()

app.include_router(auth_router)
app.include_router(ticket_router)
app.include_router(notification_router)

@app.get("/")
def root():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail" : "success"}
    )


@app.get("/health")
def health():
    return JSONResponse(
        status_code=status.HTTP_200_OK,
        content={"detail": "success"}
    )