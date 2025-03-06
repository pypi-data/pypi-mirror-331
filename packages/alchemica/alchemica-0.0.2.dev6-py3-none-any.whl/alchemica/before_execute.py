import logging

from sqlalchemy import Connection, ClauseElement

from alchemica.log_explain_plan import log_explain_plan
from alchemica.utils.utils import compile_sql_query


def before_execute(
        conn: Connection,
        clauseelement: ClauseElement,
        logger: logging.Logger,
        compile_sql: bool,
        explain_plan: bool,
        execution_info: str,
):
    compiled_query = None
    if compile_sql:
        try:
            compiled_query = compile_sql_query(conn=conn, clauseelement=clauseelement)
            logger.info(f"🟢 [SQL]{execution_info} {compiled_query}")
        except Exception as err:
            logger.warning(f"⚠️ [SQL]{execution_info} Ошибка при компиляции запроса {err}")
    else:
        logger.info(f"🟢 [SQL]{execution_info} {clauseelement}")

    if explain_plan:
        try:
            log_explain_plan(
                conn=conn,
                compiled_query=compiled_query,
                clauseelement=clauseelement,
                logger=logger,
                execution_info=execution_info
            )
        except Exception as err:
            logger.warning(f"⚠️ [SQL PLAN]{execution_info} Ошибка при получении плана запроса {err}")
