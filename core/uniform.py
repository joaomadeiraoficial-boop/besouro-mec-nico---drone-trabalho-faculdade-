import numpy as np
from OpenGL.GL import *
class Uniform:
    def __init__(self,dataType,data): self.dataType,self.data,self.variableRef=dataType,data,-1
    def locateVariable(self,programRef,variableName): self.variableRef=glGetUniformLocation(programRef,variableName)
    def uploadData(self):
        if self.variableRef<0: return
        if self.dataType=='mat4':
            # GLSL recebe colunas: transpose=False e dados transpostos em memória.
            array=np.ascontiguousarray(np.asarray(self.data,dtype=np.float32).T)
            glUniformMatrix4fv(self.variableRef,1,GL_FALSE,array)
        elif self.dataType=='vec2': glUniform2fv(self.variableRef,1,self.data)
        elif self.dataType=='vec3': glUniform3fv(self.variableRef,1,self.data)
        elif self.dataType=='sampler2D':
            textureObjectRef,textureUnitRef=self.data
            glActiveTexture(GL_TEXTURE0+textureUnitRef)
            glBindTexture(GL_TEXTURE_2D,textureObjectRef)
            glUniform1i(self.variableRef,textureUnitRef)
        else: raise ValueError('Tipo de uniform não implementado: '+self.dataType)
