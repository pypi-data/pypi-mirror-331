"""
This module contains the Vec3D class, which is a simple 3D vector class.
"""

from dataclasses import dataclass


@dataclass
class Vec3D:
    x: float
    y: float
    z: float

    def __add__(self, other):
        if not isinstance(other, Vec3D):
            raise TypeError(
                f"unsupported operand type(s) for +: {type(self)} and {type(other)}"
            )

        return Vec3D(self.x + other.x, self.y + other.y, self.z + other.z)

    def __sub__(self, other):
        if not isinstance(other, Vec3D):
            raise TypeError(
                f"unsupported operand type(s) for +: {type(self)} and {type(other)}"
            )

        return Vec3D(self.x - other.x, self.y - other.y, self.z - other.z)

    def __mul__(self, other):
        if not isinstance(other, (int, float)):
            raise TypeError(
                f"unsupported operand type(s) for *: {type(self)} and {type(other)}"
            )

        return Vec3D(self.x * other, self.y * other, self.z * other)

    def __truediv__(self, other):
        if not isinstance(other, (int, float)):
            raise TypeError(
                f"unsupported operand type(s) for /: {type(self)} and {type(other)}"
            )

        return Vec3D(self.x / other, self.y / other, self.z / other)

    def __str__(self):
        return f"({self.x}, {self.y}, {self.z})"

    def norm(self) -> float:
        return (self.x**2 + self.y**2 + self.z**2) ** 0.5

    def normalize(self) -> "Vec3D":
        n = self.norm()
        return Vec3D(self.x / n, self.y / n, self.z / n)
