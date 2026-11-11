"""2/3 - Cena: monta objetos, anima, controla e renderiza."""

from math import pi, sin, cos
from pathlib import Path
import argparse
import random
import wave
import io

import numpy as np
import pygame

# Base do motor gráfico (cena, câmera, objetos, matrizes, malhas, texturas)
from core.base import Base
from core.camera import Camera
from core.matrix import Matrix
from core.mesh import Mesh
from core.object3D import Object3D
from core.scene import Scene
from core.texture import Texture
# Geometrias para montar os modelos
from geometry.boxGeometry import BoxGeometry
from geometry.octagonalPrism import OctagonalPrism
from geometry.rectangleGeometry import RectangleGeometry
# Iluminação e sombras
from lighting import ShadowRenderer, add_face_normals

IMAGES = Path(__file__).parent / "images"  # texturas

# Tempos das fases da animação (em segundos)
CLEAR_PATH_START = 4.0
CLEAR_PATH_END = 5.8
EXPLOSION = 8.0
LANDING = 9.25
SETTLE = 9.60
DURATION = 11.0


def progress(time, start, end):
    # Converte intervalo de tempo em progresso 0..1
    return max(0.0, min(1.0, (time - start) / (end - start)))


def smooth(value):
    # Suaviza transições (ease in-out)
    return value * value * (3 - 2 * value)


