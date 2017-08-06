from imports.config import Config


class ATC:
    config = Config()

    def __init__(self):
        self.config.load()
        

if __name__ == "__main__":
    ATC()
