#Joseph Sandler, jsandler, Section B
# TP2 Deliverable

import module_manager #by Austin Schick (see file for further citation)
module_manager.review()

# Primary game object containing run method.
# Use SingingPitchSpaceInvaders().run() to run

# Tells python not to stretch the window despite high PPI display
import ctypes
ctypes.windll.user32.SetProcessDPIAware()

import pygame, aubio, random, time, copy, math
from pygamegame import PygameGame
from Ship import Ship, GyrussShip
from Bullet import *
from PitchDetectionObject import PitchDetectionObject
from Alien import Alien
from Bricks import Brick

# PygameGame superclass from Lukas Peraza's optional lecture on Pygame
# https://qwewy.gitbooks.io/pygame-module-manual/chapter1/framework.html

class SingingSpaceInvaders(PygameGame):
    
    def __init__(self, width=800, height=1000, fps=30,
                                                    title="Space Invaders 112"):
        super().__init__(width, height, fps, title)

    def init(self):
        self.guiInit()
        self.loadSelectionButtons()
        Ship.init(self.width,self.height) #inits ship image based on screen size
        #places ship near bottom of screen
        self.shipSelection = 'ship.png'
        self.shipStartX = self.width//2
        self.shipStartY = self.height-Ship.height * 1.5
        Bullet.init(self.width, self.height) #Inits bullet image based on screen

        self.alienScaleFactor = 40 # alienWidth = screenWidth/scaleFactor
        Alien.init(self.width, self.height, self.alienScaleFactor)
        self.baseAlienMoveWaitTime = 4000

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
        self.highScoresInit()
        self.cMajScale = pygame.mixer.Sound(os.path.join("Sounds", 
            "cMajScale.wav"))

    def highScoresInit(self):
        # Loads/creates highscrore text file in current dir
        self.hsPath = "highScores.txt"
        if self.hsPath not in os.listdir():
            writeFile(self.hsPath, emptyHighScores())

        highScoreRawContents = readFile(self.hsPath).splitlines()
        self.highScoreContents = []
        for line in highScoreRawContents:
            #reads contents and breaks them up by the dividing token (@)
            self.highScoreContents.append(line.split('@'))


    def guiInit(self):
        # helper for main init to handle some gui specific things (line count)
        self.guiImageDict = {}
        self.guiImageDict["helpScreen"] = pygame.image.load(os.path.join("GUI",
            "helpScreen.png"))
        self.guiImageDict["title"] = pygame.image.load(os.path.join("GUI",
            "logo.png"))
        self.guiImageDict['gyrussHelpScreen'] = pygame.image.load(os.path.join(\
            "GUI", "gyrussHelpScreen.png"))

        self.guiImageDict["easyButton"] = pygame.image.load(os.path.join("GUI",
            "easyButton.png"))
        self.guiImageDict["hardButton"] = pygame.image.load(os.path.join("GUI",
            "hardButton.png"))
        self.guiImageDict["gyrussButton"] = pygame.image.load(os.path.join(\
            "GUI", "gyrussButton.png"))
        spacer = 4.5
        self.easyButtonRect = self.guiImageDict['easyButton'].get_rect()
        self.easyButtonRect.move_ip((self.width//2 - \
            self.guiImageDict["easyButton"].get_width()//2),
            (self.height - self.guiImageDict['easyButton'].get_height()\
                * spacer))
        self.hardButtonRect = self.guiImageDict['hardButton'].get_rect()
        self.hardButtonRect.move_ip((self.width//2 - \
            self.guiImageDict["hardButton"].get_width()//2),
            (self.height - self.guiImageDict['hardButton'].get_height()\
                * (spacer / 3 * 2)))
        self.gyrussButtonRect = self.guiImageDict['gyrussButton'].get_rect()
        self.gyrussButtonRect.move_ip((self.width//2 - \
            self.guiImageDict["gyrussButton"].get_width()//2),
            (self.height - self.guiImageDict['gyrussButton'].get_height()\
                * (spacer/3)))

    def loadSelectionButtons(self):
        #Loads buttons for selecting player character image
        for img in os.listdir(os.path.join("GUI", "SelectionButtons")):
            self.guiImageDict[img] = pygame.image.load(os.path.join("GUI",
                "SelectionButtons", img))
        xBuffer = 75
        yBuffer = -self.guiImageDict['easyButton'].get_height()//2
        buttonWidth = self.guiImageDict['shipButton.png'].get_width()
        buttonHeight = self.guiImageDict['shipButton.png'].get_height()
        yStart = self.easyButtonRect.y - buttonHeight
        self.nyanButtonRect = pygame.Rect(self.width//2 - buttonWidth//2,
            yStart + yBuffer,
            buttonWidth, buttonHeight)
        self.shipButtonRect = pygame.Rect(\
            self.nyanButtonRect.x - xBuffer - buttonWidth, yStart + yBuffer,
            buttonWidth, buttonHeight)
        self.androidButtonRect = pygame.Rect(\
            self.nyanButtonRect.x + xBuffer + buttonWidth, yStart + yBuffer,
            buttonWidth, buttonHeight)
        

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
        self.fontSize = Ship.height//2
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
        self.gyrussPauseMode = 'gyruss pause mode'
        self.gyrussMode = 'gyruss mode'
        self.highScoreNameEntryMode = 'high score name entry'
        self.highScoreScreenMode = 'high scores'
        self.mode = self.menuMode
        self.hardMode = False

    def startNewGame(self, hardMode=False):
        #starts a new game and takes flag for hardMode
        #   in hard mode, barries don't regenerate and player can damage own
        #   barriers
        self.mode = self.pauseMode
        self.playerInitials = ''
        self.isGyruss = False
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
        self.shipGroup.add(Ship(self.shipStartX, self.shipStartY,
            img=self.shipSelection))

    def gyrussStartNewGame(self):
        # Starts a new game in gyruss mode
        self.mode = self.gyrussPauseMode
        self.playerInitials = ''
        self.isGyruss = True
        self.bulletCoolDownTimer = 0
        self.alienBulletTimer = 0

        self.pointsPerKill = 10
        self.playerLevel = 0
        self.playerLives = 3
        self.playerScore = 0
        self.gyrussPopulateWithAliens()
        self.playerPosR = 0.90
        self.shipGroup.add(GyrussShip(self.playerPosR, self.width, self.height,
            img=self.shipSelection))

    def gyrussPopulateWithAliens(self):
        # adds aliens to alienGroup with xy coords in a circular fashion
        alienPosR = .35
        # Add additional aliens with every player level (up to maxExtraAliens)
        maxExtraAliens = 18
        if self.playerLevel <= maxExtraAliens:
            addAliens = self.playerLevel
        else:
            addAliens = maxExtraAliens
        numAliens = 10 + addAliens 
        for alien in range(numAliens):
            # Similar to drawing numbers on a clock, loops through and 
            #   determines alien pos using sin and cos angle vals
            angle = (2*math.pi)*(alien/numAliens)
            alienX = self.width//2 + \
                min(self.width, self.height)//2 * alienPosR * math.cos(angle)
            alienY = self.height//2 - \
                min(self.width, self.height)//2 * alienPosR * math.sin(angle)
            note = random.choice(self.midiScale)
            self.alienGroup.add(Alien(alienX,alienY, note))


#Timerfired functions

    def timerFired(self, dt):
        # Main timer fired which dispatches to mode specific tF
        if self.mode == self.gameMode: self.gameTimerFired(dt)
        elif self.mode == self.gameOverMode: self.gameOverTimerFired(dt)
        elif self.mode == self.menuMode: self.menuTimerFired(dt)
        elif self.mode == self.pauseMode: self.pauseTimerFired(dt)
        elif self.mode == self.gyrussMode: self.gyrussTimerFired(dt)
        elif self.mode == self.gyrussPauseMode: self.gyrussPauseTimerFired(dt)
        elif self.mode == self.highScoreScreenMode: pass
        elif self.mode == self.highScoreNameEntryMode: pass

    def gyrussPauseTimerFired(self, dt):
        pass

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

    def gyrussTimerFired(self, dt):
        # Timer fired for gyruss game
        self.gyrussCheckForNewLevel()
        self.checkGyrussGameOver()

        self.bulletAlienCollisions()
        # checks for player collision with alien bullet. if player has lives 
        #   left will kill and replace with new gyruss ship
        self.alienBulletPlayerCollisions(gyruss=True)
        self.gyrussFireAlienBullets(dt)
        # Fires player bullets into center of screen
        self.bulletFiring(dt, gyruss=True)

        self.shipGroup.update(self.isKeyPressed, self.width, self.height)
        self.alienBulletGroup.update(self.width, self.height)
        self.pitchBulletGroup.update(self.width, self.height)
        self.gyrussCenterBulletKill()

    def gameOverTimerFired(self,dt):
        #Empty all off the groups
        self.alienGroup.empty()
        self.barrierGroups.empty()
        self.alienBulletGroup.empty()
        self.pitchBulletGroup.empty()
        self.shipGroup.empty()

# Helpers in timerFireds

    def gyrussCheckForNewLevel(self):
        # Checks for a new level and calls for a new gyruss level if needed
        if len(self.alienGroup) == 0:
            self.playerLives += 1
            time.sleep(2)
            self.pitchBulletGroup.empty()
            self.alienBulletGroup.empty()
            self.gyrussPopulateWithAliens()
            self.playerLevel += 1

    def gyrussCenterBulletKill(self):
        #removes bullets that have reached the center of the screen
        size = 15
        killZone = pygame.Rect(self.width//2-size, self.height//2-size,
                                2*size, 2*size)
        for bullet in self.pitchBulletGroup:
            if killZone.colliderect(bullet.rect): bullet.kill()


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

    def checkGyrussGameOver(self):
        # Checks for game over conditions in gyruss mode (player has < 0 lives)
        if self.playerLives < 0:
            self.mode = self.gameOverMode



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


    def alienBulletPlayerCollisions(self, gyruss=False):
        # Checks collisions between player and alien bullets, kills player and
        #   takes a life away.
        pygame.sprite.groupcollide(self.shipGroup, self.alienBulletGroup,
            True, True)
        if len(self.shipGroup) == 0:
            self.pitchBulletGroup.empty()
            self.alienBulletGroup.empty()
            time.sleep(1) #If player dies, pause for a second and then respawn
            if not gyruss:
                self.shipGroup.add(Ship(self.shipStartX, self.shipStartY, 
                    img=self.shipSelection))
            else:
                self.shipGroup.add(GyrussShip(self.playerPosR, self.width,
                    self.height, img=self.shipSelection))

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

    def gyrussFireAlienBullets(self, dt):
        # Possibly fire alien bullets every interval, and reset timer
        alienBulletCoolDownTime = 2000
        chanceOfFiring = 5
        self.alienBulletTimer += dt
        if self.alienBulletTimer > alienBulletCoolDownTime:
            self.alienBulletTimer = 0
            for alien in self.alienGroup:
                coinFlip = random.randint(0,chanceOfFiring)
                if coinFlip == chanceOfFiring:
                    vector = (0,1)
                    shipX, shipY = self.shipGroup.sprites()[0].getPos()
                    #aim at player
                    vector = self.getBulletVector(alien.x,alien.y,
                                                        shipX, shipY)
                    self.alienBulletGroup.add(Bullet(alien.x,alien.y, vector))

    def getBulletVector(self, shooterX, shooterY, targetX, targetY):
        #return (dx,dy) vector tuple for bullet creation, given xy coords of
        #   shooter and their target
        dx0 = targetX - shooterX
        dy0 = targetY - shooterY
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


    def bulletFiring(self,dt, gyruss=False):
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
                if not gyruss:
                    self.firePitchBullet(self.pitchObject.getNote())
                else:
                    # If in gyruss mode, aim bullets at center of screen
                    vector = self.getBulletVector(self.shipGroup.sprites()[0].x,
                        self.shipGroup.sprites()[0].y, 
                        self.width//2, self.height//2)
                    self.firePitchBullet(self.pitchObject.getNote(), vector)
                #reset cool down timer
                self.bulletCoolDownTimer = 0

    def firePitchBullet(self, midiVal, vector=(0,-1)):
        # Given midi val will fire a pitch bullet from ship pos
        self.pitchBulletGroup.add(PitchBullet(self.shipGroup.sprites()[0].x,
                                    self.shipGroup.sprites()[0].y,
                                    vector, midiVal))

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


## Keypressed

    def keyPressed(self, keyCode, modifier):
        #Key pressed dispatch
        if self.mode == self.gameMode: self.gameKeyPressed(keyCode, modifier)
        elif self.mode == self.gameOverMode: self.gameOverKeyPressed(keyCode,
                                                            modifier)
        elif self.mode == self.menuMode: pass
        elif self.mode == self.pauseMode: self.pauseKeyPressed(keyCode,
            modifier)
        elif self.mode == self.gyrussMode: self.gyrussKeyPressed(keyCode,
            modifier)
        elif self.mode == self.gyrussPauseMode: self.gyrussPauseKeyPressed(\
            keyCode, modifier)
        elif self.mode == self.highScoreNameEntryMode:
            self.highScoreNameEntryKeyPressed(keyCode, modifier)
        elif self.mode == self.highScoreScreenMode:
            self.highScoreScreenKeyPressed(keyCode, modifier)

    def highScoreNameEntryKeyPressed(self, keyCode, modifier):
        # Manages keyboard entry of initials if player has new high score
        if len(self.playerInitials) < 3:
            #pygame key constants translate to key ascii vals
            if ord('a') <= keyCode <= ord('z'):
                self.playerInitials += chr(keyCode)
        if keyCode == pygame.K_BACKSPACE:
            #delete last letter
            self.playerInitials = self.playerInitials[:-1]
        if len(self.playerInitials) > 0:
            #only go ahead if something was entered
            if keyCode == pygame.K_RETURN:
                for i in range(len(self.highScoreContents)):
                    if self.playerScore > int(self.highScoreContents[i][1]):
                        self.highScoreContents.insert(i, [self.playerInitials,
                            str(self.playerScore)])
                        break
                self.highScoreContents.pop() #only keep ten scores
                self.mode = self.highScoreScreenMode

    def highScoreScreenKeyPressed(self, keyCode, modifier):
        # Go to menu when any key is pressed
        self.mode = self.menuMode

    def gyrussPauseKeyPressed(self, keyCode, modifier):
        # pause keypressed method for gyruss game mode
        # Add whole screen to list of rects to be updated in the game's dirty
        #   rect update
        self.dirtyRects.append(pygame.Rect(0,0,self.width,self.height))
        # When any key is pressed, go back to game
        self.mode = self.gyrussMode

    def pauseKeyPressed(self, keyCode, modifier):
        # Pause keypressed for normal game
        # Add whole screen to list of rects to be updated in the game's dirty
        #   rect update
        #If any key is pressed, go to gameMode
        self.dirtyRects.append(pygame.Rect(0,0,self.width,self.height))
        self.mode = self.gameMode

    def gameOverKeyPressed(self, keyCode, modifier):
        # Key pressed for gameover mode
        modeChangeFlag = False # Track whether a mode change has been called
        if self.hardMode and not self.isGyruss:
            # Only go to name entry and score saving for standard hard mode
            for nameAndScore in self.highScoreContents:
                # Check if player score is higher than any current scores
                if self.playerScore > int(nameAndScore[1]):
                    # If so go to name entry
                    self.mode = self.highScoreNameEntryMode
                    modeChangeFlag = True
                    break
        if not modeChangeFlag:
            # Don't do this if already called for name entry mode
            self.mode = self.highScoreScreenMode

    def gameKeyPressed(self, keyCode, modifier):
        ## NB: player movement handled in timerfired
        if keyCode == pygame.K_p:
            self.mode = self.pauseMode
        elif keyCode == pygame.K_c:
            self.cMajScale.play()

    def gyrussKeyPressed(self, keyCode, modifier):
        ## NB: player movement handled in timerfired
        if keyCode == pygame.K_p:
            self.mode = self.gyrussPauseMode
        elif keyCode == pygame.K_c:
            self.cMajScale.play()



## Mouse Pressed
        
    def mousePressed(self, x, y):
        # Mouse currently only used in menu mode
        if self.mode == self.menuMode: self.menuMousePressed(x,y)
        else: pass

    def menuMousePressed(self, x, y):
        #check if clicked inside buttons
        # Following line included to add whole screen to list of dirty rects
        # to be updated when going to game which only updates dirty rects:
        self.dirtyRects.append(pygame.rect.Rect(0,0,self.width, self.height))
        if self.easyButtonRect.collidepoint(x,y):
            self.hardMode = False
            self.startNewGame(self.hardMode)
        elif self.hardButtonRect.collidepoint(x,y):
            self.hardMode = True
            self.startNewGame(self.hardMode)
        elif self.gyrussButtonRect.collidepoint(x,y):
            self.gyrussStartNewGame()
        elif self.shipButtonRect.collidepoint(x,y):
            self.shipSelection = "ship.png"
        elif self.nyanButtonRect.collidepoint(x,y):
            self.shipSelection = "nyan.png"
        elif self.androidButtonRect.collidepoint(x,y):
            self.shipSelection = "android.png"
        

## Redraw All

    def redrawAll(self, screen):
        # Redraw all dispatch
        if self.mode == self.gameMode: self.gameRedrawAll(screen)
        elif self.mode == self.gameOverMode: self.gameOverRedrawAll(screen)
        elif self.mode == self.pauseMode: self.pauseRedrawAll(screen)
        elif self.mode == self.menuMode: self.menuRedrawAll(screen)
        elif self.mode == self.gyrussMode: self.gyrussRedrawAll(screen)
        elif self.mode == self.gyrussPauseMode: 
            self.gyrussPauseRedrawAll(screen)
        elif self.mode == self.highScoreScreenMode:
            self.highScoreScreenRedrawAll(screen)
        elif self.mode == self.highScoreNameEntryMode:
            self.highScoreNameEntryRedrawAll(screen)

    def highScoreScreenRedrawAll(self, screen):
        # Redraw all for highscore screen
        yBuffer = 50
        leftBuffer = 200
        rightBuffer = 200
        hsText = self.bigGameFont.render('HIGH SCORES (HARD MODE ONLY)',
            True, self.fontColor)
        titleDest = (self.width//2 - hsText.get_width()//2, yBuffer)
        screen.blit(hsText, titleDest)
        for i in range(len(self.highScoreContents)):
            # blit all the high scores in order.
            # Determine values based on line number
            y = titleDest[1] + (hsText.get_height() + yBuffer) * (i + 1)
            initialsText = self.bigGameFont.render(self.highScoreContents[i][0],
                True, self.fontColor)
            scoreText = self.bigGameFont.render(self.highScoreContents[i][1],
                True, self.fontColor)
            initialsX = leftBuffer
            scoreX = self.width - rightBuffer - scoreText.get_width()
            screen.blit(initialsText, (initialsX, y))
            screen.blit(scoreText, (scoreX, y))
        pygame.display.flip() # no reason to only dirty rect update

    def highScoreNameEntryRedrawAll(self, screen):
        # redraw all for name entry screen. doesn't use dirty rect update
        titleText = self.bigGameFont.render('NEW HIGH SCORE',
            True, self.fontColor)
        instructionText = self.bigGameFont.render('ENTER YOUR INITIALS:', True,
            self.fontColor)
        hitEnterText = self.bigGameFont.render('PRESS ENTER WHEN DONE', True,
            self.fontColor)
        playerInitialsText = self.bigGameFont.render(\
            self.playerInitials.upper(), True, self.fontColor)

        yBuffer = 50
        numBuffers = 1
        screen.blit(titleText,
            (self.width//2 - titleText.get_width()//2,yBuffer * numBuffers))
        numBuffers += 1
        screen.blit(instructionText,
            (self.width//2 - instructionText.get_width()//2,
                yBuffer * numBuffers + titleText.get_height()))
        numBuffers += 1
        screen.blit(playerInitialsText,
            (self.width//2 - playerInitialsText.get_width()//2,
                yBuffer * numBuffers + titleText.get_height() * 2))
        screen.blit(hitEnterText,
            (self.width//2 - hitEnterText.get_width()//2,
                self.height - yBuffer - hitEnterText.get_height() * 2))

        pygame.display.flip()

    def gyrussPauseRedrawAll(self, screen):
        # redraw all for gyruss pause screen.
        pauseImage = self.guiImageDict['gyrussHelpScreen']
        screen.blit(pauseImage, (self.width//2 - pauseImage.get_width()//2,
            self.height//2 - pauseImage.get_height()//2))
        pygame.display.flip()

    def gyrussRedrawAll(self, screen):
        # redraw all for gyruss game.
        screen.blit(self.background, (0,0))
        self.dirtyRects.extend(self.shipGroup.draw(screen))
        self.dirtyRects.extend(self.pitchBulletGroup.draw(screen))
        self.dirtyRects.append(self.drawScoreText(screen))
        self.dirtyRects.append(self.drawLivesText(screen))
        self.dirtyRects.extend(self.alienGroup.draw(screen))
        self.dirtyRects.extend(self.alienBulletGroup.draw(screen))

        # Only updates dirty rects passed into update as list.
        pygame.display.update(self.dirtyRects)
        self.dirtyRects.clear() # clear out list for next frame

    def pauseRedrawAll(self, screen):
        # redraw all for standard pause screen
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
        #redraw all for game over screen
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
        #redraw all for menu screen
        screen.fill((0,0,0))
        bufferY = 30
        screen.blit(self.guiImageDict['title'],
            (self.width//2 - self.guiImageDict['title'].get_width()//2,
                bufferY))
        screen.blit(self.guiImageDict['easyButton'], self.easyButtonRect)
        screen.blit(self.guiImageDict['hardButton'], self.hardButtonRect)
        screen.blit(self.guiImageDict['gyrussButton'], self.gyrussButtonRect)
        #checks which button should be highlighted:
        self.drawSelectionButtons(screen) 
        self.charSelectText(screen)
        pygame.display.flip() #Update all, not just dirty rects

##Helper method to draw ship selection buttons on main screen:

    def drawSelectionButtons(self, screen):
        #displays button and highlight if selected
        if self.shipSelection == "ship.png":
            screen.blit(self.guiImageDict['shipButton1.png'],
                self.shipButtonRect)
        else:
            screen.blit(self.guiImageDict['shipButton.png'],
                self.shipButtonRect)
        if self.shipSelection == "nyan.png":
            screen.blit(self.guiImageDict['nyanButton1.png'],
                self.nyanButtonRect)
        else:
            screen.blit(self.guiImageDict['nyanButton.png'],
                self.nyanButtonRect)
        if self.shipSelection == "android.png":
            screen.blit(self.guiImageDict['androidButton1.png'],
                self.androidButtonRect)
        else:
            screen.blit(self.guiImageDict['androidButton.png'],
                self.androidButtonRect)


## Redraw helpers for screen text:
    def charSelectText(self, screen):
        # Text for title screen
        text = "CHOOSE YOUR SHIP"
        textSurf = self.bigGameFont.render(text, True, self.fontColor)
        yBuffer = 50
        dest = self.width//2 - textSurf.get_width()//2, \
            self.shipButtonRect.y - textSurf.get_height() - yBuffer
        screen.blit(textSurf, dest)

    def drawScoreText(self, screen):
        # draws score text at bottom left in game
        text = "SCORE: %d" % self.playerScore
        dest = self.textSideBuffer, self.bottomTextY
        textSurf = self.gameFont.render(text, True, self.fontColor)
        dirty = screen.blit(textSurf, dest)
        return dirty

    def drawLivesText(self, screen):
        # Draws lives text at bottom right in game
        text = "LIVES: %d" % self.playerLives
        textSurf = self.gameFont.render(text, True, self.fontColor)
        bottomTextX = self.width - textSurf.get_width() - self.textSideBuffer
        return screen.blit(textSurf, (bottomTextX, self.bottomTextY))


## Helpers for normal game alien movement

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
        # Puts aliens in top left corner of screen for standard game
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

## Barrier building helpers: 

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
        writeFile(self.hsPath, tokenizeHighScores(self.highScoreContents))

## Some functions/helpers to manage highscores/file IO
# From https://www.cs.cmu.edu/~112/notes/notes-strings.html
def readFile(path):
    with open(path, "rt") as f:
        return f.read()

def writeFile(path, contents):
    with open(path, "wt") as f:
        f.write(contents)

def emptyHighScores():
    # Generates empty base contents for highscore text file.
    oneLine = "---@0\n"
    return oneLine * 10

def tokenizeHighScores(highScoreList):
    # takes 2d list contents of highscore and combines each of the names and
    #   and scores into a readable/writeable format as: [name]@[score]
    result=''
    for nameAndScore in highScoreList:
        result += nameAndScore[0] + '@' + str(nameAndScore[1]) + '\n'
    return result


if __name__ == "__main__":
    SingingSpaceInvaders().run()
