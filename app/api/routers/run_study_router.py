from api.routers.router_base import RouterBase


class RunStudyRouter(RouterBase):
    def configure_routes(self) -> None:
        @self.api_router.get("/{study_id}")
        async def get_posts_selection():
            """
            :return: A dictionary containing the selected posts.
            """
            # Get the study

            # Check the settings

            # Recover the post selection methods

            # Return the list of selected Posts

            return {"message": "test login route"}
