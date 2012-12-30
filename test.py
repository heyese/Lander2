#!/usr/bin/env python

import pygame, sys, random, time, math
import pygame.locals as var

# set up pygame
pygame.init()

# colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)

# set up the window
screen = pygame.display.set_mode((1200, 650), 0, 32)

background = pygame.Surface(screen.get_size())  # Create empty pygame surface
background.fill(BLACK)     # Fill the background white color (red,green,blue)
background = background.convert()  # Convert Surface to make blitting faster
screen.blit(background, (0, 0))

pygame.display.set_caption('Lander')
gameRect = screen.get_rect()

image = pygame.Surface((40, 40))
image.set_colorkey(BLACK) # make the black background transparent
rect = image.get_rect()
pygame.draw.circle(image, WHITE, rect.center, 20)
#pygame.draw.circle(image, GREEN, (rect.centerx,30),7)
image = image.convert_alpha()


#screen.blit(rot_image,gameRect.center)



while True:

    # Get events from the event queue
    for event in pygame.event.get():
        if event.type == var.QUIT:
            pygame.quit()
            sys.exit()
    pos = pygame.mouse.get_pos()
    angle_in_radians = math.atan(1.0*(pos[1] - gameRect.centery)/(pos[0] - gameRect.centerx))
    angle_in_degrees = angle_in_radians * 180.0 / math.pi + 90
    
    rot_image = pygame.transform.rotate(image, angle_in_degrees)
    new_rect = rot_image.get_rect()
    new_rect.center = rect.center
    print new_rect.center
    # rotation isn't about centre - it's about (0,0)!
    screen.blit(rot_image,gameRect.center)
    
    # draw the window onto the screen
    pygame.display.update()        
        
    