from core.object3D import Object3D
from OpenGL.GL import *
class Mesh(Object3D):
    def __init__(self,geometry,material):
        super().__init__();self.geometry,self.material,self.visible=geometry,material,True
        self.vaoRef=glGenVertexArrays(1);glBindVertexArray(self.vaoRef)
        for name,attribute in geometry.attributes.items(): attribute.associateVariable(material.programRef,name)
        glBindVertexArray(0)
