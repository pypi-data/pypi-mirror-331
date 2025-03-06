import uuid

from sqlalchemy import Connection, ClauseElement


def compile_sql_query(
        conn: Connection,
        clauseelement: ClauseElement,
):
    compiled_query = clauseelement.compile(
        dialect=conn.dialect,
        compile_kwargs={"literal_binds": True}  # Подставляем реальные значения
    )
    return compiled_query


def get_uuid(uuid_len: int = 6) -> str:
    result = uuid.uuid4().hex[-uuid_len:]
    return result


async def atime():
    import asyncio
    result = asyncio.get_event_loop().time()
    return result
