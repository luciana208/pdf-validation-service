"""contador de requests en curso, lo informa el health check"""


class InFlightCounter:
    def __init__(self) -> None:
        self._count = 0

    @property
    def count(self) -> int:
        return self._count

    def increment(self) -> None:
        self._count += 1

    def decrement(self) -> None:
        self._count -= 1


in_flight = InFlightCounter()
