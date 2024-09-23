from api.routers.router_base import RouterBase
from fastapi import HTTPException, status
from pydantic import BaseModel


class CredentialsDTO(BaseModel):
    username: str
    password: str


class LoginRouter(RouterBase):
    def configure_routes(self) -> None:
        @self.api_router.post("/")
        async def login(credentials: CredentialsDTO):
            from database.commands.user_db import select_user_by_username

            user = select_user_by_username(self.app.database, credentials.username)

            if user and user.check_password(credentials.password):
                return user
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid username or password",
                )

        @self.api_router.get("/{user_id}")
        async def get_user_by_id(user_id: str):
            from database.commands.user_db import select_user_by_id

            user = select_user_by_id(self.app.database, user_id)

            if user:
                return user
            else:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="The user does not exist.",
                )
