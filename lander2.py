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

class Engine(pygame.sprite.Sprite):
    # Just playing around here.  Find it very hard to animate anythig!
    # Rotation doesn't work as I hoped it would - things go all squiffy
    # I want a way to animate engine flames coming out of the ball, basically.
    # In fact, ball.rect.center just doesn't seem to be the center of the ball!  Confused.
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface((5*Ball.radius, 5*Ball.radius))
        self.image.set_colorkey(BLACK) # make the black background transparent
        self.rect = self.image.get_rect()
        pygame.draw.line(self.image, RED, self.rect.center, self.rect.bottomright)
        self.image = self.image.convert_alpha()
        self.image_copy = self.image.copy()
    def update(self,ball):
        self.rect.center = ball.rect.center
        pos = pygame.mouse.get_pos()
        
        (x,y) = (pos[0] - self.rect.centerx,pos[1] - self.rect.centery)
        if x == 0:
            #if y == 0:
            #    return (0,0)  # Click on dead center of ball, no force / acceleration applied
            if y > 0: angle = math.pi / 2
            if y < 0: angle = (3.0/2) * math.pi
        else:
            if x > 0 and y >= 0 or x > 0 and y < 0: angle = math.atan((1.0*y)/x)
            if x < 0 and y >= 0 or x < 0 and y < 0: angle = math.atan((1.0*y)/x) + math.pi        
        
        
        angle_in_degrees = angle * 180.0 / math.pi
        print angle, angle_in_degrees
        
        self.image = pygame.transform.rotate(self.image_copy, -angle_in_degrees)
        new_rect = self.image.get_rect()
        new_rect.center = self.rect.center        


