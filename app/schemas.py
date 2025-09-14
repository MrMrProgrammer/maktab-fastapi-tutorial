from pydantic import BaseModel, constr, Field

class LoginRequest(BaseModel):
    username: constr(min_length=3)
    password: constr(min_length=6)
    lang: str = Field(default="en", description="Language code, e.g., 'en' or 'fa'")
