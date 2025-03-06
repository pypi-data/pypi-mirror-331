from sqlalchemy.engine.base import Connection


def _invoke_before_exec_event(
        self,
        elem,
        distilled_params,
        execution_options,
):
    from sqlalchemy import exc

    if len(distilled_params) == 1:
        event_multiparams, event_params = [], distilled_params[0]
    else:
        event_multiparams, event_params = distilled_params, {}

    for fn in list(self.dispatch.before_execute):
        elem, event_multiparams, event_params = fn(
            self,
            elem,
            event_multiparams,
            event_params,
            execution_options,
        )

    if event_multiparams:
        distilled_params = list(event_multiparams)
        if event_params:
            raise exc.InvalidRequestError(
                "Event handler can't return non-empty multiparams "
                "and params at the same time"
            )
    elif event_params:
        distilled_params = [event_params]
    else:
        distilled_params = []

    return elem, distilled_params, event_multiparams, event_params


def patch_connection_invoke_before_exec_event():
    Connection._invoke_before_exec_event = _invoke_before_exec_event
