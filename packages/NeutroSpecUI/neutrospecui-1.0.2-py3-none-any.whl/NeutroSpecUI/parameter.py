from dataclasses import dataclass
from typing import Generic, TypeVar

import numpy as np

T = TypeVar("T")


@dataclass
class Parameter(Generic[T]):
    value: T
    locked: bool = False
    bounds: tuple = (-np.inf, np.inf)
    name: str = "Parameter"

    def toggle(self) -> None:
        self.locked = not self.locked

    def get_bounds(self) -> tuple:
        return self.bounds