class Ball(pygame.sprite.Sprite):
    radius = 20
    def __init__(self,(x,y),fuel,shield):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface((2*Ball.radius, 2*Ball.radius))
        self.image.set_colorkey(BLACK) # make the black background transparent
        self.rect = self.image.get_rect()
        pygame.draw.circle(self.image, WHITE, self.rect.center, Ball.radius)
        pygame.draw.circle(self.image, GREEN, (self.rect.centerx,int(self.rect.height*0.25)),int(Ball.radius*0.25))
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)

        self.radius = Ball.radius
        self.rect.center = (x,y)    
        (self.x_vel,self.y_vel) = (0,0) # vel is pixels per second    
        (self.x,self.y) = (x,y)    
        (self.x_accel,self.y_accel) = (0,0)
        self.fuel = fuel
        self.shield = shield
        self.shield_active = False
        self.shield_colour = BLUE
        self.shield_timer = None

    def update_pos(self,msecs):
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
        self.update_shield()
        
    def draw_shield(self,msecs):
        if self.shield_active == True:
            if self.shield_timer == None:
                pygame.draw.circle(screen, self.shield_colour, (self.rect.centerx,self.rect.centery), Ball.radius, 5)
            else:
                # We have just collided with something and want shield to flash for visible length of time
                temp_shield_colour = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
                pygame.draw.circle(screen, temp_shield_colour, (self.rect.centerx,self.rect.centery), Ball.radius,8)
                
                self.shield_timer += msecs
                if self.shield_timer > 150: self.shield_timer = None
        
    def update_shield(self):
        if (pygame.mouse.get_pressed()[2] == True or game.keystate[var.K_s]) and self.shield > 0:
            self.shield -= 1
            self.shield_active = True
        else:
            self.shield_active = False
       
    def update_accel(self):
        if pygame.mouse.get_pressed()[0] == True or game.keystate[var.K_a]:
            (mouse_x,mouse_y) = pygame.mouse.get_pos()
            self.fuel -= 1
            if self.fuel <= 0:
                self.fuel = 0
                # Ran out of fuel ... no more acceleration
                (self.x_accel, self.y_accel) = (0,0)
                return                
        else:
            # There is no acceleration when the mouse button or 's' isn't being pressed
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
            
    def shielded_asteroid_collision(self,object):
        # This is the function called when we hit an object that is fixed
        # - ie. an asteroid, the landing pad or the ground - and need to bounce
        # off it
        self.shield_timer = 0 # Want shield to flash for a visible length of time on impact
        (Bx,By) = (self.rect.centerx,self.rect.centery) # Centre of ball
        (Ax,Ay) = (object.rect.centerx,object.rect.centery) # Centre of asteroid
        # (Ax-Bx,Ay-By) - vector from ball centre to asteroid centre 
        mod = math.sqrt((Ax-Bx)**2 + (Ay-By)**2)
        e2 = ((1.0/mod)*(Ax-Bx),(1.0/mod)*(Ay-By)) # unit vector from ball to asteroid
        # Now need to calculate other unit vector
        # v = |v|cos& e2  +  |v|sin& e1, where v.e2 = |v| cos&
        v = (float(self.x_vel),float(self.y_vel))
        v_dot_e2 = v[0]*e2[0] + v[1]*e2[1]
        mod_v = math.sqrt(v[0]**2 + v[1]**2)
        if mod_v == 0: return # 
        angle = math.acos(v_dot_e2/mod_v)
        e1 = ((v[0] - mod_v*math.cos(angle)*e2[0])/(mod_v*math.sin(angle)),(v[1] - mod_v*math.cos(angle)*e2[1])/(mod_v*math.sin(angle)))
        #print "Asteroid centre is : (%s,%s)" % (object.rect.centerx,object.rect.centery)
        #print "Asteroid centre as calculated by using e2 is : (%s,%s)" % (self.rect.centerx + mod*e2[0],self.rect.centery + mod*e2[1])
        #print "mod e1 is %s" % math.sqrt(e1[0]**2 + e1[1]**2)
        #print "e1 dot e2 is %s" % (e1[0]*e2[0] + e1[1]*e2[1])
        #print "old V vector is : %s" % str(v)
        #print "old V using e1 and e2 is : (%0.1f, %0.1f)" % ((mod_v*math.cos(angle)*e2[0] + mod_v*math.sin(angle)*e1[0]),(mod_v*math.cos(angle)*e2[1] + mod_v*math.sin(angle)*e1[1]))

        # When we hit, the e2 component (which is the resolved bit pointing directly at the asteroid) is reversed
        # It may be that this is a second collision in a row (ie. we've not yet quite escaped the asteroid after the first collision)
        # in which case I don't want to reverse e2.  
        # Since e2 is pointing from the ball to the asteroid, I simply test whether it's coefficient is positive or negative and don't reverse
        # it if it's negative.
        #v_wrt_e1_and_e2 = ((mod_v*math.cos(angle)*e2[0] + mod_v*math.sin(angle)*e1[0]),(mod_v*math.cos(angle)*e2[1] + mod_v*math.sin(angle)*e1[1]))
        new_v = ((mod_v*math.sin(angle)*e1[0] - mod_v*math.cos(angle)*e2[0]),(mod_v*math.sin(angle)*e1[1] - mod_v*math.cos(angle)*e2[1]))
        if mod_v * math.cos(angle) >= 0:
            (self.x_vel,self.y_vel) = (new_v[0],new_v[1])
        #print "new V vector is : %s" % str(new_v)

        
        
        return
        
        
        
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
        self.level += 1
        self.score += 100
        self.no_of_asteroids += 3
        self.level_animation()
        screen.fill(BLACK)
        
        self.ballGroup = pygame.sprite.Group() # Yes, I know there's only one ball
        Ball.groups = self.ballGroup           # Sprite class uses groups a lot
        self.ball = Ball((random.randrange(gameRect.left + 20,gameRect.right - 20),gameRect.top + 20),1000,2000)

        self.engineGroup = pygame.sprite.Group()
        Engine.groups = self.engineGroup
        self.engine = Engine()

        self.asteroidGroup = pygame.sprite.Group()
        Asteroid.groups = self.asteroidGroup # Every created asteroid is a member of this group
        for i in range(self.no_of_asteroids):
            (x,y) = (random.randrange(gameRect.left,gameRect.right),random.randrange(gameRect.top + 100,gameRect.bottom))
            radius = random.randrange(20,100)
            asteroid = Asteroid((x,y),radius)
            
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
class Asteroid(pygame.sprite.Sprite):
    
    def __init__(self,(x,y),radius=10):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface((2*radius, 2*radius))
        self.image.set_colorkey(BLACK) # make the black background transparent
        self.rect = self.image.get_rect()
        pygame.draw.circle(self.image, RED, self.rect.center, radius)
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.radius = radius
        self.rect.center = (x,y)
        

