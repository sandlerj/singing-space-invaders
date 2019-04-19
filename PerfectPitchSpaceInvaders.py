#Joseph Sandler, jsandler, Section B
# TP1 Deliverable

# Primary game object containing run method.
# Use PerfectPitchSpaceInvaders().run() to run

import pygame, aubio, random
from pygamegame import PygameGame
from Ship import Ship
from Bullet import *
from PitchDetectionObject import PitchDetectionObject
from Alien import Alien
# PygameGame superclass from Lukas Peraza's optional lecture on Pygame
# https://qwewy.gitbooks.io/pygame-module-manual/chapter1/framework.html

class SingingSpaceInvaders(PygameGame): 

    def __init__(self, width=700, height=850, fps=30,
                                                    title="Space Invaders 112"):
        super().__init__(width, height, fps, title)

    def init(self):
        Ship.init(self.width,self.height) #inits ship image based on screen size
        #places ship near bottom of screen
        ship = Ship(self.width//2, self.height-Ship.image.get_height())
        Bullet.init(self.width, self.height) #Inits bullet image based on screen

        self.alienScaleFactor = 40 # alienWidth = screenWidth/scaleFactor
        Alien.init(self.width, self.height, self.alienScaleFactor)

        # Using RenderUpdates subgroup of class for dirty rect blitting
        self.shipGroup = pygame.sprite.RenderUpdates(ship)
        self.pitchBulletGroup = pygame.sprite.RenderUpdates()
        self.alienGroup = pygame.sprite.RenderUpdates()

        self.dirtyRects = [] #stores rects which have been modified and must be
        #   reblitted

        self.background = pygame.Surface((self.width,self.height))
        self.bgColor = (0,0,0) # black
        self.background.fill(self.bgColor)

        #instantiate object for pitch detection
        self.pitchObject = PitchDetectionObject()

        # Will store time between bullet fires
        self.bulletCoolDownTimer = 0

        # Alien move stufdfsfhsdfdjfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfd
        self.alienStepTimer = 0
        self.alienMoveWaitTime = 500
        self.alienSpeedIncreaseFactor = 0.95
        self.alienVector = (1,0)


        # Bounds for checking if pitch is in certain range using
        self.lowBound = 48 #midi val for C3
        self.highBound = 72 #midi val for C5
        self.midiScale = [0, 2, 4, 5, 7, 9, 11] # C Major scale in midi vals
        # Notes modulo 11:C  D  E  F  G  A  B

    def timerFired(self, dt):
        # Ship moved in timer fired for steady movement based on held keys
        self.shipGroup.update(self.isKeyPressed, self.width, self.height)

        #move bullets
        self.pitchBulletGroup.update(self.width, self.height)

        self.bulletCoolDownTimer += dt

        #only fire a bullet at most every...
        bulletCoolDown = 100 #miliseconds
        if self.bulletCoolDownTimer > bulletCoolDown: 
            # Check if current sung pitch is in range
            if self.pitchObject.pitchInRange(self.lowBound, self.highBound,
                scale = self.midiScale):
                # If so, fire new bullet
                self.firePitchBullet(self.pitchObject.getNote())
                #reset cool down timer
                self.bulletCoolDownTimer = 0

        if len(self.alienGroup)  > 0:
            self.alienStepTimer += dt

            if self.alienStepTimer >= self.alienMoveWaitTime:
                # determine direction aliens should move
                newVector = self.getAlienVector(self.alienVector,
                                                        Alien.moveStepSizeX)
                self.alienVector = newVector
                self.alienGroup.update(self.alienVector)
                self.alienStepTimer = 0
                if self.alienVector == (0, 1):
                    self.alienMoveWaitTime *= self.alienSpeedIncreaseFactor



    def keyPressed(self, keyCode, modifier):
        if keyCode == pygame.K_SPACE:
            self.populateWithAliens(rand=True)

    def firePitchBullet(self, midiVal):
        # Given midi val
        self.pitchBulletGroup.add(PitchBullet(self.shipGroup.sprites()[0].x,
                                    self.shipGroup.sprites()[0].y,
                                    (0,-1), midiVal))

    def redrawAll(self, screen):
        # Drawing members of RenderUpdates groups to screen - outputs list of
        # dirty rects for use in pygame.display.update below
        screen.blit(self.background, (0,0))
        self.dirtyRects.extend(self.pitchBulletGroup.draw(screen))
        self.dirtyRects.extend(self.shipGroup.draw(screen))
        self.dirtyRects.extend(self.alienGroup.draw(screen))
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

    def getLeftmostAlien(self):
        #return left side of left-most alien rect
        currentLeftest = self.width #init at furthest right possible
        for alien in self.alienGroup:
            alienLeft = (alien.x - alien.width//2)
            if alienLeft < currentLeftest:
                currentLeftest = alienLeft
        return currentLeftest

    def getRightmostAlien(self):
        #return right side of right-most alien rect
        currentRightest = 0 #init at furthest left possible
        for alien in self.alienGroup:
            alienRight = (alien.x + alien.width//2)
            if alienRight > currentRightest:
                currentRightest = alienRight
        return currentRightest

    def getAlienVector(self, currentVector, stepSize):
        #determine direction that alien group should move based on remaining
        #alien positions and previous direction
        leftBound = self.getLeftmostAlien()
        rightBound = self.getRightmostAlien()
        if currentVector == (1,0):
            #if moving right, check if continuing in direction stays on screen,
            # else, move down
            if rightBound + Alien.moveStepSizeX < self.width:
                return (1,0)
            else:
                return (0,1)
        elif currentVector == (-1,0):
            # if going left, check if continuing in direction stays on screen,
            # else, move down
            if leftBound - Alien.moveStepSizeX > 0:
                return (-1,0)
            else:
                return (0,1)
        elif currentVector == (0,1):
            # if just went down, check left side and go that way if possible,
            # otherwise go right
            if leftBound - Alien.moveStepSizeX > 0:
                return (-1,0)
            else:
                return (1,0)


    def populateWithAliens(self, rand=False):
        topBuffer = Alien.height//2
        numCols = 10
        numRows = 7
        notes = iter(self.midiScale)
        #nested forloop drawing aliens with buffer
        for cy in range(Alien.bufferY + topBuffer, 
            topBuffer + (Alien.stepSizeY) * numRows + 1, Alien.stepSizeY):
            if not rand:
                #alien generation not random
                note = next(notes)
            for cx in range(Alien.bufferX, (Alien.stepSizeX) * numCols + 1,
                Alien.stepSizeX):
                if rand:
                    note = random.choice(self.midiScale)
                self.alienGroup.add(Alien(cx,cy, note))


if __name__ == "__main__":
    SingingSpaceInvaders().run()