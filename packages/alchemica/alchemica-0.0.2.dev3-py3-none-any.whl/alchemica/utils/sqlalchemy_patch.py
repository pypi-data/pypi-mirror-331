import threading

from sqlalchemy.engine.base import Connection
from sqlalchemy.event.attr import _CompoundListener

lock = threading.Lock()


def patch_sqlalchemy_connection_invoke_before_exec_event():
    def _invoke_before_exec_event(
            self,
            elem,
            distilled_params,
            execution_options,
    ):
        from sqlalchemy import exc

        with lock:
            distilled_params = list(distilled_params)

        if len(distilled_params) == 1:
            event_multiparams, event_params = [], distilled_params[0]
        else:
            event_multiparams, event_params = distilled_params, {}

        with lock:
            self_dispatch_before_execute = list(self.dispatch.before_execute)

        for fn in self_dispatch_before_execute:
            elem, event_multiparams, event_params = fn(
                self,
                elem,
                event_multiparams,
                event_params,
                execution_options,
            )

        if event_multiparams:
            with lock:
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

    Connection._invoke_before_exec_event = _invoke_before_exec_event


def patch_sqlalchemy_compound_listener__call__():
    def patched_call(self, *args, **kw):
        with lock:
            parent_listeners_copy = list(self.listeners)
        for fn in parent_listeners_copy:
            fn(*args, **kw)
        with lock:
            listeners_copy = list(self.listeners)
        for fn in listeners_copy:
            fn(*args, **kw)

    _CompoundListener.__call__ = patched_call


def patch_sqlalchemy_for_multithreading():
    patch_sqlalchemy_connection_invoke_before_exec_event()
    patch_sqlalchemy_compound_listener__call__()
