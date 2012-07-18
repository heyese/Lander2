#!/usr/bin/env python

import pygame, sys, random, time, math
import pygame.locals as var

# ideas

# The collision detection isn't brilliant.  I really want pixel perfect collision
# detection between the ship and the asteroid, so I probably need to work out how to
# use the 'sprite' class and masks rather than the basic colliderect function.

# Right mouse button is shield, with which ball will bounce off asteroids
# Turrets firing missiles.  Ball can destroy them using shield.
# Missiles themselves can have different amounts of fuel,
# different acceleration rates, could blow up on a timer.
# Really excited about their explosions - series of bigger circles,
# and if ball is inside explosion circle an acceleration is applied.
# The amount of acceleration can also be a property of the missile.

# Could possibly fire my own missile or drop bomb when both mouse buttons are pressed.
# Or have a more powerful burst of acceleration

# Graphics
# Engine flame
# Explosions
# New level and game over graphics


# set up pygame
pygame.init()

# colours
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)


class Ball():
    def __init__(self,(x,y),fuel,shield):
        (self.x_vel,self.y_vel) = (0,0) # vel is pixels per second
        (self.x,self.y) = (x,y)
        (self.x_accel,self.y_accel) = (0,0)
        self.rect = pygame.draw.circle(windowSurface, WHITE, (gameRect.centerx,gameRect.centery), 20, 0)
        self.fuel = fuel
        self.shield = shield

    def update_pos(self,msecs):
        (self.old_x,self.old_y) = (self.x,self.y)
        x = self.x + self.x_vel * msecs / 1000.0 + 0.5 * self.x_accel * (msecs / 1000.0) ** 2
        y = self.y + self.y_vel * msecs / 1000.0 + 0.5 * self.y_accel * (msecs / 1000.0) ** 2
        (self.x,self.y) = (x,y)
        (self.rect.centerx,self.rect.centery) = (int(x),int(y))

    def update_vel(self,msecs):
        x_vel = self.x_vel + self.x_accel * ( msecs / 1000.0)
        y_vel = self.y_vel + self.y_accel * ( msecs / 1000.0)
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
        self.update_accel()
        
    def draw(self):
        # Black out the previous position, then draw our new one.
        self.old_rect = pygame.draw.circle(windowSurface, BLACK, (int(self.old_x),int(self.old_y)), 22, 0)
        pygame.draw.circle(windowSurface, WHITE, (self.rect.centerx,self.rect.centery), 20, 0)
        
    def update_accel(self):
        if pygame.mouse.get_pressed()[0] == True:
            (mouse_x,mouse_y) = pygame.mouse.get_pos()
            self.fuel = self.fuel - 1
            if self.fuel <= 0:
                self.fuel = 0
                # Ran out of fuel ... no more acceleration
                (self.x_accel, self.y_accel) = (0,0)
                return                
        else:
            # There is no acceleration when the mouse button isn't being pressed
            (self.x_accel, self.y_accel) = (0,0)
            return
        (x,y) = (mouse_x - self.rect.centerx,mouse_y - self.rect.centery)
        if x == 0:
            if y == 0:
                return (0,0)  # Click on dead center of ball, no force / acceleration applied
            if y > 0: angle = math.pi / 2
            if y < 0: angle = (3.0/2) * math.pi
        else:
            if x > 0 and y >= 0 or x > 0 and y < 0: angle = math.atan((1.0*y)/x)
            if x < 0 and y >= 0 or x < 0 and y < 0: angle = math.atan((1.0*y)/x) + math.pi
        (self.x_accel, self.y_accel) = (accel_magnitude * math.cos(angle),accel_magnitude * math.sin(angle))
    
    def landed(self,landingStrip):
        # Know we've collided.
        # If x_vel and y_vel have low enough magnitude and we're
        # completely over the landing strip, weve landed.
        if self.rect.centerx < landingStrip.rect.left or self.rect.centerx > landingStrip.rect.right or self.rect.centery > landingStrip.rect.bottom:
            return False
        if abs(self.x_vel) > 20 or abs(self.y_vel) > 20:
            return False
        return True
            
           
        
        
