from __future__ import annotations

import os
from typing import Type, ForwardRef

from dotenv import load_dotenv
from fastapi import FastAPI

from api.routers.router_base import RouterBase
from database.blob_storage import BlobStorage
from database.database import Database


class FastAPIWrapper:
    """
    FastAPIWrapper is a top-level class designed to initialize and manage the components of a FastAPI application. It
    includes functionality for database management, logging, and registering routers, making it a comprehensive
    solution for setting the FastAPI-based project.

    Attributes:
        fast_api (FastAPI): The FastAPI application instance.
        database (Database): The database instance.
        logger (logging.Logger): The general logger instance.
        blob_storage (BlobStorage): The blob storage instance.
        app_instance (FastAPI): The FastAPI application instance stored as a Class variable.
        _development_mode (bool): Indicates if the application is in development mode.

    Methods:
        __init__(development_mode: bool): Initializes the FastAPIWrapper instance.
        init_app(development_mode: bool = False) -> None: Create and initializes the components.
        build_routers() -> None: Builds and registers routers to the application.
        get_fastapi_instance() -> FastAPI: Returns the FastAPI application instance.
        get_db_url() -> str: Retrieves the database URL based on the current development mode.
        get_db_url_remote() -> str: Returns the database URL for a remote database connection.
        get_db_url_dev() -> str: Returns the development local database URL.
        get_app() -> FastAPI: Returns the FastAPI application instance.
        register_new_router(router_class: Type[RouterBase], tags: [], prefix="/"): Registers a new router.
        configure_routes() -> None: Configures routes for all routers.
        mount_routers() -> None: Mounts the routers on the FastAPI instance.
        run(host: str, port: int) -> None: Configures the routes, mounts the routers, and starts the server.
    """
    fast_api: FastAPI
    database: Database
    logger: ForwardRef("logging.Logger")
    blob_storage: BlobStorage = None
    app_instance: FastAPI = None
    # cloud_resources_accessor: CloudResourcesAccessor = None
    _development_mode: bool = True

    def __init__(self, development_mode: bool):
        from logger import build_logger

        self.logger = build_logger(
            __name__, "INFO" if not development_mode else "DEBUG"
        )

        try:
            from dotenv import find_dotenv
            dotenv_path = find_dotenv()
            if not dotenv_path:
                raise FileNotFoundError(".env file not found. Create a .env in the root directory.")

            # Load the .env file
            load_dotenv(dotenv_path)

        except FileNotFoundError as e:
            self.logger.error(".env file not found.")
            raise e
        except ValueError as e:
            self.logger.error(".env file not found")
            raise e
        except Exception as e:
            self.logger.error("An unexpected error occurred when loading .env file.")
            raise e

        FastAPIWrapper._development_mode = development_mode
        self.routers = {}

        self.init_app(development_mode)
        self.build_routers()

        assert (
                FastAPIWrapper.app_instance is None
        ), "Trying to create a second FastAPI application."
        FastAPIWrapper.app_instance = self

    def init_app(self, development_mode: bool = False) -> None:
        self.database = Database(self.get_db_url())

        if self._development_mode:
            self.database.generate_debug_test_user()

        blob_connection_string = os.getenv("BLOB_CONNECTION_STRING")

        self.blob_storage = BlobStorage(blob_connection_string)

        self.fast_api = FastAPI()

        # @todo start using the key vault + a debug mode that try to access without it
        # key_vault_url = "https://___.vault.azure.net/"
        # self.cloud_resources_accessor = CloudResourcesAccessor(key_vault_url)

    def build_routers(self):
        """
        Registers new routers to the application.

        :return: None
        """
        from api.routers.root_router import RootRouter

        self.register_new_router(RootRouter, "root", "")
        from api.routers.ai_router import AiRouter

        self.register_new_router(AiRouter, "ai", "/ai")
        from api.routers.study_router import StudyRouter

        self.register_new_router(StudyRouter, "study", "/study")
        from api.routers.login_router import LoginRouter

        self.register_new_router(LoginRouter, "login", "/login")
        from api.routers.run_study_router import RunStudyRouter

        self.register_new_router(RunStudyRouter, "run", "/running")

        from api.routers.result_router import ResultRouter

        self.register_new_router(ResultRouter, "results", "/result")

    @staticmethod
    def get_db_url() -> str:
        """
        Retrieve the database URL based on the current development mode.

        :return: The database URL to be used.
        :rtype: str
        """
        return (
            FastAPIWrapper.get_db_url_dev()
            if FastAPIWrapper._development_mode
            else FastAPIWrapper.get_db_url_remote()
        )

    @staticmethod
    def get_db_url_remote() -> str:
        """
        Return the database URL for a remote database connection.

        :return: The database URL for a remote database connection.
        :rtype: str
        """
        username = os.getenv("REMOTE_DB_USERNAME")
        password = os.getenv("REMOTE_DB_PASSWORD")
        host = os.getenv("REMOTE_DB_HOST")
        port = os.getenv("REMOTE_DB_PORT")
        db_name = os.getenv("REMOTE_DB_NAME")

        return f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{db_name}"

    @staticmethod
    def get_db_url_dev() -> str:
        """
        Returns the development local database URL.

        :return: The database URL for the development environment.
        :rtype: str
        """
        username = os.getenv("DEV_DB_USERNAME")
        password = os.getenv("DEV_DB_PASSWORD")
        host = os.getenv("DEV_DB_HOST")
        port = os.getenv("DEV_DB_PORT")
        db_name = os.getenv("DEV_DB_NAME")

        return f"mysql+mysqlconnector://{username}:{password}@{host}:{port}/{db_name}"

    @staticmethod
    def get_app() -> FastAPI:
        return FastAPIWrapper.app_instance

    def register_new_router(self, router_class: Type[RouterBase], tags: [], prefix="/"):
        """
        Register router by inserting them in the routers dictionary.
        The created key for the dict is the name of the class, avoiding class duplicate.

        :param router_class: The class of the router to be registered. Used as key for the Dict.
        @todo Verify that the tags are passed correctly to the router.
        :param tags: The list of tags associated with the router.
        :param prefix: The prefix URL for the router.
        :return: The newly registered router object.

        """
        try:
            # Check if the router already exists.
            if self.routers.get(router_class.__name__) is not None:
                raise KeyError(
                    "The key {key} for inserting the router has already been registered for the router "
                    "{existing_router}.".format(
                        key=router_class.__name__,
                        existing_router=self.routers.get(
                            router_class.__name__
                        ).__class__.__name__,
                    )
                )
            else:
                # If it doesn't already exist, create it and insert it.
                self.routers[router_class.__name__] = router_class(self, tags, prefix)
        except KeyError as e:
            self.logger.error(
                f"Router {router_class.__name__} is already registered - {e}"
            )
        else:
            self.logger.info(f"Registering new router: {router_class.__name__}")

        return self.routers[router_class.__name__]

    def configure_routes(self) -> None:
        """
        Configure routes for all routers in the self.routers dictionary.

        :return: None
        """
        for router in self.routers.values():
            router.configure_routes()

    def mount_routers(self) -> None:
        """
        Mounts the routers from the self.routers dictionary on the FastAPI instance.

        :return: None
        """
        for router in self.routers.values():
            self.fast_api.include_router(
                router.api_router, prefix=router.prefix, tags=[router.prefix]
            )

    def run(self, host: str, port: int) -> None:
        """
        Configures the routes, mounts the routers, and starts the server using Uvicorn.

        :return: None
        """

        from fastapi.middleware.cors import CORSMiddleware

        # @todo the middleware should be secured!
        # noinspection PyTypeChecker
        self.fast_api.add_middleware(
            CORSMiddleware,
            allow_origins=["*"],
            allow_credentials=True,
            allow_methods=["*"],
            allow_headers=["*"],
        )

        self.configure_routes()
        self.mount_routers()
        import uvicorn

        try:
            uvicorn.run(self.fast_api, host=host, port=port)
        except OSError as e:
            # Example: if the port is already used...
            self.logger.error(f"Failed to start server: {str(e)}")
            raise e
        except KeyboardInterrupt:
            self.logger.info("Server has been stopped manually.")
        except Exception as e:
            self.logger.error(
                f"Unexpected error occurred during server startup: {str(e)}"
            )
            raise e
