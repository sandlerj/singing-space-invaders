#Joseph Sandler, jsandler, Section B
## The Ship Sprite
#Made with minimal references to Lukas Peraza's pygame templates;
# HOWEVER, not at all directly copied or using his GameObject
# https://qwewy.gitbooks.io/pygame-module-manual/tutorials/using-sprites.html


import pygame, os

class Ship(pygame.sprite.Sprite):
    # Player ship class from pygame sprite
    @staticmethod
    def init(screenWidth, screenHeight, scaleFactor=15):
        #loads ship and scales to screen
        # Scale factor determines size based on width
        # Ship image from https://www.kisspng.com/
        #   png-galaga-galaxian-golden-age-of-arcade-video-games-a-1052746/
        #   download-png.html
        Ship.image = pygame.image.load(os.path.join("Photos",
                                                 "ship.png")).convert_alpha()
        # Width/height ratio used to scale ship based primarily on width
        # but maintain aspect ratio
        widthHeightRatio = Ship.image.get_width() / Ship.image.get_height()

        Ship.image = pygame.transform.scale(Ship.image,
                    (int(screenWidth//scaleFactor * widthHeightRatio),
                        screenWidth//scaleFactor))


    def __init__(self, x, y):
        # initialize ship
        super().__init__()
        self.x = x
        self.y = y
        self.image = Ship.image
        self.width, self.height = self.image.get_size()
        self.rect = self.image.get_rect()
        self.updateRect()
        self.dx = 0 #initial dx
        self.speed = 10 # base speed

    def updateRect(self):
        # Updates sprite rect for blit
        self.rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2,
                                self.x + self.width//2, self.y + self.height//2)

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
