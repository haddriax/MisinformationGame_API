from api.routers.router_base import RouterBase
from database.commands.participants_queries import \
    count_participant_finished_by_study


class DashboardRouter(RouterBase):
    def configure_routes(self) -> None:
        @self.api_router.post("/{study_id}")
        async def get_studies(study_id: str):
            # get studies

            db = self.app.database
            participant_count = await count_participant_finished_by_study(db, study_id)
            # count the completed participants

            return {"message": "Successfull", "participant_count": participant_count}
