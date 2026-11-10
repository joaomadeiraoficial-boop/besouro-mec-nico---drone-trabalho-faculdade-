from OpenGL.GL import *
from core.mesh import Mesh
class Renderer:
    def __init__(self,clearColor=None):
        clearColor=clearColor or [0.94,0.95,0.97]
        glEnable(GL_DEPTH_TEST);glEnable(GL_BLEND)
        glBlendFunc(GL_SRC_ALPHA,GL_ONE_MINUS_SRC_ALPHA)
        glClearColor(*clearColor,1)
    def render(self,scene,camera):
        glClear(GL_COLOR_BUFFER_BIT|GL_DEPTH_BUFFER_BIT)
        camera.updateViewMatrix()
        for mesh in scene.getDescendantList():
            if not isinstance(mesh,Mesh) or not mesh.visible: continue
            mat=mesh.material
            glUseProgram(mat.programRef);glBindVertexArray(mesh.vaoRef)
            mat.uniforms['modelMatrix'].data=mesh.getWorldMatrix()
            mat.uniforms['viewMatrix'].data=camera.viewMatrix
            mat.uniforms['projectionMatrix'].data=camera.projectionMatrix
            for uniform in mat.uniforms.values(): uniform.uploadData()
            mat.updateRenderSettings()
            glDrawArrays(mat.settings['drawStyle'],0,mesh.geometry.vertexCount)
        glBindVertexArray(0)