#############################################################################################

class LandingStrip:
    def __init__(self,(x,y),length):
        self.rect = pygame.draw.rect(screen, BLUE, (x,y,length,10))


def draw_text(text):
    # Clear the old line of text
    try:
        text.fill(BLACK)
        screen.blit(text, (0,0))
    except: pass
    # Draw new text.  Important to make sure the text isn't transparent so we can clear it
    fuel = "Fuel (%d)" % game.ball.fuel
    shield = "Shield (%d)" % game.ball.shield
    #position = "Position (%d,%d)" % (game.ball.rect.centerx,game.ball.rect.centery)
    velocity = "Velocity (%0.1f, %0.1f)" % (game.ball.x_vel,game.ball.y_vel)
    speed = "Speed (%0.1f)" % (math.sqrt(game.ball.x_vel ** 2 + game.ball.y_vel ** 2))
    #acceleration = "Acceleration (%0.1f, %0.1f)" % (game.ball.x_accel,game.ball.y_accel)
    fps = "FPS: %0.1f" % clock.get_fps()
    text_string = fuel.ljust(20) + shield.ljust(20) + fps.ljust(20) + velocity.ljust(30) + speed.ljust(20)
    text = font.render(text_string, 0, WHITE, BLACK)
    screen.blit(text, (0,0))
    return text

#############################################################################################

# set up the window
screen = pygame.display.set_mode((1200, 650), 0, 32)

background = pygame.Surface(screen.get_size())  # Create empty pygame surface
background.fill(BLACK)     # Fill the background white color (red,green,blue)
background = background.convert()  # Convert Surface to make blitting faster
screen.blit(background, (0, 0))

pygame.display.set_caption('Lander')
gameRect = screen.get_rect()
accel_magnitude = 200
font = pygame.font.Font(None, 36)
text = None
clock = pygame.time.Clock()

# Create the game
game = Game()

###############################################################################################

# run the game loop
while True:

    msecs = clock.tick(100) 
    # Get events from the event queue
    for event in pygame.event.get():
        if event.type == var.QUIT:
            pygame.quit()
            sys.exit()
    
    game.keystate = pygame.key.get_pressed()


    # COLLISIONS        
    # Check for collisions with asteroids
    # There are ways to improve the collision detection - this one isn't great
    index = game.ball.rect.collidelist(game.asteroids)
    # First we do a quick cheap check to see if anything might be colliding ...
    asteroid_collisions = pygame.sprite.spritecollide(game.ball,game.asteroidGroup,False)
    for asteroid in asteroid_collisions:
        # Now we accurately check out those possible collisions
        if pygame.sprite.collide_mask(game.ball,asteroid):
            if game.ball.shield_active == False:
                game.it_is_game_over()
            else:
                # We are colliding with an asteroid, but our amazing shield saves us!
                game.ball.shielded_asteroid_collision(asteroid)
    

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
    game.asteroidGroup.clear(screen, background)
    game.ballGroup.clear(screen, background)
    #game.engineGroup.clear(screen, background)
    # Draw function for asteroids will be needed when explosions go over them
    game.asteroidGroup.draw(screen)
    game.engineGroup.draw(screen)
    game.ballGroup.draw(screen)
    
    game.ball.draw_shield(msecs)
    game.engineGroup.update(game.ball)
    game.ball.update(msecs)
    text = draw_text(text)
    
    # draw the window onto the screen
    pygame.display.update()  