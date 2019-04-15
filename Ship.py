## The Ship Sprite
#Made with some reference to Lukas Peraza's pygame templates:


import pygame, os

class Ship(pygame.sprite.Sprite):
    @staticmethod
    def init(screenWidth, screenHeight):
        #loads ship and scales to screen
        # Ship image from https://www.kisspng.com/
        #   png-galaga-galaxian-golden-age-of-arcade-video-games-a-1052746/
        #   download-png.html
        Ship.image = pygame.image.load(os.path.join("Photos",
                                                 "ship.png")).convert_alpha()
        widthHeightRatio = Ship.image.get_width() / Ship.image.get_height()

        scaleFactor = 15 
        Ship.image = pygame.transform.scale(Ship.image,
                    (int(screenWidth//scaleFactor * widthHeightRatio),
                        screenWidth//scaleFactor))


    def __init__(self, x, y):
        super().__init__()
        self.x = x
        self.y = y
        self.image = Ship.image
        self.width, self.height = self.image.get_size()
        self.rect = self.image.get_rect()
        self.updateRect()
        self.dx = 0
        self.speed = 10

    def updateRect(self):
        self.rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2,
                                self.x + self.width//2, self.y + self.height//2)

    def update(self, keysDown, screenWidth, screenHeight):
        if keysDown(pygame.K_LEFT) and keysDown(pygame.K_RIGHT):
            self.dx = 0
        elif keysDown(pygame.K_LEFT):
            self.dx = -1
        elif keysDown(pygame.K_RIGHT):
            self.dx = 1
        else:
            self.dx = 0

        self.x += self.speed * self.dx
        if self.x + self.width//2 >= screenWidth or self.x - self.width//2 <= 0:
            self.x -= self.speed * self.dx
        self.updateRect()
