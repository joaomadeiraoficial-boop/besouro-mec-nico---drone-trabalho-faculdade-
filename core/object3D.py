from core.matrix import Matrix
class Object3D:
    def __init__(self):
        self.transform=Matrix.makeIdentity();self.parent=None;self.children=[]
    def add(self,child): self.children.append(child);child.parent=self
    def remove(self,child): self.children.remove(child);child.parent=None
    def getWorldMatrix(self):
        return self.transform if self.parent is None else self.parent.getWorldMatrix() @ self.transform
    def getDescendantList(self):
        result=[self]
        for child in self.children: result.extend(child.getDescendantList())
        return result
    def applyMatrix(self,matrix,localCoord=True):
        self.transform=self.transform@matrix if localCoord else matrix@self.transform
    def translate(self,x,y,z,localCoord=True): self.applyMatrix(Matrix.makeTranslation(x,y,z),localCoord)
    def rotateX(self,angle,localCoord=True): self.applyMatrix(Matrix.makeRotationX(angle),localCoord)
    def rotateY(self,angle,localCoord=True): self.applyMatrix(Matrix.makeRotationY(angle),localCoord)
    def rotateZ(self,angle,localCoord=True): self.applyMatrix(Matrix.makeRotationZ(angle),localCoord)
    def scale(self,s,localCoord=True): self.applyMatrix(Matrix.makeScale(s),localCoord)
    def setPosition(self,position): self.transform[:3,3]=position
    def getPosition(self): return self.transform[:3,3].tolist()
    def getWorldPosition(self): return self.getWorldMatrix()[:3,3].tolist()
