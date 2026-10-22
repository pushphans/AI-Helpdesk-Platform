from datetime import datetime
from uuid import UUID
from pydantic import Field
from pydantic import EmailStr
from pydantic import BaseModel



class RegisterRequestSchema(BaseModel):
    name : str
    email : EmailStr
    password : str =  Field(..., min_length=6)



class RegisterResponseSchema(BaseModel):
    user_id : UUID
    name : str
    email : str
    created_at : datetime
    updated_at : datetime



class LoginRequestSchema(BaseModel):
    email : EmailStr
    password : str


class LoginResponseSchema(BaseModel):
    user_id : UUID
    name : str
    email : str
    access_token : str
    refresh_token : str
    access_token_expiry : int
    created_at : datetime
    updated_at : datetime



class RefreshTokenRequestSchema(BaseModel):
    refresh_token : str

class RefreshTokenResponseModel(BaseModel):
    user_id : UUID
    access_token : str
    refresh_token : str
    access_token_expiry : int
    created_at : datetime
    updated_at : datetime