import pygame, sys, random, time
import pygame.locals as var

# set up pygame
pygame.init()

# Set the maximum fps
clock = pygame.time.Clock()

# colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


# set up the window
global windowSurface
windowSurface = pygame.display.set_mode((1200, 650), 0, 32)
pygame.display.set_caption('Moving circle!!')
rect = windowSurface.get_rect()
clock.tick()

class Target():
    def __init__(self,x_vel,y_vel,colour,background,rect):
        (self.x_vel,self.y_vel) = (x_vel,y_vel) # vel is pixels per second
        self.internal_clock = pygame.time.Clock()
        self.internal_clock.tick()
        self.colour = colour
        self.background = background
        self.rect = rect

    def get_x(self,msecs):
        x = self.rect.centerx + self.x_vel * msecs / 1000.0
        return x
        # Code here to determine edge of screen behaviour
    def get_y(self,msecs):
        global a
        y = self.rect.centery + self.get_y_vel(msecs) * msecs / 1000.0 + 0.5 * a * (msecs / 1000.0) ** 2
        return y
    def get_y_vel(self,msecs):
        global a
        y_vel = self.y_vel + a * ( msecs / 1000.0)
        return y_vel
    
    def update(self,msecs):
        (self.rect.centerx,self.rect.centery,self.y_vel) = (self.get_x(msecs),self.get_y(msecs),self.get_y_vel(msecs))
        # The bounce properties
        if self.rect.centery < 0 or self.rect.centery > self.background.height:
            self.y_vel = 0.9 * self.y_vel
            self.y_vel = -self.y_vel
            if self.rect.centery < 0 : self.rect.centery = 0
            if self.rect.centery > self.background.height : self.rect.centery = self.background.height
        if self.rect.centerx < 0 or self.rect.centerx > self.background.width:
            self.x_vel = 0.9 * self.x_vel
            self.x_vel = -self.x_vel
            if self.rect.centerx < 0: self.rect.centerx = 0
            if self.rect.centerx > self.background.width: self.rect.centerx = self.background.width
    def clone(self):
        self.colour = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
        global targets
        global windowSurface
        circle_rect = pygame.draw.circle(windowSurface, BLACK, (int(self.rect.centerx),int(self.rect.centery)), 30, 0)
        targets.append(Target(-self.x_vel,self.y_vel,self.colour,windowSurface.get_rect(),circle_rect))
        
    def clickCheck(self,pos):
        if self.rect.collidepoint(pos):

            return True
        return False
            



RAND_COLOUR = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
# Acceleration
global a
a = -170
global targets
targets = []
(initial_x,initial_y,x_vel,y_vel,colour) = (0,0,300,200,RAND_COLOUR)
circle_rect = pygame.draw.circle(windowSurface, colour, (int(initial_x),rect.bottom - int(initial_y)), 30, 0) 
targets.append(Target(x_vel,y_vel,colour,rect,circle_rect))
# run the game loop
while True:
    for event in pygame.event.get():
        if event.type == QUIT:
            pygame.quit()
            sys.exit()
        elif event.type == MOUSEBUTTONDOWN:
            pos = pygame.mouse.get_pos()
            for target in targets:
                if target.clickCheck(pos):
                    target.clone()

    # draw the white background onto the surface
    windowSurface.fill(WHITE)            
    
    msecs = clock.get_time()
    
    # draw targets onto the surface
    for target in targets:
        target.update(msecs)
        pygame.draw.circle(windowSurface, target.colour, (int(target.rect.centerx),int(target.rect.centery)), 30, 0)            


    
    # draw the window onto the screen
    pygame.display.update()
    clock.tick(60)           