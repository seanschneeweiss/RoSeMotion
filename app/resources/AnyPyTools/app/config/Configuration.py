class Configuration:
    def __init__(self):
        self.arguments = None
        pass

    def save_arguments(self, arguments):
        self.arguments = arguments

    @property
    def config(self):
        return self.arguments


env = Configuration()