# Classe principal da cena (montagem, animação e controle)
class Battlefield(Base):
    def _make_sound(self, samples, sample_rate=44100):
        # Cria som (mono 16-bit) a partir de amostras numpy
        data = np.clip(samples, -1.0, 1.0)
        pcm = (data * 32767).astype(np.int16)
        buf = io.BytesIO()
        with wave.open(buf, 'wb') as wf:
            wf.setnchannels(1)
            wf.setsampwidth(2)
            wf.setframerate(sample_rate)
            wf.writeframes(pcm.tobytes())
        buf.seek(0)
        return pygame.mixer.Sound(buffer=buf.read())

    def _init_audio(self):
        # Inicializa áudio e gera sons simples (explosão e passo)
        self.audio_ok = False
        try:
            if not pygame.mixer.get_init():
                pygame.mixer.init(frequency=44100, size=-16, channels=1, buffer=512)
            sr = 44100
            # Explosão: ruído com decaimento
            t = np.linspace(0, 0.8, int(sr * 0.8), False)
            noise = np.random.uniform(-1, 1, t.size)
            env = np.exp(-4.5 * t)
            boom = (noise * env * 0.7 + 0.25 * np.sin(2 * np.pi * 70 * t) * np.exp(-6 * t))
            self.explosion_sound = self._make_sound(boom, sr)
            self.explosion_sound.set_volume(0.6)
            # Passo: impacto curto
            t = np.linspace(0, 0.09, int(sr * 0.09), False)
            env = np.exp(-45 * t)
            step = (0.6 * np.sin(2 * np.pi * 95 * t) + 0.25 * np.random.uniform(-1, 1, t.size)) * env
            self.step_sound = self._make_sound(step, sr)
            self.step_sound.set_volume(0.22)
            self.audio_ok = True
        except Exception:
            self.explosion_sound = None
            self.step_sound = None

    def initialize(self):
        """Inicializa renderizador, cena, câmera, materiais, objetos e áudio."""
        self.renderer = ShadowRenderer(self.screenSize)  # desenha cena com luz/sombras
        self.scene = Scene()  # grafo/contêiner de objetos 3D
        self.camera = Camera(angleOfView=51, aspectRatio=self.screenSize[0] / self.screenSize[1])  # câmera perspectiva
        # Estado da câmera (orientação e posição) + enquadramento inicial
        self.pitch, self.yaw = 0.105, 0.0
        self.cam_pos = np.array([0.55, 0.59, 7.4], dtype=np.float32)
        self.cam_home = (self.cam_pos.copy(), self.pitch, self.yaw)
        # Estado do tempo/animação
        self.time = 0.0
        self.paused = False
        self.previous_keys = set()

        # Geometrias base e materiais/cores (reutilizados nas peças)
        self.box = add_face_normals(BoxGeometry())
        self.prism = add_face_normals(OctagonalPrism())
        white = Texture(IMAGES / "branco.png")
        self.rng = random.Random(12345)  # RNG determinístico (útil para voltar/avançar o tempo)
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
        self.beetle_scale = 0.65
        self.exploded = False
        self.beetle_debris = []
        self.beetle_main_parts = []
        self.explosion_pos = None
        self.crater = None
        self._init_audio()
        self._step_cooldown = 0.0
        self.build_environment()
        self.build_beetle()
        self.build_drone()
        self.flash = self.part(self.scene, (7, 2, -2), (1, 1, 1), "fire")
        self.flash.casts_shadow = False
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
        # Monta cenário (chão texturizado e obstáculos)
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
        # Monta o besouro (hierarquia de partes)
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
        # tamanho reduzido
        self.beetle.scale(self.beetle_scale)
        self.beetle_main_parts = list(self.beetle.children)

    def build_drone(self):
        # Monta o drone (corpo e rotores)
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

    def _trigger_beetle_explosion(self):
        # Dispara explosão: separa peças do besouro e cria destroços
        if self.exploded:
            return
        self.exploded = True
        # Posição da explosão (a partir do drone)
        try:
            self.explosion_pos = np.array(self.drone.getWorldPosition(), dtype=np.float32)
        except Exception:
            self.explosion_pos = np.array([4.0, 2.0, -1.25], dtype=np.float32)
        # Cratera simples no chão
        if getattr(self, 'crater', None) is None:
            self.crater = self.part(self.scene, (float(self.explosion_pos[0]), 0.02, float(self.explosion_pos[2])),
                                    (1.8, 0.03, 1.3), "dark")
            self.crater.casts_shadow = False
        if getattr(self, 'audio_ok', False) and self.explosion_sound:
            self.explosion_sound.play()
        origin = np.array(self.beetle.getWorldPosition(), dtype=np.float32)
        parts = list(self.beetle_main_parts)
        for i, part in enumerate(parts):
            try:
                world = part.getWorldMatrix().copy()
            except Exception:
                continue
            try:
                if part.parent is not None:
                    part.parent.remove(part)
            except Exception:
                pass
            part.transform = world
            part.casts_shadow = False  # melhora desempenho na explosão
            self.scene.add(part)
            ang = (i / max(1, len(parts))) * 2 * pi + i * 0.8
            vel = np.array([
                -8.5 - 2.0 * (i % 4) + 1.0 * cos(ang),
                4.2 + 1.8 * ((i % 5) * 0.25) + 0.7 * abs(sin(ang)),
                -1.8 + 2.8 * sin(ang)
            ], dtype=np.float32)
            avel = np.array([
                (-1) ** i * (3.5 + i * 0.45),
                2.5 + (i % 5) * 0.6,
                (-1) ** (i + 1) * (3.0 + i * 0.35)
            ], dtype=np.float32)
            self.beetle_debris.append({"obj": part, "vel": vel, "avel": avel, "rest": 0.28, "settled": False})
        # alguns fragmentos extras
        for j in range(6):
            frag = self.part(self.scene, origin.copy(), (0.08 + 0.03*(j%3), 0.05 + 0.02*(j%2), 0.10 + 0.04*((j+1)%3)),
                             self.rng.choice(["steel", "dark", "alloy", "beetle"]))
            frag.setPosition((origin[0] + self.rng.uniform(-0.15, 0.15), origin[1] + self.rng.uniform(0.1, 0.4), origin[2] + self.rng.uniform(-0.15, 0.15)))
            frag.casts_shadow = False  # melhora desempenho na explosão
            ang = j * 0.75
            vel = np.array([
                -7.0 - self.rng.uniform(0, 4.0) + 1.2 * cos(ang),
                3.0 + self.rng.uniform(0, 3.5),
                self.rng.uniform(-3.0, 3.0)
            ], dtype=np.float32)
            avel = np.array([self.rng.uniform(-7, 7), self.rng.uniform(-7, 7), self.rng.uniform(-7, 7)], dtype=np.float32)
            self.beetle_debris.append({"obj": frag, "vel": vel, "avel": avel, "rest": 0.22, "settled": False})
        self.beetle.visible = False

    def _update_debris(self, dt):
        # Atualiza física simples dos destroços (gravidade/colisão/quique)
        g = -19.5
        dt = max(0.0, min(dt, 0.05))
        for d in self.beetle_debris:
            if d.get("settled"):
                continue
            obj = d["obj"]
            vel = d["vel"]
            avel = d["avel"]
            pos = obj.transform[:3, 3].copy()
            vel[1] += g * dt
            pos += vel * dt
            if pos[1] < 0.03:
                pos[1] = 0.03
                if vel[1] < 0:
                    vel[1] = -vel[1] * d.get("rest", 0.25)
                    vel[0] *= 0.78
                    vel[2] *= 0.78
                    avel *= 0.55
                if abs(vel[1]) < 0.3:
                    vel[1] = 0.0
                vel[0] *= 0.985
                vel[2] *= 0.985
                if abs(vel[0]) + abs(vel[2]) < 0.08 and np.linalg.norm(avel) < 0.25:
                    vel[:] = 0.0
                    avel[:] = 0.0
                    d["settled"] = True
            obj.transform[:3, 3] = pos
            if not d.get("settled"):
                rx = Matrix.makeRotationX(avel[0] * dt)
                ry = Matrix.makeRotationY(avel[1] * dt)
                rz = Matrix.makeRotationZ(avel[2] * dt)
                rot = (rx @ ry @ rz)[:3, :3]
                obj.transform[:3, :3] = rot @ obj.transform[:3, :3]
                avel *= (0.996 if pos[1] > 0.04 else 0.982)
            d["vel"] = vel
            d["avel"] = avel

    def animate(self):
        # Animação por tempo (fases do roteiro)
        t = self.time
        dodge = smooth(progress(t, CLEAR_PATH_START, CLEAR_PATH_END))
        scan = smooth(progress(t, 2.5, 3.3)) * (1 - smooth(progress(t, 3.6, 4.2)))

        # Explosão no tempo definido
        if t >= EXPLOSION and not self.exploded:
            self._trigger_beetle_explosion()

        # Movimento do besouro antes da explosão
        if not self.exploded:
            # comportamento original antes da explosão (sem arremesso/cambalhota do corpo inteiro)
            beetle_x = -2.4 + .56 * min(t, EXPLOSION)
            self.beetle.setPosition((beetle_x, 0.0, .72 * dodge))
            turn = .24 * scan - .37 * sin(pi * dodge)
            s = getattr(self, 'beetle_scale', 1.0)
            self.beetle.transform[:3, :3] = (Matrix.makeRotationY(turn) @ Matrix.makeRotationZ(0.0))[:3, :3] * s
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
        else:
            # Após explosão: atualiza destroços (se não estiver pausado)
            if not getattr(self, 'paused', False):
                self._update_debris(getattr(self, 'deltaTime', 1/60))

        # Movimento do drone e giro das hélices
        approach = smooth(progress(t, .2, 3.0))
        pass_by = smooth(progress(t, CLEAR_PATH_END, EXPLOSION))
        ref_x = (-2.4 + .56 * min(t, EXPLOSION)) if not self.exploded else (-2.4 + .56 * EXPLOSION)
        drone_x = ref_x - 5.8 + 4.85 * approach + 7.0 * pass_by  # aproxima um pouco para a explosão ficar visível
        self.drone.setPosition((drone_x, 1.92 + .10 * sin(3 * t) + .27 * pass_by, -1.25))
        for rotor, direction in self.rotors:
            rotor.transform[:3, :3] = Matrix.makeRotationY(direction * 26 * t)[:3, :3]
        for item in self.drone.getDescendantList():
            if isinstance(item, Mesh):
                item.visible = t < EXPLOSION

        # Efeito do clarão da explosão (a partir do drone)
        blast = progress(t, EXPLOSION, 9.0)
        self.flash.visible = EXPLOSION <= t < 9.0
        exp_pos = getattr(self, 'explosion_pos', None)
        if exp_pos is not None:
            self.flash.setPosition((float(exp_pos[0]), float(exp_pos[1] + 0.25 + blast * 0.35), float(exp_pos[2])))
        else:
            self.flash.setPosition((drone_x, 1.92 + .10 * sin(3 * t) + .27 * pass_by, -1.25))
        size = .35 + 3.2 * sin(pi * min(1.0, blast))
        self.flash.transform[:3, :3] = Matrix.makeRotationZ(blast * 1.5)[:3, :3] * size

    def _clear_dynamic(self):
        # limpa destroços e remove objetos dinâmicos (besouro/drone/flash)
        for d in getattr(self, 'beetle_debris', []):
            obj = d.get('obj')
            if obj and obj.parent is not None:
                try:
                    obj.parent.remove(obj)
                except Exception:
                    pass
        self.beetle_debris = []
        self.exploded = False
        for obj_name in ('beetle', 'drone', 'flash'):
            obj = getattr(self, obj_name, None)
            if obj and obj.parent is not None:
                try:
                    obj.parent.remove(obj)
                except Exception:
                    pass

    def _reset_sequence(self):
        # limpa destroços e reconstrói para reiniciar animação
        self._clear_dynamic()
        if hasattr(self, 'rng'):
            self.rng.seed(12345)
        self._step_cooldown = 0.0
        self.explosion_pos = None
        if getattr(self, 'crater', None) and self.crater.parent is not None:
            try:
                self.crater.parent.remove(self.crater)
            except Exception:
                pass
        self.crater = None
        self.build_beetle()
        self.build_drone()
        self.flash = self.part(self.scene, (7, 2, -2), (1, 1, 1), "fire")
        self.flash.casts_shadow = False
        self.time = 0.0
        self.animate()

    def _set_time(self, target):
        """Define o tempo da animação (permite voltar/avançar). Reconstrói estado quando necessário."""
        target = max(0.0, min(DURATION, float(target)))
        prev = getattr(self, 'time', 0.0)
        # voltar para antes da explosão ou saltos que exigem reconstrução
        if target < EXPLOSION:
            if self.exploded or target < prev:
                self._clear_dynamic()
                if hasattr(self, 'rng'):
                    self.rng.seed(12345)
                self._step_cooldown = 0.0
                self.explosion_pos = None
                if getattr(self, 'crater', None) and self.crater.parent is not None:
                    try:
                        self.crater.parent.remove(self.crater)
                    except Exception:
                        pass
                self.crater = None
                self.build_beetle()
                self.build_drone()
                self.flash = self.part(self.scene, (7, 2, -2), (1, 1, 1), "fire")
                self.flash.casts_shadow = False
            self.time = target
            self.animate()
            return
        # alvo >= EXPLOSION
        if not self.exploded:
            # avança até o momento da explosão e dispara estado de destroços
            self.time = EXPLOSION
            self.animate()  # dispara _trigger_beetle_explosion
        elif target < prev:
            # voltar no tempo após explosão: re-simula a partir da explosão
            self._clear_dynamic()
            if hasattr(self, 'rng'):
                self.rng.seed(12345)
            self._step_cooldown = 0.0
            self.explosion_pos = None
            if getattr(self, 'crater', None) and self.crater.parent is not None:
                try:
                    self.crater.parent.remove(self.crater)
                except Exception:
                    pass
            self.crater = None
            self.build_beetle()
            self.build_drone()
            self.flash = self.part(self.scene, (7, 2, -2), (1, 1, 1), "fire")
            self.flash.casts_shadow = False
            self.time = EXPLOSION
            self.animate()
        # simula destroços até o tempo alvo
        if self.exploded and target > EXPLOSION:
            dt = 1.0 / 60.0
            t = EXPLOSION
            while t < target - 1e-9:
                step = min(dt, target - t)
                self._update_debris(step)
                t += step
        self.time = target
        self.animate()

    def update(self):
        # Loop por quadro: entrada, tempo, animação e renderização
        dt = self.deltaTime
        # Teclas de ação (pausa, reinício, enquadrar)
        keys = {key for key in ("space", "r", "c") if self.isKeyPressed(key)}
        pressed = keys - self.previous_keys
        self.previous_keys = keys
        if "space" in pressed:
            self.paused = not self.paused
        if "r" in pressed:
            self._reset_sequence()
        if "c" in pressed:
            self.cam_pos, self.pitch, self.yaw = self.cam_home[0].copy(), self.cam_home[1], self.cam_home[2]
        # Controle da câmera (rotação e movimento)
        self.yaw += .8 * dt * (self.isKeyPressed("left") - self.isKeyPressed("right"))
        self.pitch += .8 * dt * (self.isKeyPressed("up") - self.isKeyPressed("down"))
        self.pitch = max(-1.2, min(1.2, self.pitch))

        move_speed = 2.2 * dt
        forward = np.array([sin(self.yaw), 0.0, -cos(self.yaw)], dtype=np.float32)
        right = np.array([cos(self.yaw), 0.0, sin(self.yaw)], dtype=np.float32)
        up = np.array([0.0, 1.0, 0.0], dtype=np.float32)
        if self.isKeyPressed("w"):
            self.cam_pos += forward * move_speed
        if self.isKeyPressed("s"):
            self.cam_pos -= forward * move_speed
        if self.isKeyPressed("a"):
            self.cam_pos -= right * move_speed
        if self.isKeyPressed("d"):
            self.cam_pos += right * move_speed
        if self.isKeyPressed("e"):
            self.cam_pos += up * move_speed
        if self.isKeyPressed("q"):
            self.cam_pos -= up * move_speed

        self.camera.transform = (
            Matrix.makeTranslation(float(self.cam_pos[0]), float(self.cam_pos[1]), float(self.cam_pos[2]))
            @ Matrix.makeRotationY(self.yaw)
            @ Matrix.makeRotationX(self.pitch)
        )

        # Controle do tempo (Z volta, X avança, ou roda normalmente)
        scrub_speed = 3.0  # segundos de vídeo por segundo
        if self.isKeyPressed("z"):
            self._set_time(self.time - scrub_speed * dt)
        elif self.isKeyPressed("x"):
            self._set_time(self.time + scrub_speed * dt)
        elif not self.paused:
            self._set_time(self.time + dt)
            # Passos simples do besouro (enquanto caminha)
            if getattr(self, 'audio_ok', False) and self.step_sound and not self.exploded and self.time < 7.8:
                self._step_cooldown -= dt
                if self._step_cooldown <= 0.0:
                    self.step_sound.play()
                    self._step_cooldown = 0.32
        else:
            self.animate()

        # Renderiza a cena
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
