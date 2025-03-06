import logging
from contextvars import ContextVar
from functools import wraps
from time import time
from typing import Optional

from sqlalchemy import event
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

from alchemica.after_execute import after_execute
from alchemica.before_execute import before_execute
from alchemica.utils.default_logger import default_logger
from alchemica.utils.sqlalchemy_patch import patch_sqlalchemy_for_multithreading
from alchemica.utils.utils import get_uuid, atime

__all__ = ["async_sql_logger", ]

execution_context_var = ContextVar("execution_context_var")
sql_request_start_time_var = ContextVar("execution_start_time_var")
execution_info_var = ContextVar("execution_info_var")

patch_sqlalchemy_for_multithreading()


def async_sql_logger(
        logger: logging.Logger = default_logger,
        log_level: int = logging.INFO,
        log_execution_info: bool = True,
        compile_sql: bool = False,
        critical_time: Optional[float] = 1,
        explain_plan: bool = False,
        uuid_len: int = 6,
):
    logger.setLevel(log_level)

    def decorator(func):
        @wraps(func)
        async def wrapper(*args, **kwargs):
            def _before_execute(conn, clauseelement, multiparams, params, execution_options):  # noqa
                if execution_context_var.get(None) != func_uuid:
                    return
                if str(clauseelement).startswith("EXPLAIN"):
                    return
                query_uuid = get_uuid(uuid_len=uuid_len)
                if log_execution_info:
                    execution_info = f"(func_name: {func_name}; func_uuid: {func_uuid}; query_uuid: {query_uuid})"
                else:
                    execution_info = ""
                execution_info_var.set(execution_info)
                before_execute(
                    conn=conn,
                    clauseelement=clauseelement,
                    logger=logger,
                    compile_sql=compile_sql,
                    explain_plan=explain_plan,
                    execution_info=execution_info
                )
                sql_request_start_time_var.set(time())

            def _after_execute(conn2, clauseelement, multiparams, params, execution_options, result):  # noqa
                if execution_context_var.get(None) != func_uuid:
                    return
                if str(clauseelement).startswith("EXPLAIN"):
                    return
                execution_info = execution_info_var.get(None)
                sql_request_start_time = sql_request_start_time_var.get()
                after_execute(
                    critical_time=critical_time,
                    logger=logger,
                    execution_info=execution_info,
                    sql_request_start_time=sql_request_start_time,
                )

            func_uuid = get_uuid(uuid_len=uuid_len)
            previous_execution_context_var = execution_context_var.get(None)
            execution_context_var.set(func_uuid)

            # sync_engine = func.__globals__['engine'].sync_engine
            sync_engine = Engine
            event.listen(sync_engine, "before_execute", _before_execute)
            event.listen(sync_engine, "after_execute", _after_execute)

            func_name = func.__name__
            if log_execution_info:
                func_execution_info = f"(func_name: {func_name}; func_uuid: {func_uuid})"
            else:
                func_execution_info = ""

            func_start_time = await atime()
            logger.info(f"🚀 [FUNC]{func_execution_info} запущена")
            try:
                func_result = await func(*args, **kwargs)
                current_time = await atime()
                elapsed_time = current_time - func_start_time
                logger.info(f"✅ [FUNC]{func_execution_info} выполнена за {elapsed_time:.4f} сек")
            except SQLAlchemyError as err:
                logger.exception(f"❌ [SQL ERROR]{func_execution_info} {str(err)}")
                raise err
            except Exception as err:
                logger.exception(f"❌ [FUNC ERROR]{func_execution_info} {func_name} {str(err)}")
                raise err
            finally:
                execution_context_var.set(previous_execution_context_var)

                event.remove(sync_engine, "before_execute", _before_execute)
                event.remove(sync_engine, "after_execute", _after_execute)
            return func_result

        return wrapper

    return decorator
