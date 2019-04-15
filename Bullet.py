import pygame, os

class Bullet(pygame.sprite.Sprite):
    @staticmethod
    def init(screenWidth, screenHeight):
        Bullet.width = screenWidth//50
        Bullet.height = screenWidth//50 * 3
        Bullet.image = pygame.Surface((Bullet.width,Bullet.height))
        Bullet.image.fill((255,255,255))


    def __init__(self, x, y, vector):
        super().__init__()
        self.x = x
        self.y = y
        self.image = Bullet.image
        self.width, self.height = self.image.get_size()
        self.rect = self.image.get_rect()
        self.dx = vector[0]
        self.dy = vector[1]
        self.speed = 10
        self.updateRect()

    def updateRect(self):
        self.rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2,
                                self.x + self.width//2, self.y + self.height//2)

    def update(self, screenWidth, screenHeight):
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        self.updateRect()
        if self.x < 0 or self.x > screenWidth or self.y < 0 or \
            self.y >screenHeight:
            self.kill()
