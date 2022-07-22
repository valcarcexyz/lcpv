from .utils import base


class EdgeProcessor(base.LcpvTemplate):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


if __name__ == "__main__":
    ep = EdgeProcessor()
