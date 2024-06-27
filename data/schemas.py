from pydantic import BaseModel

class ProfileCreate(BaseModel):
    name: str

class Profile(BaseModel):
    id: int

class Auth(BaseModel):
    email: str
    password: str

class AuthCreate(BaseModel):
    email: str
    password: str
    role: str

class Book(BaseModel):
    flight: int
    places: list[int]
