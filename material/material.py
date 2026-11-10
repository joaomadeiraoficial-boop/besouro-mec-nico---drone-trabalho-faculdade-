from OpenGL.GL import *
from OpenGL.GL.shaders import compileProgram,compileShader
from core.uniform import Uniform
from core.matrix import Matrix
class Material:
    def __init__(self,vertexShaderCode,fragmentShaderCode):
        # macOS core profile exige um VAO vinculado para o glValidateProgram do compileProgram
        tempVao=glGenVertexArrays(1);glBindVertexArray(tempVao)
        self.programRef=compileProgram(compileShader(vertexShaderCode,GL_VERTEX_SHADER),compileShader(fragmentShaderCode,GL_FRAGMENT_SHADER))
        glBindVertexArray(0);glDeleteVertexArrays(1,[tempVao])
        self.uniforms={};self.settings={'drawStyle':GL_TRIANGLES}
        for name in ['modelMatrix','viewMatrix','projectionMatrix']: self.addUniform('mat4',name,Matrix.makeIdentity())
    def addUniform(self,dataType,variableName,data): self.uniforms[variableName]=Uniform(dataType,data)
    def locateUniforms(self):
        for name,uniform in self.uniforms.items(): uniform.locateVariable(self.programRef,name)
    def setProperties(self,properties):
        for name,value in properties.items():
            if name in self.uniforms: self.uniforms[name].data=value
            elif name in self.settings: self.settings[name]=value
            else: raise ValueError('Propriedade desconhecida: '+name)
    def updateRenderSettings(self): pass
