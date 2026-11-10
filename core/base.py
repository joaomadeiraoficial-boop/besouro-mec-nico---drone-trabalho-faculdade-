import os
os.environ.setdefault('PYGAME_HIDE_SUPPORT_PROMPT','1')
import pygame
from OpenGL.GL import *
class Base:
    def __init__(self,screenSize=None,title='Texturas com Python e OpenGL',compat_display=False):
        self.screenSize=screenSize or [960,640]
        pygame.display.init()
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MAJOR_VERSION,3)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_MINOR_VERSION,2)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_PROFILE_MASK,pygame.GL_CONTEXT_PROFILE_CORE)
        pygame.display.gl_set_attribute(pygame.GL_CONTEXT_FLAGS,pygame.GL_CONTEXT_FORWARD_COMPATIBLE_FLAG)
        pygame.display.gl_set_attribute(pygame.GL_DEPTH_SIZE,24)
        flags = pygame.OPENGL | pygame.DOUBLEBUF
        if compat_display:
            flags |= pygame.HIDDEN
        pygame.display.set_mode(self.screenSize, flags)
        pygame.display.set_caption(title)
        glViewport(0, 0, *self.screenSize)
        self.window = None
        if compat_display:
            from pygame._sdl2 import Renderer, Texture, Window

            # OpenGL desenha na janela oculta. A janela visível usa SDL por software.
            self.window = Window(title + " [compatibilidade]", size=self.screenSize)
            self.presenter = Renderer(self.window, accelerated=0)
            self.frame_texture = Texture(self.presenter, self.screenSize, streaming=True)
        self.clock=pygame.time.Clock();self.deltaTime=0;self.running=True
    def isKeyPressed(self,name):
        # True enquanto a tecla estiver pressionada. Nomes do pygame: 'up', 'down', 'a', 'space'...
        return pygame.key.get_pressed()[pygame.key.key_code(name)]
    def initialize(self): pass
    def update(self): pass
    def readFrame(self):
        glReadBuffer(GL_BACK)
        glPixelStorei(GL_PACK_ALIGNMENT, 1)
        width, height = self.screenSize
        data = glReadPixels(0, 0, width, height, GL_RGB, GL_UNSIGNED_BYTE)
        return pygame.image.frombytes(data, (width, height), "RGB", True)

    def saveScreenshot(self, path, surface=None):
        from pathlib import Path

        path = Path(path)
        path.parent.mkdir(parents=True, exist_ok=True)
        if surface is None:
            surface = self.readFrame()
        pygame.image.save(surface, str(path))
    def run(self,frames=None,screenshot=None):
        try:
            self.initialize();number=0
            while self.running:
                self.deltaTime=self.clock.tick(60)/1000
                for event in pygame.event.get():
                    if event.type in (pygame.QUIT, pygame.WINDOWCLOSE) or (event.type==pygame.KEYDOWN and event.key==pygame.K_ESCAPE): self.running=False
                    if event.type==pygame.KEYDOWN and event.key==pygame.K_s: self._capture=True
                self.update();number+=1
                frame = self.readFrame() if self.window is not None else None
                if getattr(self, '_capture', False):
                    self.saveScreenshot('capturas/resultado.png', frame)
                    self._capture = False
                if frames is not None and number>=frames:
                    if screenshot: self.saveScreenshot(screenshot, frame)
                    self.running=False
                if frame is None:
                    pygame.display.flip()
                else:
                    self.frame_texture.update(frame)
                    self.frame_texture.draw()
                    self.presenter.present()
            error=glGetError()
            if error!=GL_NO_ERROR: raise RuntimeError(f'OpenGL error: {error}')
        finally:
            if self.window is not None:
                del self.frame_texture
                del self.presenter
                self.window.destroy()
            pygame.quit()
