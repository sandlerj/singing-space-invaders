#Joseph Sandler, jsandler, Section B
# TP2 Deliverable

# Primary game object containing run method.
# Use SingingPitchSpaceInvaders().run() to run

# Tells python not to stretch the window despite high PPI display
import ctypes
ctypes.windll.user32.SetProcessDPIAware()

import pygame, aubio, random, time, copy, math
from pygamegame import PygameGame
from Ship import Ship
from Bullet import *
from PitchDetectionObject import PitchDetectionObject
from Alien import Alien
from Bricks import Brick
# PygameGame superclass from Lukas Peraza's optional lecture on Pygame
# https://qwewy.gitbooks.io/pygame-module-manual/chapter1/framework.html

class SingingSpaceInvaders(PygameGame): 

    def __init__(self, width=700, height=1000, fps=30,
                                                    title="Space Invaders 112"):
        super().__init__(width, height, fps, title)

    def init(self):
        self.guiInit()
        Ship.init(self.width,self.height) #inits ship image based on screen size
        #places ship near bottom of screen
        self.shipStartX = self.width//2
        self.shipStartY = self.height-Ship.image.get_height() * 1.5
        self.ship = Ship(self.shipStartX, self.shipStartY)
        Bullet.init(self.width, self.height) #Inits bullet image based on screen

        self.alienScaleFactor = 35 # alienWidth = screenWidth/scaleFactor
        Alien.init(self.width, self.height, self.alienScaleFactor)
        self.baseAlienMoveWaitTime = 2000

        self.brickScaleFactor = .2
        Brick.init(self.width, self.height, self.brickScaleFactor)
        self.barrierGroups = pygame.sprite.RenderUpdates()

        self.maxBarriers = 4


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

        self.soundDetectionInit()
        self.textFontInit()
        self.modesInit()

        #self.startNewGame(self.hardMode)  


    def guiInit(self):
        # helper for main init to handle some gui specific things (line count)
        self.guiImageDict = {}
        self.guiImageDict["helpScreen"] = pygame.image.load(os.path.join("GUI",
            "helpScreen.png"))
        self.guiImageDict["title"] = pygame.image.load(os.path.join("GUI",
            "logo.png"))

        self.guiImageDict["easyButton"] = pygame.image.load(os.path.join("GUI",
            "easyButton.png"))
        self.guiImageDict["hardButton"] = pygame.image.load(os.path.join("GUI",
            "hardButton.png"))
        spacer = 3
        self.easyButtonRect = self.guiImageDict['easyButton'].get_rect()
        self.easyButtonRect.move_ip((self.width//2 - \
            self.guiImageDict["easyButton"].get_width()//2),
            (self.height - self.guiImageDict['easyButton'].get_height()\
                * spacer))
        self.hardButtonRect = self.guiImageDict['hardButton'].get_rect()
        self.hardButtonRect.move_ip((self.width//2 - \
            self.guiImageDict["hardButton"].get_width()//2),
            (self.height - self.guiImageDict['hardButton'].get_height()\
                * (spacer/2)))

        

    def soundDetectionInit(self):
        # Helper init to manage pitchDetectionObject
        #instantiate object for pitch detection
        self.pitchObject = PitchDetectionObject()

        # Bounds for checking if pitch is in certain range using
        self.lowBound = 48 #midi val for C3
        self.highBound = 72 #midi val for C5
        self.midiScale = [0, 2, 4, 5, 7, 9, 11] # C Major scale in midi vals
        # Notes modulo 11:C  D  E  F  G  A  B
        self.minimumVolume = 0.001 #min volume to filter out background noise

    def textFontInit(self):
        # Helper for main init to handle font related things
        self.fontSize = Ship.image.get_height()//2
        self.fontColor = (255,255,255)
        # Visitor font by Ænigma at https://www.dafont.com/visitor.font
        self.gameFont = pygame.font.Font("Font" + os.sep + "visitor1.ttf",
            self.fontSize)
        self.textSideBuffer = 10
        self.bottomTextY = self.height - self.fontSize - 10
        self.bigGameFont = pygame.font.Font("Font" + os.sep + "visitor1.ttf",
            self.fontSize * 2)

    def modesInit(self):
        # Set up game mode structure for screens and start on menu mode
        self.menuMode = 'menu mode'
        self.gameMode = 'game mode'
        self.gameOverMode = 'game over mode'
        self.pauseMode = 'pause mode'
        self.mode = self.menuMode
        self.hardMode = False

    def timerFired(self, dt):
        # Main timer fired which dispatches to mode specific tF
        if self.mode == self.gameMode: self.gameTimerFired(dt)
        elif self.mode == self.gameOverMode: self.gameOverTimerFired(dt)
        elif self.mode == self.menuMode: self.menuTimerFired(dt)
        elif self.mode == self.pauseMode: self.pauseTimerFired(dt)

    def menuTimerFired(self, dt):
        pass

    def pauseTimerFired(self, dt):
        pass

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
        self.alienGroup.empty()
        self.barrierGroups.empty()
        self.alienBulletGroup.empty()
        self.pitchBulletGroup.empty()
        self.shipGroup.empty()

    def checkGameOver(self):
        # Check if the game is over, whether because alieans got down to the
        #   player, or because player has <0 lives
        alienPastPlayerY = False
        for alien in self.getFrontRowAliens():
            if alien.y + alien.image.get_height()//2 >= \
            self.shipStartY - Ship.height//2:
                alienPastPlayerY = True
        if alienPastPlayerY or self.playerLives < 0:
            self.mode = self.gameOverMode


    def startNewGame(self, hardMode=False):
        #starts a new game and takes flag for hardMode
        #   in hard mode, barries don't regenerate and player can damage own
        #   barriers
        self.mode = self.pauseMode

        # Will store time between bullet fires
        self.bulletCoolDownTimer = 0
        self.alienBulletTimer = 0

        # Alien move stuff
        self.alienStepTimer = 0
        self.alienSpeedIncreaseFactor = 0.95
        self.alienVector = (1,0)

        self.barrierFriendlyFire = False
        if hardMode: self.barrierFriendlyFire = True

        self.startingBarriers = 3

        self.pointsPerKill = 10
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
            if not self.hardMode:
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
                    vector = (0,1)
                    shipX, shipY = self.shipGroup.sprites()[0].getPos()
                    if self.hardMode:
                        #if hardmode, aim bullet at player
                        vector = self.getBulletVector(alien.x,alien.y,
                                                            shipX, shipY)
                    self.alienBulletGroup.add(Bullet(alien.x,alien.y, vector))

    def getBulletVector(self, alienX, alienY, shipX, shipY):
        #return (dx,dy) vector tuple for bullet creation
        dx0 = shipX - alienX
        dy0 = shipY - alienY
        angle = math.atan2(dy0,dx0)
        return(math.cos(angle),math.sin(angle))



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
            # Check if current sung pitch is in range, and ignores quiet sounds
            #   to filter background noise
            if self.pitchObject.pitchInRange(self.lowBound, self.highBound,
            scale = self.midiScale) and \
            self.pitchObject.volumeInRange(self.minimumVolume):
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
        # Checks if bullets collide with any of the brick sprites in the barrier
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
        #Key pressed dispatch
        if self.mode == self.gameMode: self.gameKeyPressed(keyCode, modifier)
        elif self.mode == self.gameOverMode: self.gameOverKeyPressed(keyCode,
                                                            modifier)
        elif self.mode == self.menuMode: pass
        elif self.mode == self.pauseMode: self.pauseKeyPressed(keyCode,
            modifier)

    def pauseKeyPressed(self, keyCode, modifier):
        #If any key is pressed, go to gameMode
        self.dirtyRects.append(pygame.rect.Rect(0,0,self.width, self.height))
        self.mode = self.gameMode

    def gameOverKeyPressed(self, keyCode, modifier):
        #any key leads to menu
        self.mode = self.menuMode

    def gameKeyPressed(self, keyCode, modifier):
        if keyCode == pygame.K_p:
            self.mode = self.pauseMode
        #The rest currently is debug code
        elif keyCode == pygame.K_k:
            self.shipGroup.empty()
        elif keyCode == pygame.K_l:
            self.alienGroup.empty()
        elif keyCode == pygame.K_j:
            self.mode = self.gameOverMode

    def firePitchBullet(self, midiVal):
        # Given midi val will fire a pitch bullet from ship pos
        self.pitchBulletGroup.add(PitchBullet(self.shipGroup.sprites()[0].x,
                                    self.shipGroup.sprites()[0].y,
                                    (0,-1), midiVal))

    def drawScoreText(self, screen):
        # draws score text at bottom left
        text = "Score: %d" % self.playerScore
        dest = self.textSideBuffer, self.bottomTextY
        textSurf = self.gameFont.render(text, True, self.fontColor)
        dirty = screen.blit(textSurf, dest)
        return dirty

    def drawLivesText(self, screen):
        # Draws lives text at bottom right
        text = "Lives: %d" % self.playerLives
        textSurf = self.gameFont.render(text, True, self.fontColor)
        bottomTextX = self.width - textSurf.get_width() - self.textSideBuffer
        return screen.blit(textSurf, (bottomTextX, self.bottomTextY))

    def redrawAll(self, screen):
        # Redraw all dispatch
        if self.mode == self.gameMode: self.gameRedrawAll(screen)
        elif self.mode == self.gameOverMode: self.gameOverRedrawAll(screen)
        elif self.mode == self.pauseMode: self.pauseRedrawAll(screen)
        elif self.mode == self.menuMode: self.menuRedrawAll(screen)

    def pauseRedrawAll(self, screen):
        pauseImage = self.guiImageDict['helpScreen']
        screen.blit(pauseImage, (self.width//2 - pauseImage.get_width()//2,
            self.height//2 - pauseImage.get_height()//2))
        pygame.display.flip()

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
        text = "GAME OVER"
        textSurf = self.bigGameFont.render(text, True, self.fontColor)
        screen.fill((0,0,0))
        screen.blit(textSurf, (self.width//2 - textSurf.get_width()//2,
            Ship.height))
        text2 = "PRESS ANY KEY"
        text2Surf = self.gameFont.render(text2, True, self.fontColor)
        screen.blit(text2Surf, (self.width//2 - text2Surf.get_width()//2,
            self.height//2))
        pygame.display.flip()

    def menuRedrawAll(self, screen):
        screen.fill((0,0,0))
        bufferY = 30
        screen.blit(self.guiImageDict['title'],
            (self.width//2 - self.guiImageDict['title'].get_width()//2,
                bufferY))
        screen.blit(self.guiImageDict['easyButton'], self.easyButtonRect)
        screen.blit(self.guiImageDict['hardButton'], self.hardButtonRect)

        pygame.display.flip()
        
    def mousePressed(self, x, y):
        # Mouse currently only used in menu mode
        if self.mode == self.menuMode: self.menuMousePressed(x,y)
        else: pass

    def menuMousePressed(self, x, y):
        #check if clicked inside buttons
        if self.easyButtonRect.collidepoint(x,y):
            self.hardMode = False
            self.startNewGame(self.hardMode)
        elif self.hardButtonRect.collidepoint(x,y):
            self.hardMode = True
            self.startNewGame(self.hardMode)

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
        # Puts aliens in top left corner of screen
        topBuffer = Alien.height//2
        numCols = 8
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
        # Adds barriers (non-pygame grouping of brick sprites) to barrierGroups
        #   list to be blitted
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
        # Returns list of brick sprites which together would form a barrier
        bricks = []
        brickArray = self.getBrickArray(numWide, numTall)
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
        #Based on the barrier dimensions, returns a 2D list which designates
        #   which cells should have a brick sprite and what image for the sprite
        result = [[None] * numWide for row in range(numTall)]
        for col in range(len(result[0])):
            result[0][col] = 0 #normal brick
        for row in range(len(result)):
            result[row][0] = 0
            result[row][-1] = 0
        result[0][0] = 1 #corner image
        result[0][-1] = 2 #corner image
        result[1][1] = 0
        result[1][-2] = 0
        return result


    def getBarrierCenters(self, numBarriers):
        #given the screen width and the number of barriers, returns a list
        #   of x positions where given number of barriers should be centered
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

