#Joseph Sandler, jsandler, Section B

import pygame, os, copy
#Bullet sprite and subclasee PitchBullet

class Bullet(pygame.sprite.Sprite):
    # Bullet base class, used by aliens and subclass used by ship
    @staticmethod
    def init(screenWidth, screenHeight):
        #initialize bullet image
        Bullet.width = screenWidth//100
        heightWidthRatio = 3
        Bullet.image = pygame.Surface((Bullet.width,
                                        Bullet.width * heightWidthRatio))
        Bullet.image.fill((255,255,255))


    def __init__(self, x, y, vector):
        # Set up bullet position and direction
        super().__init__()
        self.x = x
        self.y = y
        self.image = copy.copy(Bullet.image) #prevent aliasing
        self.width, self.height = self.image.get_size()
        self.rect = self.image.get_rect()
        self.dx = vector[0]
        self.dy = vector[1]
        self.speed = 10
        self.updateRect() #update rect for sprite blitting

    def updateRect(self):
        # Updates sprite rect for blit
        self.rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2,
                                self.width, self.height)

    def update(self, screenWidth, screenHeight):
        # Move bullet, delete if off screen
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        self.updateRect()
        if self.x < 0 or self.x > screenWidth or self.y < 0 or \
            self.y >screenHeight:
            self.kill()

class PitchBullet(Bullet):
    # Subclass of bullet which has note attribute, which also determiens color
    def __init__(self, x, y, vector, note):
        #takes pitch as midi val
        super().__init__(x,y,vector)
        twelveToneScaleLen = 12
        self.note = note % twelveToneScaleLen #storing note as pitch w/o octave, 
        # ranging 0 - 11, where 0 is C and 11 is B
        self.image.fill((colorByNote(self.note)))

def colorByNote(note):
    # Determine color based on pitch class. White color pitches included for
    # proper indexing into list by valid notes using actual midi val mod 11,
    # as game currently only uses C major scale
    listOfColors = [(255, 0, 0),    # C  red
                    (255,255,255),  # C# white (unused)       
                    (255, 127, 0),  # D orange
                    (255,255,255),  # D# white (unused)
                    (255, 255, 0),  # E  yellow
                    (0, 255, 0),    # F  green
                    (255,255,255),  # F# white (unused)
                    (0, 127, 255),  # G  lighter blue
                    (255,255,255),  # G# white (unused)
                    (75, 0, 130),   # A  indigo
                    (255,255,255),  # A# white (unused)
                    (255, 0, 255)   # B  fuschia
                    ]
    return listOfColors[note] #return color based on index
