#Joseph Sandler, jsandler, Section B
# TP1 Deliverable

# Primary game object containing run method.
# Use PerfectPitchSpaceInvaders().run() to run

# Tells python not to stretch the window despite high PPI display. Solution from
# https://stackoverflow.com/questions/
#                      27421391/pygame-display-info-giving-wrong-resolution-size
import ctypes
ctypes.windll.user32.SetProcessDPIAware()

import pygame, aubio, random, time, copy
from pygamegame import PygameGame
from Ship import Ship
from Bullet import *
from PitchDetectionObject import PitchDetectionObject
from Alien import Alien
from Bricks import Brick
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
        self.shipStartY = self.height-Ship.image.get_height() * 1.5
        self.ship = Ship(self.shipStartX, self.shipStartY)
        Bullet.init(self.width, self.height) #Inits bullet image based on screen

        self.alienScaleFactor = 40 # alienWidth = screenWidth/scaleFactor
        Alien.init(self.width, self.height, self.alienScaleFactor)
        self.baseAlienMoveWaitTime = 2000

        self.brickScaleFactor = .2
        Brick.init(self.width, self.height, self.brickScaleFactor)
        self.barrierGroups = pygame.sprite.RenderUpdates()
        self.barrierGroups.add()
        self.barrierFriendlyFire = False
        self.maxBarriers = 4
        self.startingBarriers = 3

        # Using RenderUpdates subgroup of class for dirty rect blitting
        self.shipGroup = pygame.sprite.RenderUpdates()
        self.pitchBulletGroup = pygame.sprite.RenderUpdates()
        self.alienGroup = pygame.sprite.RenderUpdates()
        self.alienBulletGroup = pygame.sprite.RenderUpdates()
        self.dirtyRects = [] #stores rects which have been modified and must be
        #   reblitted

        self.background = pygame.Surface((self.width,self.height))
        self.bgColor = (0,0,0) # black
        self.background.fill(self.bgColor)


        # Will store time between bullet fires
        self.bulletCoolDownTimer = 0
        self.alienBulletTimer = 0

        # Alien move stufdfsfhsdfdjfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfdfd
        self.alienStepTimer = 0
        self.alienMoveWaitTime = 2000
        self.alienSpeedIncreaseFactor = 0.95
        self.alienVector = (1,0)

        self.pointsPerKill = 10
        
        self.soundDetectionInit()
        self.textFontInit()
        self.modesInit()

        self.startNewGame()


    def soundDetectionInit(self):
            #instantiate object for pitch detection
        self.pitchObject = PitchDetectionObject()

        # Bounds for checking if pitch is in certain range using
        self.lowBound = 48 #midi val for C3
        self.highBound = 72 #midi val for C5
        self.midiScale = [0, 2, 4, 5, 7, 9, 11] # C Major scale in midi vals
        # Notes modulo 11:C  D  E  F  G  A  B

    def textFontInit(self):
        self.fontSize = Ship.image.get_height()//2
        self.fontColor = (255,255,255)
        self.gameFont = pygame.font.SysFont("courier", self.fontSize, bold=True)
        self.textSideBuffer = 10
        self.bottomTextY = self.height - self.fontSize - 10

    def modesInit(self):
        self.menuMode = 'menu mode'
        self.gameMode = 'game mode'
        self.gameOverMode = 'game over mode'
        self.highScoreScreenMode = 'high score mode'
        self.mode = self.gameMode
        self.hardGame = False

    def timerFired(self, dt):
        if self.mode == self.gameMode: self.gameTimerFired(dt)
        elif self.mode == self.gameOverMode: self.gameOverTimerFired(dt)

    def gameTimerFired(self, dt):
        self.checkForNewLevel()
        self.checkGameOver()
                
        #check collisons between aliens and player's bullets
        self.bulletAlienCollisions()
        self.alienBulletPlayerCollisions()
        self.bulletBarrierCollisions()

        # Ship moved in timer fired for steady movement based on held keys
        self.shipGroup.update(self.isKeyPressed, self.width, self.height)

        #move bullets
        self.pitchBulletGroup.update(self.width, self.height)
        self.alienBulletGroup.update(self.width, self.height)

        self.barrierGroups.update()

        #fire player and alien bullets
        self.bulletFiring(dt) 
        self.fireAlienBullets(dt)
        #move aliens
        self.moveAliens(dt)

    def gameOverTimerFired(self,dt):
        print('game over')

    def checkGameOver(self):
        alienPastPlayerY = False
        for alien in self.getFrontRowAliens():
            if alien.y + alien.image.get_height()//2 >= \
            self.shipStartY - Ship.height//2:
                alienPastPlayerY = True
        if alienPastPlayerY or self.playerLives < 0:
            self.mode = self.gameOverMode


    def startNewGame(self):
        self.mode = self.gameMode
        self.alienMoveWaitTime = self.baseAlienMoveWaitTime
        self.playerLevel = 0
        self.playerLives = 3
        self.playerScore = 0
        self.populateWithAliens()
        self.placeBarriers(self.startingBarriers)
        self.shipGroup.add(copy.copy(self.ship))

    def checkForNewLevel(self):
        #checks if new level should be started and takes appropriate action
        if len(self.alienGroup) == 0:
            if not self.hardGame:
                self.playerLives += 1
                self.barrierGroups.empty()
                self.placeBarriers(random.randint(1, self.maxBarriers))
                time.sleep(2)
            self.pitchBulletGroup.empty()
            self.alienBulletGroup.empty()
            self.populateWithAliens(rand=True)
            self.playerLevel += 1
            alienSpeedIncrement = 200
            self.alienMoveWaitTime = self.baseAlienMoveWaitTime - \
                    alienSpeedIncrement * self.playerLevel


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
            self.playerScore += self.pointsPerKill
            alien.kill()

    def bulletBarrierCollisions(self):
        for brick in self.barrierGroups:
            for bullet in self.alienBulletGroup:
                if pygame.sprite.collide_rect(brick, bullet):
                    brick.getHit()
                    bullet.kill()
            for bullet in self.pitchBulletGroup:
                if pygame.sprite.collide_rect(brick, bullet):
                    bullet.kill()
                    if self.barrierFriendlyFire:
                        brick.getHit()


    def keyPressed(self, keyCode, modifier):
        if self.mode == self.gameMode: self.gameKeyPressed(keyCode, modifier)
        elif self.mode == self.gameOverMode: self.gameOverKeyPressed(keyCode,
                                                            modifier)

    def gameOverKeyPressed(self, keyCode, modifier):
        self.alienGroup.empty()
        self.barrierGroups.empty()
        self.alienBulletGroup.empty()
        self.pitchBulletGroup.empty()
        self.shipGroup.empty()
        if keyCode == pygame.K_r:
            self.startNewGame()
            self.mode = 'game mode'

    def gameKeyPressed(self, keyCode, modifier):
        #currently all debug code... more to be added
        if keyCode == pygame.K_k:
            self.shipGroup.empty()
        elif keyCode == pygame.K_l:
            self.alienGroup.empty()
        elif keyCode == pygame.K_j:
            self.mode = self.gameOverMode

    def firePitchBullet(self, midiVal):
        # Given midi val
        self.pitchBulletGroup.add(PitchBullet(self.shipGroup.sprites()[0].x,
                                    self.shipGroup.sprites()[0].y,
                                    (0,-1), midiVal))

    def drawScoreText(self, screen):
        text = "Score: %d" % self.playerScore
        dest = self.textSideBuffer, self.bottomTextY
        textSurf = self.gameFont.render(text, True, self.fontColor)
        dirty = screen.blit(textSurf, dest)
        return dirty

    def drawLivesText(self, screen):
        text = "Lives: %d" % self.playerLives
        textSurf = self.gameFont.render(text, True, self.fontColor)
        bottomTextX = self.width - textSurf.get_width() - self.textSideBuffer
        return screen.blit(textSurf, (bottomTextX, self.bottomTextY))

    def redrawAll(self, screen):
        if self.mode == self.gameMode: self.gameRedrawAll(screen)
        if self.mode == self.gameOverMode: self.gameOverRedrawAll(screen)

    def gameRedrawAll(self, screen):
        # Drawing members of RenderUpdates groups to screen - outputs list of
        # dirty rects for use in pygame.display.update below
        screen.blit(self.background, (0,0))
        self.dirtyRects.extend(self.barrierGroups.draw(screen))
        self.dirtyRects.extend(self.pitchBulletGroup.draw(screen))
        self.dirtyRects.extend(self.shipGroup.draw(screen))
        self.dirtyRects.extend(self.alienBulletGroup.draw(screen))
        self.dirtyRects.extend(self.alienGroup.draw(screen))
        self.dirtyRects.append(self.drawScoreText(screen))
        self.dirtyRects.append(self.drawLivesText(screen))
        #update only the dirty rects
        pygame.display.update(self.dirtyRects)
        #clear the list of dirty rects
        self.dirtyRects.clear()

    def gameOverRedrawAll(self, screen):
        pass
        

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

    def placeBarriers(self, numBarriers):
        toBePlaced = []
        numBricksWide = 4
        numBricksTall = 3
        barrierWidth = Brick.width * numBricksWide
        barrierHeight = Brick.height * numBricksTall
        barrierCXList = self.getBarrierCenters(numBarriers)
        barrierCY = self.shipStartY - Ship.height * 2
        for x in barrierCXList:
            toBePlaced.extend(self.buildBarrier(x, barrierCY,
                            numBricksWide, numBricksTall))
        self.barrierGroups.add(toBePlaced)

    def buildBarrier(self, cx, cy, numWide, numTall):
        print("barrier cent", cx, cy)
        bricks = []
        brickArray = self.getBrickArray(numWide, numTall)
        print(brickArray)
        for row in range(len(brickArray)):
            if numTall % 2 == 0:
                correction = 1 
                y = (cy - Brick.height * ((numTall//2) - row)) + \
                        correction * Brick.height//2
            else:
                y = cy - Brick.height * ((numTall//2) - row)
            for col in range(len(brickArray[row])):
                if numWide % 2 == 0:
                    correction = 1 
                    x = (cx - Brick.width * ((numWide//2) - col)) + \
                            correction * Brick.width//2
                else:
                    x = cx - Brick.width * ((numWide//2) - col)
                if brickArray[row][col] != None:
                    bricks.append(Brick(x,y, brickArray[row][col]))
        return bricks



    def getBrickArray(self, numWide, numTall):
        result = [[None] * numWide for row in range(numTall)]
        for col in range(len(result[0])):
            result[0][col] = 0
        for row in range(len(result)):
            result[row][0] = 0
            result[row][-1] = 0
        result[0][0] = 1
        result[0][-1] = 2
        result[1][1] = 0
        result[1][-2] = 0
        return result


    def getBarrierCenters(self, numBarriers):
        cxList = []
        for x in range(0, self.width, self.width//(numBarriers + 1)):
            cxList.append(x)
        if 0 in cxList:
            #remov first element, which is on wall
            cxList.remove(0)
        if len(cxList) > numBarriers:
            cxList.pop()
        return cxList

    def run(self):
        # Run the game
        super().run()
        # After mainloop is exited (in superclass run method), kill the pitch
        # object to close stream and terminate pyaudio.
        self.pitchObject.kill()

if __name__ == "__main__":
    SingingSpaceInvaders().run()

