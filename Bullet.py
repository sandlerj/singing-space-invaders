import pygame, os, copy, math
from numpy import real
#Bullet sprite and subclasee PitchBullet

class Bullet(pygame.sprite.Sprite):
    # Bullet base class, used by aliens and subclass used by ship
    @staticmethod
    def init(screenWidth, screenHeight):
        #initialize bullet image
        Bullet.width = screenWidth//100
        heightWidthRatio = 3
        Bullet.image = pygame.Surface((Bullet.width,
                                        Bullet.width * heightWidthRatio),
                                        pygame.SRCALPHA)
        #Use of SRCALPHA to create alpha channel for rotation solution from
        # jsbueno on stackoverflow:
        # <https://stackoverflow.com/questions/40949613/how-to-rotate-a-surface-
        # in-pygame-without-changing-its-shape>
        Bullet.image.fill((255,255,255))


    def __init__(self, x, y, vector, color=None):
        # Set up bullet position and direction
        super().__init__()
        self.x = x
        self.y = y
        self.image = copy.copy(Bullet.image) #prevent aliasing
        # Based on vector (angle via unit circle point coords), rotate image
        #   to appropriate angle using inverse tangent
        if color != None:
            self.image.fill(color)
        self.image = pygame.transform.rotate(self.image,
            math.degrees(math.atan2(*vector)))
        self.width, self.height = self.image.get_size()
        self.rect = self.image.get_rect()
        self.dx = vector[0]
        self.dy = vector[1]
        self.speed = 10
        self.mask = pygame.mask.from_surface(self.image)
        self.updateRect() #update rect for sprite blitting

    def updateRect(self):
        # Updates sprite rect for blit
        self.rect = pygame.Rect(self.x - self.width//2, self.y - self.height//2,
                                self.width, self.height)

    def update(self, screenWidth, screenHeight):
        # Move bullet, delete if off screen
        self.x += self.dx * self.speed
        self.y += self.dy * self.speed
        # round pos to int because whole pixels
        self.x, self.y = (roundHalfUp((self.x).real), 
                            roundHalfUp((self.y).real))
        self.updateRect()

        if self.x < 0 or self.x > screenWidth or self.y < 0 or \
            self.y >screenHeight:
            self.kill()

    def updateVector(self, vector):
        #Updates dx,dy with new vector given
        self.dx = vector[0]
        self.dy = vector[1]

class PitchBullet(Bullet):
    # Subclass of bullet which has note attribute, which also determiens color
    def __init__(self, x, y, vector, note):
        #takes pitch as midi val
        super().__init__(x,y,vector)
        twelveToneScaleLen = 12
        self.note = note % twelveToneScaleLen #storing note as pitch w/o octave, 
        # ranging 0 - 11, where 0 is C and 11 is B
        self.image.fill((colorByNote(self.note)))
        super().__init__(x,y,vector, color=colorByNote(self.note))



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

def roundHalfUp(d):
    # From: https://www.cs.cmu.edu/~112/notes/notes-variables-and-functions.html
    # Round to nearest with ties going away from zero.
    # You do not need to understand how this function works.
    import decimal
    rounding = decimal.ROUND_HALF_UP
    return int(decimal.Decimal(d).to_integral_value(rounding=rounding))


def distance(x0,y0,x1,y1):
    result = ((x1-x0)**2 + (y1-y0)**2)**0.5
    return result
