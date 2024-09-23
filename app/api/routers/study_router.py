from typing import Any, Dict, List, Tuple

from azure.core.exceptions import AzureError, ResourceNotFoundError
from fastapi import Body, HTTPException
from fastapi.params import Depends
from pydantic import BaseModel, ValidationError
from sqlalchemy.exc import DBAPIError, SQLAlchemyError

from api.routers.router_base import RouterBase
from database.commands.database_to_json import convert_study
from database.commands.json_to_database import get_study_by_id
from database.models.db_model import Comment, Post
from database.models.json_study_models import JSONStudyModel


class UpdateStudyModel(BaseModel):
    id: int
    enabled: str
    last_modified_time: str


class StudyRouter(RouterBase):
    @staticmethod
    def sort_raw_posts_comments_dict(
            posts_comments_dict: dict[str, Any],
    ) -> dict[str, Tuple[Post, List[Comment]]]:
        """
        Sorts a dictionary containing posts and comments based on their relationships.
        Requires "posts" and "comments" keys.

        :param posts_comments_dict: A dictionary containing "posts" key with a list of posts and "comments" key
        with a list of comments.
        :return: A sorted dictionary where each key being a post id and its value is a tuple containing the post itself
        and a list of comments.
        """
        ordered_dict = {}
        posts = posts_comments_dict["posts"]

        for comment in posts_comments_dict["comments"]:
            # Checking if there is already an entry for this post in the Dictionary
            p = ordered_dict.get(comment.fk_linked_post)

            if p is None:
                # No entry? Creating it with the post id as Key, and a tuple as value containing:
                # The Post owning this comment, from the Posts list created earlier.
                # A new list with the comment.
                ordered_dict[comment.fk_linked_post] = (
                    posts[comment.fk_linked_post],
                    [comment],
                )
            else:
                # Entry already exist? Simply append the comment to the comment list.
                p[1].append(comment)
        return ordered_dict

    async def query_study_as_json(self, db_id: str) -> JSONStudyModel:

        """
        Query a study from the database by its study ID and return it as a JSONStudyModel.

        :param db_id: The ID of the study to query.
        :return: The study as a JSONStudyModel.
        """

        study = await get_study_by_id(self.app.database, db_id)

        if study is None:
            raise HTTPException(status_code=404, detail="Study not found")

        # Getting the raw values of study's comments and posts from the database
        raw_values = await self.app.database.query_study_comments_and_posts_raw(study.id)

        # Ordering the raw values of study's comments and posts
        ordered_dict = self.sort_raw_posts_comments_dict(raw_values)

        # Converting the study object to JSONStudyModel and return it
        return convert_study(study, ordered_dict, raw_values["sources"])

    def configure_routes(self) -> None:
        from database.blob_storage import ImageBase64

        @self.api_router.post("/upload-base64-image")
        async def upload_base64_image(image: ImageBase64):
            # @todo Change the way of getting the container_name and item_name. Hardcoded and too prone to errors.
            # Exactly, this line (List Comprehension):
            # 1) Create a list named components.
            # 2) Split the 'path' string into a string array using'/' as separator, and iterate on its elements.
            # 2.1) Do not keep empty string, remove empty strings resulting from leading "/".
            # 3) Insert array entries to the list.
            components = [component for component in image.path.split("/") if component]
            container_name = str(components[2]).lower()
            item_name = components[3]

            # Attempt to upload the image given in parameter to the app blob storage.
            try:
                uploaded_item_url = await self.app.blob_storage.upload_image_to_blob(
                    container_name=container_name, item_name=item_name, image64=image
                )
                self.logger.info(f"Uploaded an image at {uploaded_item_url}")
                return {"url": uploaded_item_url}
            except ResourceNotFoundError:
                raise HTTPException(status_code=404, detail="Container not found")
            except AzureError:
                raise HTTPException(status_code=500, detail="Azure error occurred")
            except Exception as e:
                self.logger.error(f"Unexpected error: {e}")
                raise HTTPException(
                    status_code=500, detail="An unexpected error occurred"
                )

        @self.api_router.post("/upload")
        async def read_json_file(json_content: dict = Body(...)):
            """
            :param json_content: The JSON content to be processed and used to build a study.
            :return: None

            This method reads and validates the provided JSON content, builds a study from it, and inserts the study
            into the database.

            The JSON content should be a dictionary representing the study in a specific format.

            The method follows the following steps:

            Step 1: Read and validate JSON content: - The JSON content is validated against a specific model called
            JSONStudyModel. - If the validation fails, a JSON validation error is logged, and an HTTPException with a
            status code of 422 and the validation errors is raised.

            Step 2: Build study from JSON: - The study is built from the validated JSON content using the
            `build_study_from_json` method. - If there are any validation errors during the building process,
            they are logged, and an HTTPException with a status code of 422 and the validation errors is raised. - If
            any unexpected errors occur during the building process, they are logged, and an HTTPException with a
            status code of 500, an error message, and the encountered exception is raised.

            Step 3: Insert study into the database: - The built study is inserted into the database using the
            `insert_study` method of the app's database. - If any SQLAlchemy errors occur during the insertion
            process, they are logged, and an HTTPException with a status code of 500 and the SQLAlchemy error is
            raised. - If any database API errors occur during the insertion process, they are logged,
            and an HTTPException with a status code of 500 and the database API error is raised. - If any unexpected
            errors occur during the insertion process, they are logged, and an HTTPException with a status code of
            500, an error message, and the encountered exception is raised.
            """
            from database.commands.json_to_database import \
                build_study_from_json

            study_formatted = None

            # Step 1: Read and validate JSON content
            try:
                self.logger.info("Starting validation of JSON content.")
                validated_content_json = JSONStudyModel(**json_content)
                self.logger.info("Successfully validated JSON content.")
            except ValidationError as e:
                self.logger.error(f"JSON validation error: {e}")
                raise HTTPException(status_code=422, detail=e.errors())

            # Step 2: Build study from JSON
            try:
                self.logger.info("Starting to build study from JSON.")
                study_formatted = build_study_from_json(validated_content_json)
            except ValidationError as e:
                self.logger.error(f"Validation error while building study: {e}")
                raise HTTPException(status_code=422, detail=e.errors())
            except AttributeError as e:
                self.logger.error(f"Attribute error during study build: {e}")
                raise HTTPException(status_code=422, detail=e)
            except Exception as e:
                self.logger.error(f"Unexpected error during study build: {e}")
                raise HTTPException(
                    status_code=500,
                    detail={"error": "Unexpected error", "message": str(e)},
                )
            else:
                self.logger.info("Successfully built study from JSON.")

            # Step 3: Insert study into the database
            try:
                self.logger.info("Attempting to insert study into the database.")
                await self.app.database.insert_study(study_formatted)
                self.logger.info("Successfully inserted study into the database.")
            except SQLAlchemyError as e:
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

            return {"message": "Success"}

        @self.api_router.get("/get/{study_id}")
        async def get_study(study_id: str) -> JSONStudyModel:
            """
            :param study_id: The ID of the study to retrieve.
            :return: The study converted to a JSON Object with the specified ID,
            along with associated comments, posts, and sources.

            """
            return await self.query_study_as_json(study_id)

        @self.api_router.get("/all")
        async def get_all_studies() -> List[JSONStudyModel]:
            """
            Get all studies from the database.
            Used for legacy application, but is very costly.

            # @todo Create a version that query one at a time to avoid a HUGE query? + pagination system + Study Light version.

            :return: A list of JSONStudyModel objects representing the studies.
            """
            studies = await self.app.database.get_all_studies()
            json_studies = []

            # Return an empty list when there is no Study to query.
            if len(studies) == 0:
                return []

            # For every study that we queried, recover the posts, comments and source to build it into a single JSON
            # file per study.
            for study in studies:
                raw_values = await self.app.database.query_study_comments_and_posts_raw(study.id)
                ordered_dict = self.sort_raw_posts_comments_dict(raw_values)

                # Attempt to convert the data we queried from the database to a JSON object.
                try:
                    self.logger.info("Starting to build study from JSON.")
                    json_study = convert_study(
                        study, ordered_dict, raw_values["sources"]
                    )
                except ValidationError as e:
                    self.logger.error(
                        f"Validation error while convert_study study: {e}"
                    )
                    raise HTTPException(status_code=422, detail=e.errors())
                except AttributeError as e:
                    self.logger.error(f"Attribute error during convert_study: {e}")
                    raise HTTPException(status_code=422, detail=e)
                except Exception as e:
                    self.logger.error(f"Unexpected error during convert_study: {e}")
                    raise HTTPException(
                        status_code=500,
                        detail={"error": "Unexpected error", "message": str(e)},
                    )
                else:
                    # If no exception were raised, add this study to the list containing all the studies
                    json_studies.append(json_study)
                    self.logger.info("Successfully built study from JSON.")

            return json_studies

        @self.api_router.put("/enable")
        async def update_study(values=Body(...),
                               database=Depends(self.get_database)
                               ) -> Dict[str, str]:
            try:
                await database.update_study_enabled(values)
                return {"message": "Success"}
            except Exception as e:
                raise HTTPException(status_code=500, detail={'error': 'Unexpected error', 'message': str(e)}) from e

        @self.api_router.delete("/delete/{study_id}")
        async def delete_study(study_id: str,
                               database=Depends(self.get_database)) -> Dict[str, str]:
            try:
                self.logger.info(f"Route for deletion of study {study_id}.")
                await database.delete_study(study_id)
                return {"message": "Success"}
            except Exception as e:
                raise HTTPException(
                    status_code=500,
                    detail={"error": "Unexpected error", "message": str(e)},
                )
