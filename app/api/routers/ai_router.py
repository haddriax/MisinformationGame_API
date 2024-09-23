from api.routers.router_base import RouterBase
from fastapi import HTTPException
from sqlalchemy.exc import DBAPIError


class AiRouter(RouterBase):
    def configure_routes(self) -> None:
        @self.api_router.get("/new_study")
        async def generate_study_ai():
            from generators.OpenAI.study_generator import generate_study

            study = generate_study()
            try:
                self.logger.info("Attempting to insert study into the database.")
                self.app.database.insert_study(study)
                self.logger.info("Successfully inserted study into the database.")
            except study as e:
                self.logger.error(f"SQLAlchemy error occurred: {e}")
                raise HTTPException(status_code=500, detail={"SQLAlchemyError": str(e)})
            except DBAPIError as e:
                self.logger.error(f"Database API error occurred: {e}")
                raise HTTPException(status_code=500, detail={"DBAPIError": str(e)})
            except Exception as e:
                self.logger.error(f"Unexpected error during database insertion: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={"error": "Unexpected error", "message": str(e)},
                )
            return {"message": "success"}
