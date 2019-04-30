#Joseph Sandler, jsandler, Section B
## The Ship Sprite
#Made with minimal references to Lukas Peraza's pygame templates;
# HOWEVER, not at all directly copied or using his GameObject
# https://qwewy.gitbooks.io/pygame-module-manual/tutorials/using-sprites.html


import pygame, os, math, copy

class Ship(pygame.sprite.Sprite):
    # Player ship class from pygame sprite
    @staticmethod
    def init(screenWidth, screenHeight, scaleFactor=20):
        #loads ships and scales to screen
        # Scale factor determines size based on width
        # Ship image from https://www.kisspng.com/
        #   png-galaga-galaxian-golden-age-of-arcade-video-games-a-1052746/
        #   download-png.html
        Ship.imageDict = {}
        # Ship.image = pygame.image.load(os.path.join("Photos",
        #                                          "ship.png")).convert_alpha()
        # Width/height ratio used to scale ship based primarily on width
        # but maintain aspect ratio

        for img in os.listdir(os.path.join("Photos", "Ships")):
            tmpImage = pygame.image.load(os.path.join("Photos", "Ships", img))\
                .convert_alpha()
            widthHeightRatio = tmpImage.get_width() / tmpImage.get_height()
            Ship.imageDict[img] = pygame.transform.scale(tmpImage,
                    (int(screenWidth//scaleFactor * widthHeightRatio),
                        screenWidth//scaleFactor))



        # Ship width/height sometimes used as a unit in mainfile. Set to be 
        #   default image
        Ship.width, Ship.height = Ship.imageDict['ship.png'].get_size()


    def __init__(self, x, y, img='ship.png'):
        # initialize ship
        super().__init__()
        self.x = x
        self.y = y
        self.image = Ship.imageDict[img]
        self.width, self.height = self.image.get_size()
        self.rect = self.image.get_rect()
        self.updateRect()
        self.dx = 0 #initial dx
        self.speed = 10 # base speed

    def updateRect(self):
        # Updates sprite rect for blit
        self.rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2,
                                self.width, self.height)

    def update(self, keysDown, screenWidth, screenHeight):
        # Steady movement of sprite if keys held
        if keysDown(pygame.K_LEFT) and keysDown(pygame.K_RIGHT):
            #don't move if both keys held
            self.dx = 0
        elif keysDown(pygame.K_LEFT):
            self.dx = -1
        elif keysDown(pygame.K_RIGHT):
            self.dx = 1
        else:
            #ensure dx is 0 if neither left or right held
            self.dx = 0

        self.x += self.speed * self.dx #move sprite
        #bounds check
        if self.x + self.width//2 >= screenWidth or self.x - self.width//2 <= 0:
            self.x -= self.speed * self.dx
        self.updateRect() #update for blitting

    def getPos(self):
        #returns tuple of x,y coords
        return (self.x, self.y)

class GyrussShip(Ship):
    #Ship used for gyruss game
    def __init__(self, r, screenWidth, screenHeight, img='ship.png'):
        self.startAngle = 90
        self.angle = math.radians(self.startAngle)
        self.shipRadius = r
        self.x = screenWidth//2 + min(screenWidth, screenHeight) * \
            self.shipRadius * math.cos(self.angle)
        self.y = screenHeight//2 + min(screenWidth, screenHeight) * \
            self.shipRadius * math.sin(self.angle)
        super().__init__(self.x,self.y,img)
        self.baseImage = copy.copy(self.image)

    def update(self, keysDown, screenWidth, screenHeight):
        angleIncrement = math.radians(5)
        dA = 0
        if keysDown(pygame.K_LEFT) and keysDown(pygame.K_RIGHT):
            dA = 0
        elif keysDown(pygame.K_LEFT):
            dA += angleIncrement
        elif keysDown(pygame.K_RIGHT):
            dA -= angleIncrement

        self.angle += dA
        self.x = screenWidth//2 + min(screenWidth, screenHeight) * self.shipRadius\
            * math.cos(self.angle)
        self.y = screenHeight//2 + min(screenWidth, screenHeight) * self.shipRadius\
            * math.sin(self.angle)
        self.image = pygame.transform.rotate(self.baseImage, 
            -(math.degrees(self.angle) - self.startAngle))
        self.updateRect()
