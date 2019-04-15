import pygame
from pygamegame import PygameGame
from Ship import Ship
from Bullet import Bullet
from PitchDetectionObject import PitchDetectionObject
# PygameGame superclass from Lukas Peraza's optional lecture on Pygame
class PerfectPitchSpaceInvaders(PygameGame): 

    def __init__(self, width=700, height=850, fps=30,
                                                    title="Space Invaders 112"):
        super().__init__(width, height, fps, title)

    def init(self):
        Ship.init(self.width,self.height)
        ship = Ship(self.width//2, self.height-Ship.image.get_height())
        Bullet.init(self.width, self.height)
        # Using RenderUpdates subgroup of class for dirty rect blitting
        self.shipGroup = pygame.sprite.RenderUpdates(ship)
        self.bulletGroup = pygame.sprite.RenderUpdates()
        self.dirtyRects = []
        self.background = pygame.Surface((self.width,self.height))
        self.bgColor = (0,0,0)
        self.background.fill(self.bgColor)
        self.pitchObject = PitchDetectionObject()

    def timerFired(self, dt):
        self.shipGroup.update(self.isKeyPressed, self.width, self.height)
        self.bulletGroup.update(self.width, self.height)
        ## UNFINISHED#######################################################################
        if self.pitchObject.getPitch() == "A":
            self.fireBullet()

    def keyPressed(self, keyCode, modifier):
        if keyCode == pygame.K_SPACE:
            self.fireBullet()

    def redrawAll(self, screen):
        # drawing members of RenderUpdates groups to screen - outputs
        screen.blit(self.background, (0,0))
        self.dirtyRects.extend(self.shipGroup.draw(screen))
        self.dirtyRects.extend(self.bulletGroup.draw(screen))
        #update only the dirty rects
        pygame.display.update(self.dirtyRects)
        #clear the list of dirty rects
        self.dirtyRects.clear()

    def fireBullet(self):
        self.bulletGroup.add(Bullet(self.shipGroup.sprites()[0].x,
                                    self.shipGroup.sprites()[0].y,
                                    (0,-1)))