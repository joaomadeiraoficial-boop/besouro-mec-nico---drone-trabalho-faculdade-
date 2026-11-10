import numpy as np
from OpenGL.GL import *
class Attribute:
    def __init__(self,dataType,data):
        self.dataType,self.data=dataType,data
        self.bufferRef=glGenBuffers(1)
        array=np.asarray(data,dtype=np.float32)
        glBindBuffer(GL_ARRAY_BUFFER,self.bufferRef)
        glBufferData(GL_ARRAY_BUFFER,array.nbytes,array,GL_STATIC_DRAW)
    def associateVariable(self,programRef,variableName):
        ref=glGetAttribLocation(programRef,variableName)
        if ref<0: return
        size={'vec2':2,'vec3':3,'vec4':4}[self.dataType]
        glBindBuffer(GL_ARRAY_BUFFER,self.bufferRef)
        glVertexAttribPointer(ref,size,GL_FLOAT,GL_FALSE,0,None)
        glEnableVertexAttribArray(ref)
