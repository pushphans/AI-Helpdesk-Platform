from datetime import datetime
import uuid
from pydantic import BaseModel, Field

class CreateNotificationRequestSchema(BaseModel):
    message : str

class CreateNotificationResponseSchema(BaseModel):
    id : uuid.UUID
    user_id : uuid.UUID
    message : str
    is_read : bool
    created_at : datetime
    updated_at : datetime



class UpdateNotificationRequestSchema(BaseModel):
    is_read : bool = Field(...)

class UpdateNotificationResponseSchema(BaseModel):
    id : uuid.UUID
    user_id : uuid.UUID
    message : str
    is_read : bool
    created_at : datetime
    updated_at : datetime