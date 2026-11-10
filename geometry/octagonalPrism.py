from math import cos, pi, sin

from geometry.geometry import Geometry


class OctagonalPrism(Geometry):
    """Prisma unitário com o eixo longitudinal em Z."""

    def __init__(self):
        super().__init__()
        ring = [
            (0.5 * cos(pi / 8 + index * pi / 4),
             0.5 * sin(pi / 8 + index * pi / 4))
            for index in range(8)
        ]
        positions = []
        for index, (x, y) in enumerate(ring):
            next_x, next_y = ring[(index + 1) % 8]
            back = (x, y, -0.5)
            next_back = (next_x, next_y, -0.5)
            front = (x, y, 0.5)
            next_front = (next_x, next_y, 0.5)
            positions.extend([back, next_back, next_front, back, next_front, front])
            positions.extend([(0, 0, -0.5), next_back, back])
            positions.extend([(0, 0, 0.5), front, next_front])

        self.addAttribute("vec3", "vertexPosition", positions)
        self.addAttribute("vec2", "vertexUV", [(0, 0)] * len(positions))
        self.countVertices()
