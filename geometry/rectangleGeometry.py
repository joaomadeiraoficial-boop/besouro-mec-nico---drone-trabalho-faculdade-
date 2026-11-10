from geometry.geometry import Geometry
class RectangleGeometry(Geometry):
    def __init__(self,width=1,height=1):
        super().__init__()
        P0=[-width/2,-height/2,0];P1=[width/2,-height/2,0]
        P2=[-width/2,height/2,0];P3=[width/2,height/2,0]
        self.addAttribute('vec3','vertexPosition',[P0,P1,P3,P0,P3,P2])
        T0,T1,T2,T3=[0,0],[1,0],[0,1],[1,1]
        uvData=[T0,T1,T3,T0,T3,T2]
        self.addAttribute('vec2','vertexUV',uvData)
        self.countVertices()
