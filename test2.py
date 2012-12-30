import pygame
import math
#necessary pygame initializing
pygame.init()


#create a varible for degrees pf rotation
degree = 0
size = 50

class Circle(pygame.sprite.Sprite):
    
    def __init__(self,center=(0,0),radius=50):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface((2*radius, 2*radius))
        self.image.set_colorkey(BLACK) # make the black background transparent
        self.rect = self.image.get_rect()
        pygame.draw.circle(self.image, WHITE, self.rect.center, radius)
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.radius = radius
        self.rect.center = center

class Triangle(pygame.sprite.Sprite):
    
    def __init__(self,circle,degree,size):
        # A launcher will be a triangle that sits on the surface (maybe a bit beneath the surface, as the base
        # of the triangle will be flat but the asteroid surface will be curved) of an asteroid and will be
        # able to fire missiles.
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.circle = circle
        self.image = pygame.Surface((size, size))
        self.image.set_colorkey(BLACK) # make the black background transparent
        pygame.draw.polygon(self.image, (100,100,100), [(0,size),(size/2,0),(size,size)])
        #rotate surf by DEGREE amount degrees
        self.image =  pygame.transform.rotate(self.image, degree)
        #get the rect of the rotated surface
        self.rect = self.image.get_rect()
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        (x,y) = circle.rect.center
        (X,Y) = ((x - circle.radius * math.sin(degree * math.pi / 180.0)),(y - circle.radius * math.cos(degree * math.pi / 180.0)))
        self.rect.center = (X,Y)
        

# set up the window
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)


screen = pygame.display.set_mode((200, 200), 0, 32)    # Can use pygame.FULLSCREEN instead of 0
clock = pygame.time.Clock()
background = pygame.Surface(screen.get_size())  # Create empty pygame surface
background.fill(BLACK)     # Fill the background white color (red,green,blue)
background = background.convert()  # Convert Surface to make blitting faster
screen.blit(background, (0, 0))
gameRect = screen.get_rect()        
        
        
circleGroup = pygame.sprite.Group()
Circle.groups = circleGroup

triangleGroup = pygame.sprite.Group()
Triangle.groups = triangleGroup
      
degree = 180  
circle = Circle(center=(100,100),radius=30)
triangle = Triangle(circle,degree,40)


        
while True:
    
    msecs = clock.tick(1) 
    degree += 1
    
    circleGroup.clear(screen,background)
    triangleGroup.clear(screen,background)
    
    
    triangleGroup.draw(screen)
    circleGroup.draw(screen)

    
    # draw the window onto the screen
    pygame.display.update() 