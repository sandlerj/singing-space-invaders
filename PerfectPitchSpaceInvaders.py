import pygame, aubio
from pygamegame import PygameGame
from Ship import Ship
from Bullet import *
from PitchDetectionObject import PitchDetectionObject
# PygameGame superclass from Lukas Peraza's optional lecture on Pygame

class PerfectPitchSpaceInvaders(PygameGame): 

    def __init__(self, width=700, height=850, fps=30,
                                                    title="Space Invaders 112"):
        super().__init__(width, height, fps, title)

    def init(self):
        Ship.init(self.width,self.height) #inits ship image based on screen size
        #places ship near bottom of screen
        ship = Ship(self.width//2, self.height-Ship.image.get_height())

        Bullet.init(self.width, self.height) #Inits bullet image based on screen

        # Using RenderUpdates subgroup of class for dirty rect blitting
        self.shipGroup = pygame.sprite.RenderUpdates(ship)
        self.bulletGroup = pygame.sprite.RenderUpdates()

        self.dirtyRects = [] #stores rects which have been modified and must be
        #   reblitted

        self.background = pygame.Surface((self.width,self.height))
        self.bgColor = (0,0,0) # black
        self.background.fill(self.bgColor)

        #instantiate object for pitch detection
        self.pitchObject = PitchDetectionObject()

        # Will store time between bullet fires
        self.bulletTimer = 0

        # Bounds for checking if pitch is in certain range using
        self.lowBound = 48 #midi val for C3
        self.highBound = 72 #midi val for C5

    def timerFired(self, dt):
        # Ship moved in timer fired for steady movement based on held keys
        self.shipGroup.update(self.isKeyPressed, self.width, self.height)

        #move bullets
        self.bulletGroup.update(self.width, self.height)

        self.bulletTimer += dt
        #only fire a bullet at most every half second
        bulletCoolDown = 500 #miliseconds
        if self.bulletTimer > bulletCoolDown: 
            # Check if current sung pitch is in range
            if self.pitchObject.pitchInRange(self.lowBound, self.highBound):
                # If so, fire new bullet
                self.firePitchBullet(self.pitchObject.getNote())
                #reset cool down timer
                self.bulletTimer = 0

    def firePitchBullet(self, midiVal):
        # Given midi val
        self.bulletGroup.add(PitchBullet(self.shipGroup.sprites()[0].x,
                                    self.shipGroup.sprites()[0].y,
                                    (0,-1), midiVal))

    def redrawAll(self, screen):
        # Drawing members of RenderUpdates groups to screen - outputs list of
        # dirty rects for use in pygame.display.update below
        screen.blit(self.background, (0,0))
        self.dirtyRects.extend(self.bulletGroup.draw(screen))
        self.dirtyRects.extend(self.shipGroup.draw(screen))
        #update only the dirty rects
        pygame.display.update(self.dirtyRects)
        #clear the list of dirty rects
        self.dirtyRects.clear()

    def run(self):
        # Run the game
        super().run()
        # After mainloop is exited (in superclass run method), kill the pitch
        # object to close stream and terminate pyaudio.
        self.pitchObject.kill()