## Joseph Sandler jsandler Section B
## Alien Class for Singing Space Invaders

import pygame

class Alien(pygame.sprite.Sprite):
    @staticmethod
    def init(screenWidth, screenHeight):
        pass

    def __init__(self, x, y, note):
        super().__init__()
        self.x = x
        self.y = y
        self.note = note
        self.image = ???
        self.width, self.height = self.image.get_size()
        self.rect = self.image.get_rect()

    def updateRect(self):
        # Updates sprite rect for blit
        self.rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2,
                                self.x + self.width//2, self.y + self.height//2)
