#!/usr/bin/env python

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
windowSurface = pygame.display.set_mode((1200, 650), 0, 32)
pygame.display.set_caption('Lander')
gameRect = windowSurface.get_rect()

# the game class!!
# level
# number of asteroids
# fuel indicator
# number of lives?
# start animation?
class Game:
    def __init__(self):
        self.no_of_asteroids = 10
        self.pad_size = 50
        self.score = 0
    
    def next_level(self):
        pass
        
    

# the asteroid class!
class Asteroid:
    def __init__(self,(x,y),radius=10):
        self.rect = pygame.draw.circle(windowSurface, WHITE, (x,y), radius, 0)
    def draw(self):
        pygame.draw.circle(windowSurface, WHITE, (self.rect.centerx,self.rect.centery), self.rect.width/2, 0)
        
        

# the spaceship class!
class Ship:
    def __init__(self,(x,y),fuel=1000,radius=10):
        self.rect = pygame.draw.circle(windowSurface, GREEN, (x,y), radius, 0)
        (self.x_vel,self.y_vel) = (0,0)
    def get_x(self,msecs):
        x = self.rect.centerx + self.x_vel * msecs / 1000.0
        return x
        # Code here to determine edge of screen behaviour
    def get_y(self,msecs):
        y = self.rect.centery + self.get_y_vel(msecs) * msecs / 1000.0 + 0.5 * 100 * (msecs / 1000.0) ** 2
        return y
    def get_y_vel(self,msecs):

        y_vel = self.y_vel + 100 * ( msecs / 1000.0 )
        return y_vel
    def update(self,msecs):
        self.old_rect = pygame.draw.circle(windowSurface, BLACK, (self.rect.centerx,self.rect.centery), self.rect.width/2, 0)
        self.y_vel = self.get_y_vel(msecs)
        self.rect.centerx = self.get_x(msecs)
        self.rect.centery = self.get_y(msecs)
    def draw(self):
        pygame.draw.circle(windowSurface, GREEN, (self.rect.centerx,self.rect.centery), self.rect.width/2, 0)
        

#class Ground:
        
###################################################################################

a = 100
game = Game()
(x,y) = (random.randrange(0,gameRect.right),random.randrange(0,gameRect.bottom))
ship = Ship((x,y),1000,10)

asteroids = []
for i in range(game.no_of_asteroids):
    (x,y) = (random.randrange(0,gameRect.right),random.randrange(0,gameRect.bottom))
    radius = random.randrange(10,40)
    asteroid = Asteroid((x,y),radius)
    asteroids.append(asteroid)


# run the game loop
while True:

    # ensure 60 fps
    msecs = clock.tick(30)
    
    #Handle events
    for event in pygame.event.get():
        if event.type == var.QUIT:
            pygame.quit()
            sys.exit()
#        elif event.type == MOUSEBUTTONDOWN:
#            pos = pygame.mouse.get_pos()

    # Update the screen
    windowSurface.fill(BLACK)
    for asteroid in asteroids:
        asteroid.draw()
    ship.update(msecs)
    ship.draw()

    # draw the window onto the screen
    pygame.display.update([ a.rect for a in asteroids ] + [ ship.old_rect, ship.rect ])
   