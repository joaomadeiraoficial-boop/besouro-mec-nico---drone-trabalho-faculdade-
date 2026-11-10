from core.attribute import Attribute
class Geometry:
    def __init__(self): self.attributes={};self.vertexCount=0
    def addAttribute(self,dataType,variableName,data): self.attributes[variableName]=Attribute(dataType,data)
    def countVertices(self): self.vertexCount=len(self.attributes['vertexPosition'].data)
