from api.routers.router_base import RouterBase


class RootRouter(RouterBase):
    def configure_routes(self) -> None:
        @self.api_router.get("/")
        async def default_route():
            return "A test to check that the page is working as it should."
