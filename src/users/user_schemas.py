from pydantic import BaseModel


class CreateAdminResponse(BaseModel):
    status: bool
