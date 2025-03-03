class DomainException(Exception):
    def __init__(
        self,
        detail: str = "Domain exception has occured.",
    ):
        super().__init__(detail)
