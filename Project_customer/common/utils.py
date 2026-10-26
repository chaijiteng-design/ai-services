from datetime import UTC, datetime
from uuid import uuid4


def get_uid(prefix: str) -> str:
    '''
    Generate a unique id with the given prefix.
    :param prefix: The prefix of the uid.
    :return: The unique id.
    '''
    return f"{prefix}_{uuid4().hex}"


def get_utcnow() -> datetime:
    '''
    Get the current UTC time.
    :return: The current UTC time.
    '''
    return datetime.now(UTC)
