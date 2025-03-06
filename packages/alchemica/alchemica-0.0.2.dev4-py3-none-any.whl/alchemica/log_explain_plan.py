import logging

from sqlalchemy import Connection, text, ClauseElement

from alchemica.utils.utils import compile_sql_query


def get_explain_plan(
        conn: Connection,
        compiled_query,
):
    explain_query = text(f"EXPLAIN {compiled_query}")
    result = conn.execute(explain_query)
    plan = list(result.fetchall())
    plan = "\n".join(" ".join(str(i) for i in row) for row in plan)
    return plan


def log_explain_plan(
        conn: Connection,
        compiled_query,
        clauseelement: ClauseElement,
        logger: logging.Logger,
        execution_info: str,
):
    if compiled_query is None:
        compiled_query = compile_sql_query(conn=conn, clauseelement=clauseelement)
    plan = get_explain_plan(conn=conn, compiled_query=compiled_query)
    logger.info(f"📝 [SQL PLAN]{execution_info} \n{plan}")
