from database.database import Database

"""
 in this async function they setup an database session.
the Participant model from db_model.py  is imported
in the query they retrieve Participant instances that match the conditions of Linked study and the finish time
Finally counts the retrieved participants that match the conditions
returns as an variable called result
"""


async def count_participant_finished_by_study(database: Database, study_id: str) -> int:
    with database.session() as session:
        from database.models.db_model import Participant

        result = (
            session.query(Participant)
            .filter(Participant.fk_linked_study == study_id)
            .filter(Participant.game_finish_time is not None)
            .count()
        )

    return result
