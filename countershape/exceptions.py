import state

class ApplicationError(Exception):
    def __init__(self, msg):
        Exception.__init__(self, msg)
        self.page = state.page
