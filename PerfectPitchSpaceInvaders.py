#Joseph Sandler, jsandler, Section B
# TP1 Deliverable

# Primary game object containing run method.
# Use PerfectPitchSpaceInvaders().run() to run

import pygame, aubio, random, time
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
        self.shipStartX = self.width//2
        self.shipStartY = self.height-Ship.image.get_height() * 2
        ship = Ship(self.shipStartX, self.shipStartY)
        Bullet.init(self.width, self.height) #Inits bullet image based on screen

        self.alienScaleFactor = 40 # alienWidth = screenWidth/scaleFactor
        Alien.init(self.width, self.height, self.alienScaleFactor)

        # Using RenderUpdates subgroup of class for dirty rect blitting
        self.shipGroup = pygame.sprite.RenderUpdates(ship)
        self.pitchBulletGroup = pygame.sprite.RenderUpdates()
        self.alienGroup = pygame.sprite.RenderUpdates()
        self.alienBulletGroup = pygame.sprite.RenderUpdates()
        self.dirtyRects = [] #stores rects which have been modified and must be
        #   reblitted

        self.background = pygame.Surface((self.width,self.height))
        self.bgColor = (0,0,0) # black
        self.background.fill(self.bgColor)

        #instantiate object for pitch detection
        self.pitchObject = PitchDetectionObject()

        # Will store time between bullet fires
        self.bulletCoolDownTimer = 0
        self.alienBulletTimer = 0

        # Alien move stufdfsfhsdfdjfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfd
        self.alienStepTimer = 0
        self.alienMoveWaitTime = 2000
        self.alienSpeedIncreaseFactor = 0.95
        self.alienVector = (1,0)


        # Bounds for checking if pitch is in certain range using
        self.lowBound = 48 #midi val for C3
        self.highBound = 72 #midi val for C5
        self.midiScale = [0, 2, 4, 5, 7, 9, 11] # C Major scale in midi vals
        # Notes modulo 11:C  D  E  F  G  A  B

        self.playerLives = 3
        self.playerScore = 0

    def timerFired(self, dt):

        #check collisons between aliens and player's bullets
        self.bulletAlienCollisions()
        self.alienBulletPlayerCollisions()

        # Ship moved in timer fired for steady movement based on held keys
        self.shipGroup.update(self.isKeyPressed, self.width, self.height)

        #move bullets
        self.pitchBulletGroup.update(self.width, self.height)
        self.alienBulletGroup.update(self.width, self.height)

        #fire player and alien bullets
        self.bulletFiring(dt) 
        self.fireAlienBullets(dt)
        #move aliens
        self.moveAliens(dt)

    # @staticmethod
    # def collideMask(sprite1, sprite2):
    #     # Wrapper for pygame.sprite.collide_mask for use as callback in
    #     #   groupcollide
    #     print(sprite1.mask)
    #     print(sprite2.mask)
    #     point = pygame.sprite.collide_mask(sprite1, sprite2)
    #     print(point)
    #     if point != None:
    #         return True
    #     return False

    def alienBulletPlayerCollisions(self):
        # Checks collisions between player and alien bullets, kills player and
        #   takes a life away.
        pygame.sprite.groupcollide(self.shipGroup, self.alienBulletGroup,
            True, True)
        if len(self.shipGroup) == 0:
            self.pitchBulletGroup.empty()
            self.alienBulletGroup.empty()
            time.sleep(1) #If player dies, pause for a second and then respawn
            self.shipGroup.add(Ship(self.shipStartX, self.shipStartY))
            self.playerLives -= 1

    def fireAlienBullets(self, dt):
        # Possibly fire alien bullets every interval, and reset timer
        alienBulletCoolDownTime = 2000
        chanceOfFiring = 5
        self.alienBulletTimer += dt
        if self.alienBulletTimer > alienBulletCoolDownTime:
            self.alienBulletTimer = 0
            frontRowAliens = self.getFrontRowAliens()
            for alien in frontRowAliens:
                coinFlip = random.randint(0,chanceOfFiring)
                if coinFlip == chanceOfFiring:
                    self.alienBulletGroup.add(Bullet(alien.x,alien.y, (0,1)))


    def getFrontRowAliens(self):
        # Returns list of aliens who have no aliens in front of them, i.e. a 
        #   clear line of sight for firing bullets
        frontRowAliens = {}
        # Map furthest south alien in a column to the x value of that column
        for alien in self.alienGroup:
            if alien.x not in frontRowAliens:
                # If column has not been seen yet, add it with current alien
                frontRowAliens[alien.x] = alien
            elif alien.y > frontRowAliens[alien.x].y:
                #otherwise, check if current alien is further south than last
                # stored in that column
                frontRowAliens[alien.x] = alien
        #return list of those aliens
        return list(frontRowAliens.values())


    def bulletFiring(self,dt):
        #fires bullets intermitently when there's sound input
        self.bulletCoolDownTimer += dt
        #only fire a bullet at most every...
        bulletCoolDown = 200 #miliseconds
        if self.bulletCoolDownTimer > bulletCoolDown: 
            # Check if current sung pitch is in range
            if self.pitchObject.pitchInRange(self.lowBound, self.highBound,
                scale = self.midiScale):
                # If so, fire new bullet
                self.firePitchBullet(self.pitchObject.getNote())
                #reset cool down timer
                self.bulletCoolDownTimer = 0

    def moveAliens(self,dt):
        #helper method to move aliens as a unit
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

    def bulletAlienCollisions(self):
        # Checks if bullets are colliding with aliens and if so removes bullets
        # from all groups. In same iteration, checks if bullet was correct hit
        # for given alien, and if so, removes alien from all groups as well.
        correctHitAliens = []
        hitBullets = []
        for bullet in self.pitchBulletGroup:
            for alien in self.alienGroup:
                if pygame.sprite.collide_rect(bullet, alien):
                    hitBullets.append(bullet)
                    if bullet.note == alien.note:
                        correctHitAliens.append(alien)
        for bullet in hitBullets:
            bullet.kill()
        for alien in correctHitAliens:
            alien.kill()



    def keyPressed(self, keyCode, modifier):
        if keyCode == pygame.K_SPACE:
            self.populateWithAliens(rand=True)
        elif keyCode == pygame.K_k:
            self.shipGroup.empty()
        elif keyCode == pygame.K_l:
            self.getFrontRowAliens()

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
        self.dirtyRects.extend(self.alienBulletGroup.draw(screen))
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