from logging import Logger
from typing import List

from fastapi import APIRouter


class RouterBase:
    """
    A base router class to inherit from for handling routes.

    Attributes:
        api_router (APIRouter): The APIRouter object used for defining routes.
        prefix (str): The prefix path for all routes defined in the router.
        tags (list): The list of tags associated with the router.
        logger (Logger): The logger object for logging router actions.

    Methods:
        configure_routes(): Configures the routes for the router. The method that should be overridden.
    """

    __abstract__ = True

    api_router: APIRouter = None
    prefix: str
    tags: List = []
    logger: Logger

    def __init__(self, api_object, tags: [], prefix="/"):
        self.api_router = APIRouter()
        self.prefix = prefix
        self.tags = tags
        self.app = api_object
        from logger import build_logger

        # Build a logger with the class, or child class name.
        self.logger = build_logger(self.__class__.__name__, "INFO")

    def get_database(self):
        # Dependency function to retrieve the database connection
        return self.app.database

    def configure_routes(self):
        pass
