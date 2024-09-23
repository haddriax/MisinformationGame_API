from typing import List, Any

from fastapi import Body, HTTPException
from pydantic import ValidationError
from sqlalchemy import select, desc
from sqlalchemy.exc import DBAPIError, SQLAlchemyError

from api.routers.router_base import RouterBase
from database.models.db_model import StudyResultFile, Study
from database.models.json_result_models import JSONResultModel


class ResultRouter(RouterBase):
    """
    This class is responsible for configuring routes related to the handling of study results (query and upload).

    Attributes
    ----------
    self.api_router : APIRouter
        The API router for handling HTTP requests.
    """

    def get_study_results_from_db(self, study_id: str) -> List[JSONResultModel]:
        """
        Retrieves all study results for a given study ID from the database.

        :param self: The instance of the ResultRouter class.
        :param study_id: The ID of the study.
        :return: A list of JSONResultModel objects representing the study results.
        """
        self.logger.info(f"Trying to retrieve all study results for study ID: {study_id}...")
        with self.app.database.session() as session:
            req = select(StudyResultFile).where(StudyResultFile.fk_study_ID == study_id)
            results = session.execute(req)
            study_results = results.scalars().all()
            return [entry.data for entry in study_results]

    def configure_routes(self) -> None:
        """
        :return: None

        """
        @self.api_router.post("/upload")
        async def upload_study_result(json_content: dict = Body(...)):
            """
            :param json_content: A dictionary containing the study result data in JSON format.
            :return: Dict:
                "message" indicating whether the study result was uploaded successfully.
                "entry_id" the primary key that the object will occupy in the database.

            This method is used to upload a study result to the database. The study result data is provided as a JSON
            object in the `json_content` parameter. The method performs the following steps:

            :raise HTTPException
            If any validation error, SQLAlchemy error, or DBAPI error occurs during the process, an HTTPException
            with a status code of 400 and a detailed error message is raised.
            """
            with self.app.database.session(True) as db_session:
                try:
                    # 1. Create an instance of the `JSONResultModel` class using the `json_content` dictionary.
                    study_data_json = JSONResultModel(**json_content)

                    # 2. Create an instance of the `StudyResultFile` class and populate its properties with data from
                    # the json_content` dictionary.
                    result = StudyResultFile(
                        id=self.app.database.generate_uuid(),
                        fk_study_ID=study_data_json.studyID,
                        study_mod_time=study_data_json.studyModTime,
                        session_ID=study_data_json.sessionID,
                        study_start_time=study_data_json.startTime,
                        study_end_time=study_data_json.endTime,
                        data=json_content,
                    )

                    # Uploading object to database.
                    db_session.add(result)
                    return {
                        "message": "Study result uploaded successfully",
                        "entry_id": result.id,
                    }
                except ValidationError as e:
                    self.logger.error(f"ValidationError error occurred: {e}")
                    raise HTTPException(status_code=422, detail=str(e)) from e
                except (SQLAlchemyError, DBAPIError) as e:
                    self.logger.error(f"An API error occurred: {e}")
                    raise HTTPException(status_code=400, detail=str(e)) from e
                except Exception as e:
                    self.logger.error(f"An unexpected error occurred: {e}")
                    raise HTTPException(status_code=500, detail=str(e)) from e

        @self.api_router.post("/get_all_from_latest")
        async def get_all_study_results_from_latest():
            with self.app.database.session() as session:
                req = select(Study).order_by(desc(Study.created_at)).limit(1)
                result = session.execute(req)
                study = result.scalars().one_or_none()
                self.logger.info(f"Study result: {study}" if study is not None else "No Study results")

                if study is None:
                    return None
                else:
                    return self.get_study_results_from_db(study.id)

        from pydantic import BaseModel
        class StudyResultsAll(BaseModel):
            data: List[JSONResultModel]

        @self.api_router.post("/get_all/{study_id}")
        async def get_all_study_results(study_id: str) -> dict[str, Any]:
            """
            Retrieve all study results for a given study ID.

            :param study_id: The ID of the study.
            :return: A list of study results.
            """
            try:
                self.logger.info(f"Trying to retrieve all study results for study ID: {study_id}...")
                results = self.get_study_results_from_db(study_id)
                return StudyResultsAll(data=results).model_dump()
            except Exception as e:
                self.app.logger.error(f"Failed to fetch study results: {str(e)}")
                raise HTTPException(status_code=500, detail="Failed to fetch study results") from e
