from database.models.db_model import Study
from sqlalchemy import event
from sqlalchemy.pool import Pool


@event.listens_for(Study, "after_insert")
def function_called_after_insert(mapper, connection, target):
    print("Study [{}] inserted".format(target.id))


@event.listens_for(Pool, "connect")
def my_on_connect(dbapi_con, connection_record):
    print("New DBAPI connection:", dbapi_con)
