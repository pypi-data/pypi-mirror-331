from ..callbacks import CallbackContext

class CallbackMixin:
    """
    Implements callbacks and nothing else
    """
    
    def __init__(self, callback_ids: list):
        # holds all callbacks based on their ids
        self._callbacks: dict[str, list] = {}
        self._init_callbacks(callback_ids)

    def _init_callbacks(self, callback_ids: list, strict: bool = True):
        for id in callback_ids:
            if id in self._callbacks.keys() and strict:
                raise ValueError(
                    f"callback_id=\"{id}\" alredy not exist, available: {list(self._callbacks.keys())}."
                )
            self._callbacks.update({id: []})
    
    def validate_callback_id(self, callback_id):
        if callback_id not in self._callbacks.keys():
            raise ValueError(
                f"Callback with id=\"{callback_id}\" does not exist, available: {list(self._callbacks.keys())}."
            )

    def add_callback(self, calllback_id: str, fn):
        self.validate_callback_id(calllback_id)
        self._callbacks[calllback_id].append(fn)

    def _run_callbacks(self, context: CallbackContext):
        if context.is_cancelled():
            return False, context.get_result()

        callback_id = context.get_callback_id()
        self.validate_callback_id(callback_id)

        for fn in self._callbacks[callback_id]:
            fn(context) # function modifies context in-place
            if context.is_cancelled():
                return False, context.get_result()
        
        return True, context.get_result()