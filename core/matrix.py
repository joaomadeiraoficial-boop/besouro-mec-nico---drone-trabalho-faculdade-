import numpy as np
from math import sin, cos, tan, radians
class Matrix:
    @staticmethod
    def makeIdentity(): return np.identity(4, dtype=np.float32)
    @staticmethod
    def makeTranslation(x,y,z):
        m=Matrix.makeIdentity(); m[:3,3]=[x,y,z]; return m
    @staticmethod
    def makeRotationX(a):
        c,s=cos(a),sin(a)
        return np.array([[1,0,0,0],[0,c,-s,0],[0,s,c,0],[0,0,0,1]],dtype=np.float32)
    @staticmethod
    def makeRotationY(a):
        c,s=cos(a),sin(a)
        return np.array([[c,0,s,0],[0,1,0,0],[-s,0,c,0],[0,0,0,1]],dtype=np.float32)
    @staticmethod
    def makeRotationZ(a):
        c,s=cos(a),sin(a)
        return np.array([[c,-s,0,0],[s,c,0,0],[0,0,1,0],[0,0,0,1]],dtype=np.float32)
    @staticmethod
    def makeScale(s): return np.diag([s,s,s,1]).astype(np.float32)
    @staticmethod
    def makePerspective(angleOfView=60,aspectRatio=1,near=0.1,far=1000):
        f=1/tan(radians(angleOfView)/2)
        return np.array([[f/aspectRatio,0,0,0],[0,f,0,0],[0,0,(far+near)/(near-far),2*far*near/(near-far)],[0,0,-1,0]],dtype=np.float32)
