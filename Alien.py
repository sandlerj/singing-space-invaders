## Joseph Sandler jsandler Section B
## Alien Class for Singing Space Invaders
"""
Alien sprite images originally designed by Tomohiro Nishikado for game Space
Invaders. Sprite images take from:
https://vignette.wikia.nocookie.net/villains/images/9/9b/Spaceinvaders.png
"""

import pygame, os


class Alien(pygame.sprite.Sprite):
    @staticmethod
    def init(screenWidth, screenHeight, scaleFactor=30):
        #Load and scale all of the alien images once
        Alien.alienImages = {}
        Alien.width = Alien.height = screenWidth//scaleFactor
        for img in os.listdir(os.path.join("Photos", "Aliens")):
            tmpImage = pygame.image.load(os.path.join("Photos", "Aliens", img))
            Alien.alienImages[img] = pygame.transform.scale(tmpImage,
                (Alien.width, Alien.height))
    @staticmethod
    def getImageFromNote(note):
        # Returns proper image for alien based on note of C major scale as midi
        # val. If invalid input (note not in scale), will return a white surface
        note = note%12 #ensures note has been reduced to 0 - 11
        for key in Alien.alienImages.keys():
            if key.startswith(str(note)):
                return Alien.alienImages[key]
        #otherwise, white rect surface (scaled to alien size
        width, height = Alien.alienImages[list(\
            Alien.alienImages.keys())[0]].get_size()
        surf = pygame.Surface((width, height))
        surf.fill((255,255,255)) # white surface
        return surf

    def __init__(self, x, y, note):
        super().__init__()
        self.x = x
        self.y = y
        self.note = note
        self.image = Alien.getImageFromNote(self.note)
        self.width, self.height = self.image.get_size()
        self.rect = self.image.get_rect()
        self.updateRect()

    def updateRect(self):
        # Updates sprite rect for blit
        self.rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2,
                                self.x + self.width//2, self.y + self.height//2)
