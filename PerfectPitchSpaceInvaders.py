import pygame
from pygamegame import PygameGame

# PygameGame superclass from Lukas Peraza's optional lecture on Pygame
class PerfectPitchSpaceInvaders(PygameGame): 

    def init(self):
        self.shipGroup = pygame.sprite.RenderUpdates()
        self.shipGroup.add(Ship())
        self.bulletGroup = pygame.sprite.RenderUpdates()
        self.dirtyRects = []

    def timerFired(self, dt):
        self.shipGroup.update(...)
        self.bulletGroup.update(...)

    def keyPressed(self, keyCode, modifier):
        if keyCode == pygame.K_SPACE:
            self.bulletGroup.add(Bullet(shipGroup.sprites()[0].x,
                                        shipGroup.sprites()[0].y,
                                        (0,-1)))

    def redrawAll(self, screen):
        #populating list of dirty rects
        self.dirtyRects.extend(self.shipGroup.draw(screen))
        self.dirtyRects.extend(self.bulletGroup.draw(screen))
        #update only the dirty rects
        screen.update(self.dirtyRects)
        #clear the list of dirty rects
        self.dirtyRects.clear()