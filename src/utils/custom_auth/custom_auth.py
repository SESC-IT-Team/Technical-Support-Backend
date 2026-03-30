# from sesc_auth_sdk.dependencies import LyceumAuth
#
#
from typing import Annotated, Optional, Union

from fastapi import Depends
from sesc_auth_sdk.dependencies import LyceumAuth
from sesc_auth_sdk.enums.role import Role
from src.enums import Role as CustomRole
from sesc_auth_sdk.schemas.user import UserSchema


class CustomAuth(LyceumAuth):
    def __init__(self, allowed_roles: Optional[list[Union[Role, CustomRole]]] = None):
        super().__init__(allowed_roles)

    async def __call__(self, current_user: Annotated[UserSchema, Depends(LyceumAuth._get_current_user)]):
        user = super().__call__(current_user)