class Game:
# the game class!!
# level
# number of asteroids
# fuel indicator
# number of lives?
# start animation?
    def __init__(self):
        self.no_of_asteroids = 10
        self.pad_size = 50
        self.score = 0
        self.level = 0
        self.game_over = False
        self.asteroids = []
        self.next_level()

    
    def next_level(self):
        self.ball = Ball((random.randrange(gameRect.left + 20,gameRect.right - 20),gameRect.top + 20),300,200)
        self.level += 1
        self.score += 100
        self.no_of_asteroids += 3
        self.level_animation()
        windowSurface.fill(BLACK)
        # Draw the asteroids!
        self.asteroids = []
        for i in range(self.no_of_asteroids):
            (x,y) = (random.randrange(gameRect.left,gameRect.right),random.randrange(gameRect.top + 100,gameRect.bottom))
            radius = random.randrange(10,40)
            asteroid = Asteroid((x,y),radius)
            self.asteroids.append(asteroid)
            
        # draw the landing strip
        self.landingStrip = LandingStrip((random.randrange(gameRect.left,gameRect.right),random.randrange(gameRect.bottom - 100,gameRect.bottom)),100)
        
    def level_animation(self):
        pass    
    
    def it_is_game_over(self):
        self.game_over = True
        # play blow up animation!
        print "Game Over"
        sys.exit()

# the asteroid class!
class Asteroid:
    def __init__(self,(x,y),radius=10):
        self.rect = pygame.draw.circle(windowSurface, RED, (x,y), radius, 0)

#############################################################################################

class LandingStrip:
    def __init__(self,(x,y),length):
        self.rect = pygame.draw.rect(windowSurface, BLUE, (x,y,length,10))


def draw_text(text):
    # Clear the old line of text
    try:
        text.fill(BLACK)
        windowSurface.blit(text, (0,0))
    except: pass
    # Draw new text.  Important to make sure the text isn't transparent so we can clear it
    fuel = "Fuel (%d)" % game.ball.fuel
    #position = "Position (%d,%d)" % (game.ball.rect.centerx,game.ball.rect.centery)
    velocity = "Velocity (%0.1f, %0.1f)" % (game.ball.x_vel,game.ball.y_vel)
    #acceleration = "Acceleration (%0.1f, %0.1f)" % (game.ball.x_accel,game.ball.y_accel)
    fps = "FPS: %s" % clock.get_fps()
    text_string = fuel.ljust(30) + fps.ljust(30) + velocity.ljust(30)
    text = font.render(text_string, 0, WHITE, BLACK)
    windowSurface.blit(text, (0,0))
    return text

#############################################################################################

# set up the window
windowSurface = pygame.display.set_mode((1200, 650), 0, 32)
pygame.display.set_caption('Lander')
gameRect = windowSurface.get_rect()
accel_magnitude = 200
font = pygame.font.Font(None, 36)
text = None
clock = pygame.time.Clock()

# Create the game
game = Game()



# run the game loop
while True:

    msecs = clock.tick(100) 
    # Get events from the event queue
    for event in pygame.event.get():
        if event.type == var.QUIT:
            pygame.quit()
            sys.exit()

    # Check for collisions with asteroids
    # There are ways to improve the collision detection - this one isn't great
    index = game.ball.rect.collidelist(game.asteroids)
    if index != -1:
        game.it_is_game_over()
    

    # Check landing pad collision
    if game.ball.rect.colliderect(game.landingStrip):
        # We've either landed or we've crashed!
        if game.ball.landed(game.landingStrip) == True:
            print "You've landed!"
            game.next_level()
        else:
            game.it_is_game_over()

        
    
    
    # Update the screen
    # acceleration calculation uses that we've used pygame.event.get()
    if game.game_over == False:
        game.ball.update(msecs)
        game.ball.draw()
        text = draw_text(text)
    
    
    



    

    
    
    
    # draw the window onto the screen
    pygame.display.update()  