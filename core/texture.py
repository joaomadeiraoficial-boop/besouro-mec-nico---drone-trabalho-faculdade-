import pygame
from OpenGL.GL import *
class Texture:
    def __init__(self,fileName=None,properties=None):
        self.surface=None;self.textureRef=glGenTextures(1)
        self.properties={'magFilter':GL_LINEAR,'minFilter':GL_LINEAR_MIPMAP_LINEAR,'wrap':GL_REPEAT}
        self.setProperties(properties or {})
        if fileName is not None: self.loadImage(fileName);self.uploadData()
    def loadImage(self,fileName): self.surface=pygame.image.load(str(fileName))
    def setProperties(self,props):
        for name,value in props.items():
            if name not in self.properties: raise ValueError('Propriedade desconhecida: '+name)
            self.properties[name]=value
    def uploadData(self):
        width,height=self.surface.get_size()
        # Inverte linhas: imagem tem origem superior, UV tem origem inferior.
        pixelData=pygame.image.tostring(self.surface,'RGBA',True)
        glBindTexture(GL_TEXTURE_2D,self.textureRef)
        glTexImage2D(GL_TEXTURE_2D,0,GL_RGBA,width,height,0,GL_RGBA,GL_UNSIGNED_BYTE,pixelData)
        glGenerateMipmap(GL_TEXTURE_2D)
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MAG_FILTER,self.properties['magFilter'])
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_MIN_FILTER,self.properties['minFilter'])
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_S,self.properties['wrap'])
        glTexParameteri(GL_TEXTURE_2D,GL_TEXTURE_WRAP_T,self.properties['wrap'])
