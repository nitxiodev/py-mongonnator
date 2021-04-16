class BaseResponseWrapper:
    def operation(self, iterable: list):
        raise NotImplementedError("Implement in child classes")

    def __call__(self, iterable: list):
        """Make an operation to cursor/list"""
        return self.operation(iterable)


class AsIsWrapper(BaseResponseWrapper):
    """Wrapper to return response as is"""

    def operation(self, iterable: list):
        return iterable


class ChatWrapper(BaseResponseWrapper):
    """Wrapper to return response showing the most recent value at bottom"""

    def operation(self, iterable: list):
        return iterable[::-1]
