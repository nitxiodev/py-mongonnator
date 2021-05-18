class BaseResponseWrapper:
    def __init__(self, iterable: list):
        self._iterable = iterable

    def format(
        self,
    ):
        raise NotImplementedError("Implement in child classes")


class DefaultResponseWrapper(BaseResponseWrapper):
    """Wrapper to return response as is"""

    def format(
        self,
    ):
        return self._iterable


class ChatResponseWrapper(BaseResponseWrapper):
    """Wrapper to return response showing the most recent value at bottom"""

    def format(
        self,
    ):
        return self._iterable[::-1]
