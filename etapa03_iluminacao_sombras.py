"""3/3 - Iluminação e sombras (shadow mapping)."""
from pathlib import Path

import numpy as np
from OpenGL.GL import *

from core.matrix import Matrix
from core.mesh import Mesh
from core.renderer import Renderer
from material.material import Material

SHADERS = Path(__file__).parent / "shaders"  # pasta dos shaders GLSL


def shader_material(name):
    # Carrega e cria material a partir dos shaders .vert/.frag
    return Material(
        (SHADERS / f"{name}.vert").read_text(),
        (SHADERS / f"{name}.frag").read_text(),
    )


def add_face_normals(geometry):
    """Calcula normais por face (usadas na iluminação)."""
    triangles = np.asarray(geometry.attributes["vertexPosition"].data, dtype=np.float32).reshape(-1, 3, 3)
    normals = np.cross(triangles[:, 1] - triangles[:, 0], triangles[:, 2] - triangles[:, 0])
    normals /= np.linalg.norm(normals, axis=1, keepdims=True)
    geometry.addAttribute("vec3", "vertexNormal", np.repeat(normals, 3, axis=0))
    return geometry


class ShadowRenderer(Renderer):
    SIZE = 1024  # resolução do mapa de sombra

    def __init__(self, screen_size):
        super().__init__([0.43, 0.51, 0.58])
        self.screen_size = screen_size
        # Direção da luz (luz direcional)
        direction = np.array([-5.0, 9.0, 5.0])
        self.to_light = direction / np.linalg.norm(direction)

        # Matriz da "câmera da luz" (projeção ortográfica)
        right = np.cross([0, 1, 0], self.to_light)
        right /= np.linalg.norm(right)
        up = np.cross(self.to_light, right)
        light_pose = Matrix.makeIdentity()
        light_pose[:3, :3] = np.column_stack([right, up, self.to_light])
        light_pose[:3, 3] = self.to_light * 15
        ortho = np.diag([1 / 11, 1 / 11, -2 / 32, 1])
        ortho[2, 3] = -1
        self.light_matrix = ortho @ np.linalg.inv(light_pose)

        # Textura/framebuffer para o mapa de profundidade (sombra)
        self.depth_texture = glGenTextures(1)
        glBindTexture(GL_TEXTURE_2D, self.depth_texture)
        glTexImage2D(GL_TEXTURE_2D, 0, GL_DEPTH_COMPONENT24, self.SIZE, self.SIZE,
                     0, GL_DEPTH_COMPONENT, GL_FLOAT, None)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MIN_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_MAG_FILTER, GL_NEAREST)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_S, GL_CLAMP_TO_EDGE)
        glTexParameteri(GL_TEXTURE_2D, GL_TEXTURE_WRAP_T, GL_CLAMP_TO_EDGE)

        self.framebuffer = glGenFramebuffers(1)
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebuffer)
        glFramebufferTexture2D(GL_FRAMEBUFFER, GL_DEPTH_ATTACHMENT,
                               GL_TEXTURE_2D, self.depth_texture, 0)
        glDrawBuffer(GL_NONE)
        glReadBuffer(GL_NONE)
        if glCheckFramebufferStatus(GL_FRAMEBUFFER) != GL_FRAMEBUFFER_COMPLETE:
            raise RuntimeError("Falha ao configurar o mapa de sombras.")
        glBindFramebuffer(GL_FRAMEBUFFER, 0)

        # Material do passe de profundidade (1º passe)
        self.depth_material = shader_material("depth")
        self.depth_material.addUniform("mat4", "lightMatrix", self.light_matrix)
        self.depth_material.locateUniforms()
        self.depth_vaos = {}

    def material(self, texture, color, repeat=(1, 1)):
        # Material da cena (textura/cor/luz/sombra) para o 2º passe
        material = shader_material("scene")
        material.addUniform("mat4", "lightMatrix", self.light_matrix)
        material.addUniform("vec3", "toLight", self.to_light)
        material.addUniform("vec3", "baseColor", color)
        material.addUniform("vec2", "repeatUV", repeat)
        material.addUniform("vec2", "texel", [1 / self.SIZE] * 2)
        material.addUniform("sampler2D", "surfaceImage", [texture.textureRef, 0])
        material.addUniform("sampler2D", "shadowMap", [self.depth_texture, 1])
        material.locateUniforms()
        return material

    def render(self, scene, camera):
        # 1º passe: desenha profundidade a partir da luz (gera mapa de sombra)
        glBindFramebuffer(GL_FRAMEBUFFER, self.framebuffer)
        glViewport(0, 0, self.SIZE, self.SIZE)
        glClear(GL_DEPTH_BUFFER_BIT)
        depth = self.depth_material
        glUseProgram(depth.programRef)
        depth.uniforms["lightMatrix"].uploadData()
        for mesh in scene.getDescendantList():
            if not isinstance(mesh, Mesh) or not mesh.visible or not getattr(mesh, "casts_shadow", True):
                continue
            geometry = mesh.geometry
            if geometry not in self.depth_vaos:
                vao = glGenVertexArrays(1)
                glBindVertexArray(vao)
                geometry.attributes["vertexPosition"].associateVariable(depth.programRef, "vertexPosition")
                self.depth_vaos[geometry] = vao
            glBindVertexArray(self.depth_vaos[geometry])
            depth.uniforms["modelMatrix"].data = mesh.getWorldMatrix()
            depth.uniforms["modelMatrix"].uploadData()
            glDrawArrays(GL_TRIANGLES, 0, geometry.vertexCount)

        # 2º passe: desenha a cena pela câmera (aplica luz e sombra)
        glBindFramebuffer(GL_FRAMEBUFFER, 0)
        glViewport(0, 0, *self.screen_size)
        super().render(scene, camera)
