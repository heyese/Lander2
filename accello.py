#!/usr/bin/env python

import pygame, sys, random, time, math
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


class Ball():
    def __init__(self):
        (self.x_vel,self.y_vel) = (0,0) # vel is pixels per second
        (self.x,self.y) = (gameRect.centerx,gameRect.centery)
        self.rect = pygame.draw.circle(windowSurface, WHITE, (gameRect.centerx,gameRect.centery), 20, 0)

    def update_pos(self,msecs):
        (self.old_x,self.old_y) = (self.x,self.y)
        x = self.x + self.x_vel * msecs / 1000.0 + 0.5 * x_accel * (msecs / 1000.0) ** 2
        y = self.y + self.y_vel * msecs / 1000.0 + 0.5 * y_accel * (msecs / 1000.0) ** 2
        (self.x,self.y) = (x,y)
        (self.rect.centerx,self.rect.centery) = (int(x),int(y))

    def update_vel(self,msecs):
        x_vel = self.x_vel + x_accel * ( msecs / 1000.0)
        y_vel = self.y_vel + y_accel * ( msecs / 1000.0)
        # Edge of screen collision code
        if self.rect.top < gameRect.top or self.rect.bottom > gameRect.bottom:
            y_vel = -y_vel
            if self.rect.top < gameRect.top : self.rect.top = gameRect.top
            if self.rect.bottom > gameRect.bottom : self.rect.bottom = gameRect.bottom

        if self.rect.left < gameRect.left or self.rect.right > gameRect.right:
            x_vel = -x_vel
            if self.rect.left < gameRect.left: self.rect.left = gameRect.left
            if self.rect.right > gameRect.right: self.rect.right = gameRect.right
            
        (self.x_vel,self.y_vel) = (x_vel,y_vel)
    def update(self,msecs):
        self.update_vel(msecs)
        self.update_pos(msecs)
    def draw(self):
        self.old_rect = pygame.draw.circle(windowSurface, BLACK, (int(self.old_x),int(self.old_y)), 22, 0)
        pygame.draw.circle(windowSurface, WHITE, (self.rect.centerx,self.rect.centery), 20, 0)
        

#############################################################################################

def calculate_accel((mouse_x,mouse_y),(ball_x,ball_y)):
    (x,y) = (mouse_x - ball_x,mouse_y - ball_y)
    if x == 0:
        if y == 0:
            return (0,0)  # Click on dead center of ball, no force / acceleration applied
        if y > 0: angle = math.pi / 2
        if y < 0: angle = (3.0/2) * math.pi
    else:
        if x > 0 and y >= 0 or x > 0 and y < 0: angle = math.atan((1.0*y)/x)
        if x < 0 and y >= 0 or x < 0 and y < 0: angle = math.atan((1.0*y)/x) + math.pi
    (x_accel, y_accel) = (accel_magnitude * math.cos(angle),accel_magnitude * math.sin(angle))
    return (x_accel, y_accel)

def draw_text(text):
    # Clear the old line of text
    try:
        text.fill(BLACK)
        windowSurface.blit(text, (0,0))
    except: pass
    # Draw new text.  Important to make sure the text isn't transparent so we can clear it
    position = "Position (%d,%d)" % (ball.rect.centerx,ball.rect.centery)
    velocity = "Velocity (%0.1f, %0.1f)" % (ball.x_vel,ball.y_vel)
    acceleration = "Acceleration (%0.1f, %0.1f)" % (x_accel,y_accel)
    text_string = velocity.ljust(30) + acceleration.ljust(30) + position.ljust(30)
    text = font.render(text_string, 0, WHITE, BLACK)
    windowSurface.blit(text, (0,0))
    return text

#############################################################################################

# set up the window
windowSurface = pygame.display.set_mode((1200, 650), 0, 32)
pygame.display.set_caption('Accello')
gameRect = windowSurface.get_rect()
accel_magnitude = 200
(x_accel,y_accel) = (0,0)
ball = Ball()
font = pygame.font.Font(None, 36)
text = None



# run the game loop
while True:

    msecs = clock.tick(100) 

    # Update the screen
    ball.update(msecs)
    ball.draw()
    text = draw_text(text)

    
    for event in pygame.event.get():
        if event.type == var.QUIT:
            pygame.quit()
            sys.exit()
    if pygame.mouse.get_pressed()[0] == True:
        pos = pygame.mouse.get_pos()
        (x_accel,y_accel) = calculate_accel(pos,ball.rect.center)
    else: (x_accel,y_accel) = (0,0)
    
    
    
    # draw the window onto the screen
    pygame.display.update()  