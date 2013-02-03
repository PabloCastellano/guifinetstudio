class GuifiApiError(Exception):
    def __init__(self, reason, code=0, extra=None):
        self.reason = reason
        self.code = int(code)
        self.extra = extra

    def __str__(self):
        return self.reason
