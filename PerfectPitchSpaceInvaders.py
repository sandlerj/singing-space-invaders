import pygame
from pygamegame import PygameGame
from Ship import Ship

# PygameGame superclass from Lukas Peraza's optional lecture on Pygame
class PerfectPitchSpaceInvaders(PygameGame): 

    def init(self):
        ship = Ship(self.width//2, self.height//2)
        # Using RenderUpdates subgroup of class for dirty rect blitting
        self.shipGroup = pygame.sprite.RenderUpdates(ship)
        self.bulletGroup = pygame.sprite.RenderUpdates()
        self.dirtyRects = []

    def timerFired(self, dt):
        self.shipGroup.update(self.isKeyPressed, self.width, self.height)
        #self.bulletGroup.update(...)

    def keyPressed(self, keyCode, modifier):
        if keyCode == pygame.K_SPACE:
            self.bulletGroup.add(Bullet(shipGroup.sprites()[0].x,
                                        shipGroup.sprites()[0].y,
                                        (0,-1)))

    def redrawAll(self, screen):
        # drawing members of RenderUpdates groups to screen - outputs
        self.dirtyRects.extend(self.shipGroup.draw(screen))
        self.dirtyRects.extend(self.bulletGroup.draw(screen))
        #update only the dirty rects
        pygame.display.update(self.dirtyRects)
        #clear the list of dirty rects
        self.dirtyRects.clear()