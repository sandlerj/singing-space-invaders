import pygame, os

class Brick(pygame.sprite.Sprite):
    @staticmethod
    def init(screenWidth, screenHeight, scaleFactor=1):
        # Loads images into dictionaries and scales ahead of use
        # Load and scale images at the samet time. Three separate libraries for
        #   main bricks and corners. Corners need to be rotated 180 for
        #   interior edges
        Brick.imageLib = getImagesAndScale("Photos" + os.sep + \
            "nonCorner", scaleFactor)
        Brick.imageLibLeft = getImagesAndScale("Photos" + os.sep + \
            "leftBrickCorner", scaleFactor)
        Brick.imageLibRight = getImagesAndScale("Photos" os.sep + \
            "rightBrickCorner", scaleFactor)

    def __init__(self, x, y, brickType):
        self.x = x
        self.y = y
        self.brickType = brickType
        self.imgLib = self.getLib()
        self.timesHit = 0
        self.image = self.imgLib[self.timesHit]
        self.updateRect()

    def getLib(self):
        if self.brickType == 0:
            return Brick.imageLib
        elif self.brickType == 1:
            return Brick.imageLibLeft
        elif self.brickType == 2:
            return Brick.imageLibRight

    def updateRect(self):
        self.width, self.height = self.image.get_size()
        # Updates sprite rect for blit
        self.rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2,
                                self.width, self.height)

    def update(self):
        # Check if brick should be dead. Otherwise update image if necessary
        if self.timesHit >= 4:
            self.kill()
        else:
            self.image = self.imgLib[self.timesHit]
            self.updateRect()s

    def getHit(self):
        self.timesHit += 1

def getImagesAndScale(path, scale):
    imageDict = {}
    for img in os.listdir(path):
        #assigns key of first char in file name, which is number of times
        #   brick has been hit, to loaded and scaled pygame image surface
        imageDict[img[0]] = pygame.transform.rotozoom(pygame.image.load(path \
                            + os.sep + img), 0, scale)
    return imageDict