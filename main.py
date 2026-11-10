from math import pi, sin
from pathlib import Path
import argparse

import numpy as np

from core.base import Base
from core.camera import Camera
from core.matrix import Matrix
from core.mesh import Mesh
from core.object3D import Object3D
from core.scene import Scene
from core.texture import Texture
from geometry.boxGeometry import BoxGeometry
from geometry.octagonalPrism import OctagonalPrism
from geometry.rectangleGeometry import RectangleGeometry
from lighting import ShadowRenderer, add_face_normals

IMAGES = Path(__file__).parent / "images"
CLEAR_PATH_START = 4.0
CLEAR_PATH_END = 5.8
EXPLOSION = 8.0
LANDING = 9.25
SETTLE = 9.60
DURATION = 11.0


def progress(time, start, end):
    return max(0.0, min(1.0, (time - start) / (end - start)))


def smooth(value):
    return value * value * (3 - 2 * value)


class Battlefield(Base):
    def initialize(self):
        self.renderer = ShadowRenderer(self.screenSize)
        self.scene = Scene()
        self.camera = Camera(angleOfView=51, aspectRatio=self.screenSize[0] / self.screenSize[1])
        self.pitch, self.yaw = 0.105, 0.0
        self.time = 0.0
        self.paused = False
        self.previous_keys = set()

        self.box = add_face_normals(BoxGeometry())
        self.prism = add_face_normals(OctagonalPrism())
        white = Texture(IMAGES / "branco.png")
        self.materials = {
            name: self.renderer.material(white, color)
            for name, color in {
                "steel": (0.40, 0.48, 0.48),
                "dark": (0.14, 0.18, 0.19),
                "beetle": (0.87, 0.39, 0.12),
                "alloy": (0.65, 0.72, 0.76),
                "marking": (0.96, 0.74, 0.26),
                "eye": (0.45, 0.94, 0.88),
                "drone": (0.61, 0.63, 0.32),
                "fire": (1.0, 0.59, 0.12),
            }.items()
        }
        self.build_environment()
        self.build_beetle()
        self.build_drone()
        self.flash = self.part(self.scene, (7, 2, -2), (1, 1, 1), "fire")
        self.animate()

    def node(self, parent, position):
        node = Object3D()
        node.setPosition(position)
        parent.add(node)
        return node

    def part(self, parent, position, dimensions, color, geometry=None):
        mesh = Mesh(self.box if geometry is None else geometry, self.materials[color])
        mesh.setPosition(position)
        mesh.applyMatrix(np.diag([*dimensions, 1]))
        parent.add(mesh)
        return mesh

    def build_environment(self):
        earth = Texture(IMAGES / "terra.png")
        floor = Mesh(add_face_normals(RectangleGeometry(54, 48)),
                     self.renderer.material(earth, (1, 1, 1), (19, 17)))
        floor.rotateX(-pi / 2)
        floor.casts_shadow = False
        self.scene.add(floor)
        for x, z, height in [(-5, -6, .8), (-3.5, -6, .5), (4, -7, 1.2), (5.4, -7, .65)]:
            wall = self.part(self.scene, (x, height / 2, z), (1.4, height, .65), "dark")
            wall.rotateY(.12)

    def build_beetle(self):
        self.beetle = self.node(self.scene, (0, 0, 0))
        self.part(self.beetle, (-.17, .67, 0), (1.47, .43, .94), "dark")
        # Duas placas facetadas com uma abertura ao centro, como os élitros.
        for side in (-1, 1):
            plate = self.node(self.beetle, (-.30, .89, side * .28))
            plate.rotateY(pi / 2)
            self.part(plate, (0, 0, 0), (.57, .45, 1.27), "beetle", self.prism)
            for x in (-.59, .46):
                self.part(plate, (-side * .26, .06, x), (.065, .085, .085),
                          "alloy", self.prism)
            for x in (-.22, 0, .22):
                self.part(plate, (-side * .266, -.08, x), (.045, .045, .13), "dark")

        self.part(self.beetle, (.47, .84, 0), (.30, .34, .84), "steel")
        self.part(self.beetle, (.73, .73, 0), (.43, .34, .58), "dark")
        self.part(self.beetle, (.96, .75, 0), (.14, .23, .42), "alloy")
        self.legs, self.antennas = [], []
        for side in (-1, 1):
            lens = self.node(self.beetle, (1.045, .76, side * .115))
            lens.rotateY(pi / 2)
            self.part(lens, (0, 0, 0), (.14, .14, .08), "dark", self.prism)
            self.part(lens, (0, 0, .05), (.09, .09, .04), "eye", self.prism)

            antenna = self.node(self.beetle, (.80, .87, side * .22))
            self.part(antenna, (0, 0, 0), (.16, .16, .18), "alloy", self.prism)
            mast = self.node(antenna, (0, .06, 0))
            mast.rotateZ(-.69)
            self.part(mast, (0, .14, 0), (.09, .28, .09), "dark")
            self.part(mast, (0, .36, 0), (.055, .31, .055), "alloy")
            self.part(mast, (0, .53, 0), (.10, .12, .10), "eye")
            self.antennas.append((antenna, side))

            for index, x in enumerate((-.72, -.19, .32)):
                pivot = self.node(self.beetle, (x, .61, side * .38))
                self.part(pivot, (0, 0, side * .07), (.29, .29, .22), "steel", self.prism)
                joint = self.node(pivot, (0, 0, side * .09))
                joint.rotateX(side * .35)
                self.part(joint, (0, 0, side * .19), (.14, .12, .38), "dark")
                # Camisa e haste do atuador aparente, paralelas à coxa.
                self.part(joint, (.10, .07, side * .12), (.09, .09, .23),
                          "alloy", self.prism)
                self.part(joint, (.10, .07, side * .28), (.048, .048, .16),
                          "alloy", self.prism)
                knee = self.node(joint, (0, 0, side * .38))
                knee.rotateX(-side * .60)
                self.part(knee, (0, 0, side * .04), (.22, .22, .20), "steel", self.prism)
                self.part(knee, (0, 0, side * .15), (.105, .105, .055),
                          "marking", self.prism)
                self.part(knee, (0, -.20, 0), (.13, .40, .13), "dark")
                self.part(knee, (.055, -.24, side * .08), (.08, .29, .085), "alloy")
                self.part(knee, (.06, -.41, 0), (.24, .10, .16), "steel")
                self.legs.append((pivot, index + (side > 0)))

    def build_drone(self):
        self.drone = self.node(self.scene, (0, 0, 0))
        self.part(self.drone, (0, 0, 0), (.75, .24, .61), "drone")
        self.part(self.drone, (.30, -.13, 0), (.28, .21, .23), "eye")
        self.rotors = []
        for x in (-1, 1):
            for z in (-1, 1):
                self.part(self.drone, (x * .43, 0, z * .28), (.74, .10, .12), "steel")
                self.part(self.drone, (x * .77, 0, z * .45), (.13, .10, .45), "steel")
                self.part(self.drone, (x * .77, .10, z * .64), (.26, .21, .26), "dark")
                rotor = self.node(self.drone, (x * .77, .25, z * .64))
                self.part(rotor, (0, 0, 0), (.85, .055, .10), "steel")
                self.rotors.append((rotor, x * z))

    def animate(self):
        t = self.time
        dodge = smooth(progress(t, CLEAR_PATH_START, CLEAR_PATH_END))
        scan = smooth(progress(t, 2.5, 3.3)) * (1 - smooth(progress(t, 3.6, 4.2)))
        flight = progress(t, EXPLOSION, LANDING)
        bounce = progress(t, LANDING, SETTLE)
        # O impulso começa com o clarão. O deslocamento para trás diminui até o pouso.
        launch_distance = 1.48 * (1 - (1 - flight) ** 2) + .14 * bounce
        beetle_x = -2.4 + .56 * min(t, EXPLOSION) - launch_distance
        beetle_height = 6.4 * flight * (1 - flight) + .76 * bounce * (1 - bounce)
        self.beetle.setPosition((beetle_x, beetle_height, .72 * dodge))
        # Gira quando já está longe do chão e volta com as patas para baixo.
        tumble = smooth(progress(flight, .12, .86))
        pitch = 2 * pi * tumble - .10 * sin(pi * bounce)
        turn = .24 * scan - .37 * sin(pi * dodge)
        self.beetle.transform[:3, :3] = (
            Matrix.makeRotationY(turn) @ Matrix.makeRotationZ(pitch)
        )[:3, :3]
        for leg, phase in self.legs:
            stride = 1 - progress(t, 7.8, EXPLOSION)
            angle = .40 * sin(9 * t + phase * pi) * stride
            leg.transform[:3, :3] = (
                Matrix.makeRotationY(angle) @ Matrix.makeRotationZ(.21 * abs(angle / .4))
            )[:3, :3]
        for antenna, side in self.antennas:
            antenna.transform[:3, :3] = (
                Matrix.makeRotationY(.32 * scan + .13 * sin(5 * t + side))
                @ Matrix.makeRotationX(side * (.24 + .28 * sin(6 * t + side)))
            )[:3, :3]

        approach = smooth(progress(t, .2, 3.0))
        pass_by = smooth(progress(t, CLEAR_PATH_END, EXPLOSION))
        drone_x = beetle_x - 5.8 + 4.85 * approach + 10.5 * pass_by
        self.drone.setPosition((drone_x, 1.92 + .10 * sin(3 * t) + .27 * pass_by, -1.25))
        for rotor, direction in self.rotors:
            rotor.transform[:3, :3] = Matrix.makeRotationY(direction * 26 * t)[:3, :3]
        for item in self.drone.getDescendantList():
            if isinstance(item, Mesh):
                item.visible = t < EXPLOSION
        # O clarão começa na borda direita e entra brevemente no enquadramento.
        blast = progress(t, EXPLOSION, 8.55)
        self.flash.visible = EXPLOSION <= t < 8.55
        self.flash.setPosition((6.35, 1.9 + blast * .5, -.55))
        size = .25 + 1.9 * sin(pi * blast)
        self.flash.transform[:3, :3] = Matrix.makeRotationZ(blast * 1.3)[:3, :3] * size

    def update(self):
        dt = self.deltaTime
        keys = {key for key in ("space", "r", "c") if self.isKeyPressed(key)}
        pressed = keys - self.previous_keys
        self.previous_keys = keys
        if "space" in pressed:
            self.paused = not self.paused
        if "r" in pressed:
            self.time = 0.0
        if "c" in pressed:
            self.pitch, self.yaw = .105, 0
        self.yaw += .8 * dt * (self.isKeyPressed("left") - self.isKeyPressed("right"))
        self.pitch += .8 * dt * (self.isKeyPressed("up") - self.isKeyPressed("down"))
        self.pitch = max(-1.2, min(1.2, self.pitch))
        self.camera.transform = (
            Matrix.makeTranslation(.55, .59, 7.4)
            @ Matrix.makeRotationY(self.yaw)
            @ Matrix.makeRotationX(self.pitch)
        )
        if not self.paused:
            self.time = min(DURATION, self.time + dt)
        self.animate()
        self.renderer.render(self.scene, self.camera)


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--frames", type=int)
    parser.add_argument("--screenshot")
    parser.add_argument("--compat-display", action="store_true",
                        help="Exibe o quadro via janela SDL por software.")
    args = parser.parse_args()
    app = Battlefield(title="Campo de batalha | Besouro mecanico e drone",
                      compat_display=args.compat_display)
    app.run(args.frames, args.screenshot)
