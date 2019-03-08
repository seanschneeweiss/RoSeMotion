class Configuration:
    def __init__(self):
        self.arguments = None
        self.parser = None
        pass

    def add_parser(self, parser):
        self.parser = parser

    def save_arguments(self, arguments):
        self.arguments = arguments

    @property
    def config(self):
        return self.parser.parse_args()

    @staticmethod
    def args(var):
        import sys
        arguments = sys.argv
        if var in arguments or "-" + var in arguments:
            return True
        return False


env = Configuration()
