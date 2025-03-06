import logging
import time
from typing import Optional


def after_execute(
        logger: logging.Logger,
        execution_info: str,
        sql_request_start_time: float,
        critical_time: Optional[float] = None,
):
    if sql_request_start_time is None:
        return
    elapsed_time = time.time() - sql_request_start_time
    logger.info(f"🕑️ [SQL]{execution_info} Выполнено за {elapsed_time:.4f} сек")
    if critical_time and elapsed_time > critical_time:
        logger.warning(
            f"⚠️ [SQL]{execution_info} Запрос выполнялся дольше {critical_time} секунд: {elapsed_time:.4f} сек"
        )
