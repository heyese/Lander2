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
YELLOW = (255, 255, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
GREY = (119,119,119)
PINK = (255,200,200)

class Engine():
    # Just playing around here.  Find it very hard to animate anythig!
    # Rotation doesn't work as I hoped it would - things go all squiffy
    # I want a way to animate engine flames coming out of the ball, basically.
    
    # Engine object should be instantiated by the item it is an engine for
    # That item should have an .angle attribute, being the angle of engine force
    
    engines = []
    def __init__(self,item):
        Engine.engines.append(self) # add this instance to the class list
        self.item = item # this could be the ship, a missile or whatever
        # Want size of engine animation to depend on the accel_magnitude of the item
        self.image = pygame.Surface((2*item.accel_magnitude, 2*item.accel_magnitude))
        self.image_copy = self.image.copy()
        self.image_copy.fill(BLACK)
        self.draw()

    def engine_activated(self):
        # Plan to give the ball and all missiles engine animations
        # Doing it below be letting the engine work out what it's an engine for.
        if self.item.__class__.__name__ == 'Ball':
            try:
                if self.item.fuel > 0 and (pygame.mouse.get_pressed()[0] == True or game.keystate[var.K_a] == True):
                    return True
                else:
                    return False
            except:
                return False
        elif self.item.__class__.__name__ == 'Missile':
            try:
                if self.item.fuel > 0:
                    return True
                else:
                    return False
            except:
                return False
        else:
            return True
            
    def draw(self):
        
        self.image = self.image_copy.copy()
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK) # make the black background transparent
        
        # Missiles will always be accelerating (unless they're out of fuel? ...)
        # With the ball, we only want animation if we're accelerating
        if self.engine_activated() == False:
           return
        # Calculating points ...
        base_of_triangle = (self.rect.centerx - 0.5 * self.item.radius * math.cos(self.item.angle),self.rect.centery - 0.5 * self.item.radius * math.sin(self.item.angle))
        unit_perp_vector = (math.sin(self.item.angle), -math.cos(self.item.angle))
        
        # Cente of circle to base of triangle
        vector1 = (-0.5 * self.item.radius * math.cos(self.item.angle),0.5 * self.item.radius * math.sin(self.item.angle))
        
        #Vectors to base corners of triangle
        
        width_factor = random.random()/2.0 + 0.5
        #height_factor = 2*random.random() + 1.5
        height_factor = random.random() * 0.7 + 0.3
        
        colour_factor = random.randrange(0,256)
        p1 = (int(base_of_triangle[0] + width_factor*self.item.radius*unit_perp_vector[0]),int(base_of_triangle[1] + width_factor*self.item.radius*unit_perp_vector[1]))
        p2 = (int(base_of_triangle[0] - width_factor*self.item.radius*unit_perp_vector[0]),int(base_of_triangle[1] - width_factor*self.item.radius*unit_perp_vector[1]))
        p3 = (int(self.rect.centerx - 0.5 * height_factor * self.item.accel_magnitude * math.cos(self.item.angle)),int(self.rect.centery - 0.5 * height_factor * self.item.accel_magnitude * math.sin(self.item.angle)))
        colour = (255, colour_factor, 0)
        pygame.draw.polygon(self.image, colour, [p1, p2, p3] )

        
        self.image.set_alpha(200) # How transparent do we want it?  0 = transparent, 255 = solid.
        self.image = self.image.convert_alpha()
        self.rect.center = self.item.rect.center
        screen.blit(self.image,self.rect)
    
    def clear(self):
        # Here I want to trim the background down to size and blit that
        # over the image.  Not sure how to do it just now so I'll use a square of black.
        screen.blit(self.image_copy,self.rect)
        # If the item is no longer alive, it should no longer have an engine
        if self.item not in game.allGroup:
            Engine.engines.remove(self)
             
class Ball(pygame.sprite.Sprite):
    def __init__(self,center=(0,0),fuel=0,shield=0,accel_magnitude=0,radius=0,colour=WHITE):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface((2*radius, 2*radius))
        self.image.set_colorkey(BLACK) # make the black background transparent
        self.rect = self.image.get_rect()
        pygame.draw.circle(self.image, colour, self.rect.center, radius)
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.angle = math.pi
        self.accel_magnitude = accel_magnitude
        (self.x_accel_external, self.y_accel_external) = (0,0)

        self.radius = radius
        self.rect.center = center    
        (self.x_vel,self.y_vel) = (0,0) # vel is pixels per second    
        (self.x,self.y) = center    
        (self.x_accel,self.y_accel) = (0,0)
        self.fuel = fuel
        self.shield = shield
        self.shield_active = False
        self.shield_colour = BLUE
        self.shield_impact_timer = None  # If we hit something, shield animation changes colour for an amount of time
        self.shield_timer_min = 300  # For missiles, shields remain on more than a minimum amount of time
        self.shield_timer = 0
        self.engine = Engine(self)
        

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
    def update_mouse_angle_to_ball(self):
        # Nice to know what angle the mouse is at to the ball
        pos = pygame.mouse.get_pos()
        (x,y) = (pos[0] - self.rect.centerx,pos[1] - self.rect.centery)
        if x == 0:
            #if y == 0:
            #    return (0,0)  # Click on dead center of ball, no force / acceleration applied
            if y > 0: self.angle = math.pi / 2
            if y < 0: self.angle = (3.0/2) * math.pi
        else:
            if x > 0 and y >= 0 or x > 0 and y < 0: self.angle = math.atan((1.0*y)/x)
            if x < 0 and y >= 0 or x < 0 and y < 0: self.angle = math.atan((1.0*y)/x) + math.pi 
    
    def update(self,msecs):
        self.update_mouse_angle_to_ball()
        self.update_shield()
        self.draw_shield(msecs)
        self.update_vel(msecs)
        self.update_pos(msecs)
        self.update_accel()

        
        
    def draw_shield(self,msecs):
        if self.shield_active == True:
            if self.shield_impact_timer == None:
                pygame.draw.circle(screen, self.shield_colour, (self.rect.centerx,self.rect.centery), self.radius, 5)
            else:
                # We have just collided with something and want shield to flash for visible length of time
                temp_shield_colour = (random.randint(0,255),random.randint(0,255),random.randint(0,255))
                pygame.draw.circle(screen, temp_shield_colour, (self.rect.centerx,self.rect.centery), self.radius,8)
                
                self.shield_impact_timer += msecs
                if self.shield_impact_timer > 150: self.shield_impact_timer = None
    

    def update_shield(self):
        if (pygame.mouse.get_pressed()[2] == True or game.keystate[var.K_s]) and self.shield > 0:
            self.shield -= 1
            self.shield_active = True
        else:
            self.shield_active = False
       
    def update_accel(self):
        if pygame.mouse.get_pressed()[0] == True or game.keystate[var.K_a]:
            self.fuel -= 1
            if self.fuel <= 0:
                self.fuel = 0
                # Ran out of fuel ... no more acceleration
                (self.x_accel, self.y_accel) = (0,0)
            else:
                (self.x_accel, self.y_accel) = (self.accel_magnitude * math.cos(self.angle),self.accel_magnitude * math.sin(self.angle))

        else:
            # There is no acceleration when the mouse button or 's' isn't being pressed
            (self.x_accel, self.y_accel) = (0,0)
        self.add_gravitational_accel()
        self.add_external_acceleration()
        
    def add_gravitational_accel(self):
        self.y_accel += game.gravity
      
    def external_acceleration(self,magnitude,angle):
        self.x_accel_external += magnitude * math.cos(angle)
        self.y_accel_external += magnitude * math.sin(angle)
        
    def add_external_acceleration(self):
        self.x_accel += self.x_accel_external
        self.y_accel += self.y_accel_external
        # Now reset the external acceleration
        (self.x_accel_external,self.y_accel_external) = (0,0)
        
        
    
    def landed(self,landingStrip):
        # Know we've collided.
        # If x_vel and y_vel have low enough magnitude and we're
        # completely over the landing strip, weve landed.
        if self.rect.centerx < landingStrip.rect.left or self.rect.centerx > landingStrip.rect.right or self.rect.centery > landingStrip.rect.bottom:
            return False
        if abs(math.sqrt(self.x_vel ** 2 + self.y_vel ** 2)) > landingStrip.maxLandingSpeed:
            return False
        return True
            
    def fixed_collision(self,(mask_x,mask_y)):
        # This is the function called when we hit an object that is fixed
        # - ie. an asteroid, the landing pad or the ground - and need to bounce
        # off it.  (x,y) are the coordinates of the ball mask at which point the collision is.
        self.shield_impact_timer = 0 # Want shield to flash for a visible length of time on impact
        (Bx,By) = (self.rect.centerx,self.rect.centery) # Centre of ball
        (Ax,Ay) = (self.rect.topleft[0] + mask_x,self.rect.topleft[1] + mask_y)
        # (Ax-Bx,Ay-By) - vector from ball centre to asteroid centre 
        mod = math.sqrt((Ax-Bx)**2 + (Ay-By)**2)
        if mod == 0:
            print "mod was zero - check this out"
            return
        e2 = ((1.0/mod)*(Ax-Bx),(1.0/mod)*(Ay-By)) # unit vector from ball to asteroid
        # Now need to calculate other unit vector
        # v = |v|cos& e2  +  |v|sin& e1, where v.e2 = |v| cos&
        v = (float(self.x_vel),float(self.y_vel))
        v_dot_e2 = v[0]*e2[0] + v[1]*e2[1]
        mod_v = math.sqrt(v[0]**2 + v[1]**2)
        if mod_v == 0: return # 
        angle = math.acos(v_dot_e2/mod_v)
        e1 = ((v[0] - mod_v*math.cos(angle)*e2[0])/(mod_v*math.sin(angle)),(v[1] - mod_v*math.cos(angle)*e2[1])/(mod_v*math.sin(angle)))

        # When we hit, the e2 component (which is the resolved bit pointing directly at the asteroid) is reversed
        # It may be that this is a second collision in a row (ie. we've not yet quite escaped the asteroid after the first collision)
        # in which case I don't want to reverse e2.  
        # Since e2 is pointing from the ball to the asteroid, I simply test whether it's coefficient is positive or negative and don't reverse
        # it if it's negative.

        new_v = ((mod_v*math.sin(angle)*e1[0] - mod_v*math.cos(angle)*e2[0]),(mod_v*math.sin(angle)*e1[1] - mod_v*math.cos(angle)*e2[1]))
        if mod_v * math.cos(angle) >= 0:
            (self.x_vel,self.y_vel) = (new_v[0],new_v[1])
        #print "new V vector is : %s" % str(new_v)
        
        return

class Missile(Ball):
    
    def update(self,msecs):
        self.update_ball_angle_to_missile()
        self.update_shield(msecs)
        self.draw_shield(msecs)
        self.update_vel(msecs)
        self.update_pos(msecs)
        self.update_accel()        


    def update_ball_angle_to_missile(self):
        #(x,y) = (game.ball.x - self.rect.centerx,game.ball.y - self.rect.centery)
        (x,y) = (game.ball.x + game.ball.x_vel - self.rect.centerx,game.ball.y + game.ball.y_vel - self.rect.centery)
        if x == 0:
            #if y == 0:
            #    return (0,0)  # Click on dead center of ball, no force / acceleration applied
            if y > 0: self.angle = math.pi / 2
            if y < 0: self.angle = (3.0/2) * math.pi
        else:
            if x > 0 and y >= 0 or x > 0 and y < 0: self.angle = math.atan((1.0*y)/x)
            if x < 0 and y >= 0 or x < 0 and y < 0: self.angle = math.atan((1.0*y)/x) + math.pi
            
    def update_accel(self):
        self.fuel -= 1
        if self.fuel <= 0:
            self.fuel = 0
            # Ran out of fuel ... no more acceleration
            (self.x_accel, self.y_accel) = (0,0)             
        (self.x_accel, self.y_accel) = (self.accel_magnitude * math.cos(self.angle),self.accel_magnitude * math.sin(self.angle))
        self.add_gravitational_accel()
        self.add_external_acceleration()
        
    
    def update_shield(self,msecs):
        # If a missile activates its shield, it should stay on for a minimum amount of time
        # if missile is close - ie. a rect collide - with other solid objects and self.shield > 0 then switch on the shield
        close_solid_encounters = pygame.sprite.spritecollide(self,game.staticSolidsGroup,False)
        close_explosion_encounters = pygame.sprite.spritecollide(self,game.explosionGroup,False)
        #close_missile_encounters = pygame.sprite.spritecollide(self,game.missileGroup,False) # missile will always collide with itself, of course
        
        
        if (len(close_solid_encounters) > 0 or len(close_explosion_encounters) > 0) and self.shield > 0: 
            self.shield_timer = self.shield_timer_min
            self.shield -= 1
            self.shield_active = True
        elif self.shield > 0 and self.shield_timer > 0:
            self.shield_timer -= msecs
            self.shield -= 1
            self.shield_active = True
        else:
            self.shield_timer = 0
            self.shield_active = False
        
class Ground(pygame.sprite.Sprite):
    def __init__(self, landingStrip):
        pygame.sprite.Sprite.__init__(self, self.groups)
        # 1 fifth of the screen up, all the way across
        (width, height) = screen.get_size()
        self.image = pygame.Surface((width, int(0.2 * height)))
        self.image.set_colorkey(BLACK) # make the black background transparent
        self.rect = self.image.get_rect()
        self.landingStrip = landingStrip
        
        # landStrip coordinates as imposed on ground rectangle
        (ls_x1,ls_y1) = (self.landingStrip.rect.bottomleft[0],int(self.landingStrip.rect.bottomleft[1] - 0.8 * height))
        (ls_x2,ls_y2) = (self.landingStrip.rect.bottomright[0], int(self.landingStrip.rect.bottomright[1] - 0.8 * height))

        # This should be a filled in rectangle - the top is a series of points
        points = []
        x = self.rect.left
        while x < self.rect.right:
            y = random.randrange(self.rect.top,self.rect.bottom)
            x = x + random.randrange(0,50)
            if x >= self.rect.right:
                x = self.rect.right
            if x >= ls_x1 and (ls_x1,ls_y1) not in points:
                points.extend([(ls_x1,ls_y1),(ls_x2,ls_y2)])
                x = ls_x2
                continue
            points.append((x,y))
            if x == self.rect.right: break
        points.extend([self.rect.bottomright, self.rect.bottomleft])
            
        pygame.draw.polygon(self.image, GREEN, points)
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.bottomleft = gameRect.bottomleft       
        
class Game:
# the game class!!
# level
# number of asteroids
# fuel indicator
# number of lives?
# start animation?
    def __init__(self):
        self.gravity = 20
        self.no_of_asteroids = 1
        self.no_of_launchers = 0
        self.pad_size = 50
        self.score = 0
        self.level = 0
        self.game_over = False
        self.asteroids = []
        self.next_level()
    
    def next_level(self):
        self.level += 1
        self.score += 100
        self.no_of_asteroids += 2
        self.no_of_launchers += 2
        self.level_animation()
        screen.fill(BLACK)
        
        # Clear last levels engines and explosions
        Engine.engines = []
        Explosion.explosions = []
        Asteroid.asteroids = []
        # Set up the sprite groups
        self.allGroup = pygame.sprite.Group()
        self.explosionGroup = pygame.sprite.Group()
        Explosion.groups = self.explosionGroup, self.allGroup
        self.staticSolidsGroup = pygame.sprite.Group()
        self.ballGroup = pygame.sprite.Group()
        Ball.groups = self.ballGroup, self.allGroup         # Sprite class uses groups a lot
        self.missileGroup = pygame.sprite.Group()
        Missile.groups = self.missileGroup, self.allGroup    
        self.asteroidGroup = pygame.sprite.Group()
        Asteroid.groups = self.asteroidGroup, self.staticSolidsGroup, self.allGroup
        self.groundGroup = pygame.sprite.Group()
        Ground.groups = self.groundGroup, self.staticSolidsGroup, self.allGroup
        self.launcherGroup = pygame.sprite.Group()
        Launcher.groups = self.launcherGroup, self.allGroup
        self.landingStripGroup = pygame.sprite.Group()
        LandingStrip.groups = self.landingStripGroup, self.staticSolidsGroup, self.allGroup
        self.textGroup = pygame.sprite.Group()
        Text.groups = self.textGroup, self.allGroup
        self.explosionGroup = pygame.sprite.Group()
        Explosion.groups = self.explosionGroup, self.allGroup
        self.earthquakeGroup = pygame.sprite.Group()
        Earthquake.groups = self.earthquakeGroup, self.allGroup  
        
        # Below, I need to create the launchers.
        # Each sits on a particular asteroid.  If it intersects with any other asteroid, landing pad or ground, it explodes
        # On it's update method, after a timer, it launches a missile.
        # When it does that, for a while it has a kind of shield which means the missile doesn't collide with it
        # That shield switches off after a couple of seconds
        # They can be destroyed by missiles colliding with them and by the ball colliding with them (shield up, though!).
        
        # Create the sprites
        self.text = Text()
        ball_center = (random.randrange(gameRect.left + 20,gameRect.right - 20),gameRect.top + 20)
        self.ball = Ball(center=ball_center,fuel=3000,shield=2000,accel_magnitude=200,radius=20,colour=WHITE)
        #for i in range(3):
        #    missile_center = (random.randrange(gameRect.left + 20,gameRect.left + 50),random.randrange(gameRect.top + 20,gameRect.bottom - 150))
        #    self.missile = Missile(center=missile_center,fuel=2000,shield=400,accel_magnitude=80,radius=10,colour=RED)
        coords = (random.randrange(gameRect.left,gameRect.right - 100),random.randrange(gameRect.bottom - 100,gameRect.bottom))
        self.landingStrip = LandingStrip(topleft=coords,length=100)

        self.ground = Ground(self.landingStrip)
        
        for i in range(self.no_of_asteroids):
            (min_rad,max_rad) = (30,105)
            rad = int(math.sqrt(random.randrange(min_rad**2,max_rad**2)))
            (x,y) = (random.randrange(gameRect.left,gameRect.right),random.randrange(gameRect.top + rad + 2*self.ball.radius,gameRect.bottom - rad - 0.2 * screen.get_size()[1]))
            initial_life = int(200 + 200 * (rad - min_rad)/(max_rad - min_rad))
            asteroid = Asteroid(center=(x,y),radius=rad,life=initial_life)
        # Create the missile launchers
        for i in range(self.no_of_launchers):
            # I want to be sure the launchers are in the open, so I keep trying until I get it right
            tries = 0
            while True:
                # first, pick a random asteroid
                asteroid = Asteroid.asteroids[random.randrange(0,len(Asteroid.asteroids))]
                # second, pick a random angle in degrees
                degree = random.randrange(0,360)
                # Thirdly, how powerful will the missiles be?
                accel_magnitude = random.randrange(40,110)
                # How frequently will it fire missiles?
                time_spacing = random.randrange(2000,10000)
                launcher = Launcher(asteroid,degree,50,accel_magnitude,time_spacing)
                # if launcher coincides with any other asteroids, try again
                if len(pygame.sprite.spritecollide(launcher,self.asteroidGroup,False)) > 1 or len(pygame.sprite.spritecollide(launcher,self.launcherGroup,False)) > 1:  # launcher etc.
                    launcher.kill()
                    tries += 1
                    if tries >= 10: break
                else:
                    break
                    
    def level_animation(self):
        pass
    
    def it_is_game_over(self):
        self.game_over = True
        print "Game over"
        
        # Create an explosion for the ball
        Explosion(game.ball.rect.center,game.ball.radius,3*game.ball.radius)
        # Set the alive flag to false (its engine is removed)
        game.ball.alive = False
        # Remove the sprite from any groups it's a member of
        game.ball.kill()
        # Click to start a new game ...
        global PLAYING
        PLAYING = False

class Asteroid(pygame.sprite.Sprite):
    
    asteroids = []
    def __init__(self,center=(0,0),radius=10,life=200):
        pygame.sprite.Sprite.__init__(self, self.groups)
        Asteroid.asteroids.append(self) # add this instance to the class list
        self.image = pygame.Surface((2*radius, 2*radius))
        self.image.set_colorkey(BLACK) # make the black background transparent
        self.rect = self.image.get_rect()
        pygame.draw.circle(self.image, (150,150,150), self.rect.center, radius)
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.radius = radius
        self.centre = self.rect.center
        self.rect.center = center
        self.original_life = life
        self.current_life = self.original_life
        self.earthquake = Earthquake(self)
                
    def lose_life(self,x):
        self.current_life = self.current_life - x
        # Also want to randomly create new earthquakes / make existing earthquakes branch out
        # This function will be called roughly self.original_life times (as each hurt is -1).
        # Quite want big asteroids, which have more life, to have more earthquakes
        if random.randrange(35) == 0: 
            self.earthquake.new_quake()
        
class Quake():
    # Yes, I've managed to utterly confuse myself.
    # Basically, the Earthquake class gives you the sprite.
    # The Quake class are the lists of points you want to draw on the sprite.
    def __init__(self,starting_point,current_point,orientation,asteroid_life):
        self.initial_asteroid_life = asteroid_life
        self.starting_point = starting_point
        self.current_point = current_point
        self.target_point = self.current_point
        self.orientation = orientation
        self.points = []
        
class Earthquake(pygame.sprite.Sprite):
    def __init__(self,asteroid):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.asteroid = asteroid
        self.image = pygame.Surface((2*asteroid.radius, 2*asteroid.radius))
        self.image.set_colorkey(BLACK) # make the black background transparent
        self.rect = self.image.get_rect()
        self.image = self.image.convert_alpha()
        self.quakes = []
        self.rect.center = asteroid.rect.center
        self.new_quake()

    def new_quake(self):
            # This bit of code is just deciding whether to start a new quake
            # at the centre or whether to spin off a vertex of an existing quake
            developed_quakes = [ q for q in self.quakes if len(q.points) > 1 ]
            if len(developed_quakes) == 0:
                # If there are no earthquakes with a non-central vertex, new earthquake
                # has to start at the centre again
                starting_point = self.asteroid.centre
            else:
                if random.randrange(2) == 0:
                    starting_point = self.asteroid.centre
                else:
                    quake = developed_quakes[random.randrange(len(developed_quakes))]
                    point_number = random.randrange(1,len(quake.points))
                    starting_point = quake.points[point_number]
                    orientation = quake.orientation * (-1)**(len(quake.points) - point_number + 1)
            if starting_point == self.asteroid.centre:
                orientation = [-1,1][random.randrange(2)]
            
            # Create a new quake
            self.quakes.append(Quake(starting_point,starting_point,orientation,self.asteroid.current_life))

    def update(self):
        # Are we at the end of a line - if so, choose a new point
        for quake in self.quakes:
            if quake.current_point == quake.target_point:
                quake.points.append(quake.target_point)
                quake.orientation = -1 * quake.orientation
                quake.target_point = self.next_target_point(quake.target_point,self.asteroid.centre,quake.points[0],self.asteroid.radius,quake.orientation)

            # Calculate the current point we should be drawing to        
            quake.current_point = self.next_current_point(self.asteroid.current_life,quake.initial_asteroid_life,self.asteroid.radius,self.asteroid.centre,quake.points[0],quake.points[-1],quake.target_point)
            
            # Calculate the list of points which draw out the earthquake
            points_to_draw = quake.points + [quake.current_point]

            if self.asteroid.current_life > 0:
                # Want the colour to fade from black to red
                proportion = (1 - float(self.asteroid.current_life) / quake.initial_asteroid_life)
                X = int(proportion * 255)
                COLOUR = (X,0,0)
                # Draw the earthquake
                pygame.draw.lines(self.image, COLOUR, False, points_to_draw,1)
        
    def next_target_point(self,current_target_point,planet_centre,initial_point,planet_radius,orientation):
        # choose a new target_point:
        #  * in the circle (inc. on edge)
        #  * calculate distance from centre of current target point and say this is x percent of full planet radius.  Then new point
        #    must be at a distance from the centre of at least x + 10 percent of full planet radius (or be on the planet edge)
        #  * imagine line from centre to old target point.  Now imagine perpendicular bisector to that which also passes through old target point.
        #    New point must be on the far side of this bisector (from the circle centre).
        #    Point is that this means no point on the new line will have a shorter distance to circle centre than current point
        
        # Choose distance from centre of new point
        #distance_of_current_point = math.sqrt(sum([ (current_target_point[i] - planet_centre[i]) ** 2 for i in [0,1] ]))
        #distance_proportion = float(distance_of_current_point) / planet_radius
        
        
        distance_of_current_point = math.sqrt(sum([ (current_target_point[i] - planet_centre[i]) ** 2 for i in [0,1] ]))
        distance_proportion = float(distance_of_current_point) / planet_radius
        
        if distance_proportion + 0.1 >= 1:
            new_distance_proportion = 1
        else:
            #new_distance_proportion = random.randrange(math.floor((distance_proportion + 0.1)*100),100)/100.0
            new_distance_proportion = random.randrange(math.floor((distance_proportion + 0.1)*100),min([math.floor((distance_proportion + 0.5)*100),100]))/100.0
        distance = new_distance_proportion * planet_radius

        
        # Let's see if we can have a pure math way of getting the point
        # 1) Choose the distance we want the next point to be from the centre of the circle.
        #     This is done above
        # 2a) Choose an angle less than 90 degrees - new point will be at this angle to the current point
        #    This is to make sure our new line does keep moving away from the centre of the circle
        # 2b) Choose whether this angle will be measured clockwise or anti-clockwise from line from centre to current point
        #    Perhaps we should ensure we go one way, then the other, etc.
        if current_target_point == planet_centre: angle = random.randrange(180)
        else: angle = random.randrange(30,90)
        
        # 3) Solve the equation - we want a point lying on the line at this angle that is the new distance from the centre
        # self.planet_centre = O
        # self.current_point = A
        # new target point will be B
        # n1 = unit vector along OA
        # n2 = unit vector perpendicular to n1
        
        OA = tuple([ (current_target_point[i] - planet_centre[i]) for i in [0,1] ])
        mod_OA = math.sqrt(sum([ OA[i]**2 for i in [0,1] ]))           
        if current_target_point == planet_centre:
            # choose n1 to be in direction of angle
            #n1 = (math.sin(angle * math.pi / 180.0),math.cos(angle * math.pi / 180.0))
            n1 = (1,0)
        else:
            # n1 = OA / |OA|
            n1 = tuple([ OA[i]/mod_OA for i in [0,1] ])
        
        
        # n2 is obtained by n1 by rotating 90 degrees.  ie. using the matrix [ [0,-1],[1,0] ]
        # This confused me at first - it's because pygame gives the (0,0) coordinate at the top left.
        if orientation == 1: n2 = tuple([-n1[1],n1[0]])
        else: n2 = tuple([n1[1],-n1[0]])
        
        # Unit vector in direction of AB is:
        #unit_AB = cos(angle * math.pi/180.0)n1 + sin(angle * math.pi/180.0)n2
        unit_AB = tuple([ math.cos(angle * math.pi/180.0)*n1[i] + math.sin(angle * math.pi/180.0)*n2[i] for i in [0,1] ])
        
        # Now, OA + x * unit_AB = OB and |OA + x * unit_AB| = |OB| = new_distance, where x > 0
        # -> solve for x
        # get a quadratic equation, ax^2 + bx + c = 0, where:
        a = 1 # a = mod_AB
        b = 2 * sum([ OA[i]*unit_AB[i] for i in [0,1] ])  # 2 * OA dot unit_AB
        c = mod_OA ** 2 - distance ** 2
        
        # Solutions for x are : (-b +- (b^2 -4ac)^(1/2))/2a - I take bigger one.
        if b**2 -4*a*c < 0:
            print "No real solutions in next_target_point - b^2 -4ac = %f" % (b**2 - 4*a*c)
            x1 = -b/2*a
        else:
            (x1,x2) = ((-b + math.sqrt(b**2 - 4*a*c))/2*a,(-b - math.sqrt(b**2 - 4*a*c))/2*a)
        # So OB is OA + x*unit_AB
        OB = [ OA[i] + x1 * unit_AB[i] for i in [0,1] ]
        B = tuple([ int(planet_centre[i] + OB[i]) for i in [0,1] ])
        return B
     
    def next_current_point(self,current_life,original_life,planet_radius,planet_centre,initial_point,last_point,next_point):
        # Calculate next point P
        # This is the point P that lies on the line 'points[-1] -> target_point' and
        # whose distance from the centre is proportional to the life of the planet.
        def mod(vector):
            return math.sqrt(sum([ vector[i]**2 for i in [0,1] ]))
        def dot(v1,v2):
            return sum([ v1[i]*v2[i] for i in [0,1] ])
        
        # When life is proportion life_proportion of original life (life at start of earthquake),
        # mod_OP = mod_start_point + (1 - life_proportion) * (planet_radius - mod_start_point)
        life_proportion = float(current_life) / original_life
        
        
        
        O = planet_centre
        I = initial_point # start of earthquake
        A = last_point
        B = next_point
        OI = tuple([ I[i] - O[i] for i in [0,1] ])
        OA = tuple([ A[i] - O[i] for i in [0,1] ]) # vector from centre to the last (corner) point of earthquake
        AB = tuple([ B[i] - A[i] for i in [0,1] ]) # vecor from last corner point to next target point
        OB = tuple([ B[i] - O[i] for i in [0,1] ]) # vector from centre to next point
        mod_OP = mod(OI) + (1-life_proportion)*(planet_radius - mod(OI))
        if mod_OP == 0: return last_point

        # because we're rounding to integers to get pixels, think it can be the case we get
        # mod_OP < mod(OA).  Just set mod_OP = mod(OA) in these cases
        if mod_OP <= mod(OA):
            mod_OP = mod(OA)
        # Bit of a hack - if I've gone too far, I just reset
        if mod(OB) <= mod(OA):
            P = B
        # If the next_point is already not far enough away from the centre, we jump straight to it
        elif mod_OP >= mod(OB):
            P = B
        else:
            # solving |OA + xAB| = mod_OP
            # (OA + xAB) dot (OA + xAB) = mod_OP ^ 2
            # ax^2 + bx + c = 0 where:
            (a,b,c) = (mod(AB)**2, 2*dot(OA,AB), mod(OA)**2 - mod_OP**2)
            
            #  Solutions for x are : (-b +- (b^2 -4ac)^(1/2))/2a
            if b**2 - 4*a*c < 0:
                # Need to work out why I'm getting unreal roots to this
                print "b^2 -4ac is %f" % (b**2 - 4*a*c)
                print "O is %s" % str(O)
                print "OA is %s" % str(OA)
                print "AB is %s" % str(AB)
                print "OB is %s" % str(OB)
                print "mod_OA is %s" % str(mod(OA))
                print "mod_OP is %s" % str(mod_OP)
                print "mod_OB is %s" % str(mod(OB))
                print "(a,b,c) are (%s,%s,%s)" % (str(a),str(b),str(c))
                sys.exit()
                x = -b/(2*a)
            else:
                x = (-b + math.sqrt(b**2 - 4*a*c))/(2*a)
            OP = tuple([ OA[i] + x*AB[i] for i in [0,1] ])
            P = tuple([ int(O[i] + OP[i]) for i in [0,1] ])
        return P
                
 
class Launcher(pygame.sprite.Sprite):
    
    def __init__(self,asteroid,degree,size,accel_magnitude,time_spacing):
        # A launcher will be a triangle that sits on the surface (maybe a bit beneath the surface, as the base
        # of the triangle will be flat but the asteroid surface will be curved) of an asteroid and will be
        # able to fire missiles.
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.asteroid = asteroid
        self.image = pygame.Surface((size, size))
        self.image.set_colorkey(BLACK) # make the black background transparent
        pygame.draw.polygon(self.image, (100,100,100), [(0,size),(size/2,0),(size,size)])
        self.base_image = self.image
        #rotate surf by DEGREE amount degrees
        self.degree = degree
        self.size = size
        self.image = pygame.transform.rotate(self.image, degree)
        #get the rect of the rotated surface
        self.rect = self.image.get_rect()
        self.mask = pygame.mask.from_surface(self.image)
        (x,y) = asteroid.rect.center
        (X,Y) = ((x - asteroid.radius * math.sin(degree * math.pi / 180.0)),(y - asteroid.radius * math.cos(degree * math.pi / 180.0)))
        # The vector from the centre of the asteroid to the centre of the launcher gives our desired initial velocity direction for missiles
        mod_v = math.sqrt((X-x) ** 2 + (Y-y) ** 2)
        self.initial_missile_velocity_unit_vector = ((X-x)*1.0/mod_v,(Y-y)*1.0/mod_v)
        self.rect.center = (X,Y)
        self.image = self.image.convert_alpha()
        self.accel_magnitude = accel_magnitude
        self.timer = 0
        self.time_spacing = time_spacing
        self.immune_missiles = {}
        self.size = size

    def update(self,msecs):
        # We decide whether to launch a missile.
        # If one is created, we fire it with an appropriate velocity vector
        # The initial contact with the missile shouldn't blow up the launcher,
        # but subsequent contact should.
        self.timer += msecs
        
        if self.timer > self.time_spacing:
            self.timer = 0
            # Missile properties below could be properties of the launcher, of course
            missile = Missile(center=self.rect.center,fuel=2000,shield=100,accel_magnitude=self.accel_magnitude,radius=10,colour=RED)
            missile.update(1) # To set the shield on initially
            speed = 100
            # Now wish to set an appropriate initial velocity for the missile - in the direction of the launcher
            (missile.x_vel,missile.y_vel) = (speed*self.initial_missile_velocity_unit_vector[0],speed*self.initial_missile_velocity_unit_vector[1])
            # Launcher is to be immune to contact with this missile for the first half second
            # Append missile and a timer to a list
            self.immune_missiles[missile] = 0
        # Update the missile launcher colour
        self.update_colour()
        # Add msecs to all timers in the immune_missiles list
        for missile in self.immune_missiles.keys():
            self.immune_missiles[missile] += msecs
            if self.immune_missiles[missile] >= 900:
                del self.immune_missiles[missile]
                
    def update_colour(self):
        # Called by self.update()
        # Want the launcher to get redder as it gets close to firing rocket.        
        #Normal colour (Grey) = (100,100,100)
        #RED = (255, 0, 0)
        # t=0 -> Grey, t=self.time_spacing -> Red, want an x^2 relationship so it gets red quicker and quicker
        self.image = self.base_image
        proportion = float(self.timer)/self.time_spacing
        GREY = (100,100,100)
        
        if proportion > 1:
            colour = list(RED)
        else:
            colour = [ (GREY[i] + int((RED[i] - GREY[i]) * (proportion ** 2))) for i in [0,1,2] ]
        pygame.draw.polygon(self.image, colour, [(0,self.size),(self.size/2,0),(self.size,self.size)])
        self.image = pygame.transform.rotate(self.image, self.degree)
        
        
        
class Explosion(pygame.sprite.Sprite):
    explosions = []
    def __init__(self,(x,y),initial_radius, final_radius):
        pygame.sprite.Sprite.__init__(self, self.groups)
        Explosion.explosions.append(self)
        self.image = pygame.Surface((2*final_radius, 2*final_radius))
        self.image_copy = self.image.copy()
        self.image_copy.fill(BLACK)

        self.initial_radius = initial_radius
        self.final_radius = final_radius
        self.current_radius = int(self.initial_radius)
        (self.x,self.y) = (x,y)
        self.timer = 0
        self.draw_time = 0
        self.draw()
        
        

    def draw(self):

        self.image = self.image_copy.copy()
        self.rect = self.image.get_rect()
        self.image.set_colorkey(BLACK) # make the black background transparent

        for temp_radius in range(self.current_radius,6,-5):
            colour_factor = random.randrange(0,256)
            colour = (255, colour_factor, 0) 
            pygame.draw.circle(self.image, colour, self.rect.center, temp_radius,6)
        self.image.set_alpha(230)
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.center = (self.x,self.y)
        screen.blit(self.image,self.rect)
        
    def clear(self):
        screen.blit(self.image_copy,self.rect)

    def update_angle_to_explosion(self,item):
        (x,y) = (item.x - self.rect.centerx,item.y - self.rect.centery)
        if x == 0:
            #if y == 0:
            #    return (0,0)  # Click on dead center of ball, no force / acceleration applied
            if y >= 0: self.angle = math.pi / 2
            if y < 0: self.angle = (3.0/2) * math.pi
        else:
            if x >= 0 and y >= 0 or x >= 0 and y < 0: self.angle = math.atan((1.0*y)/x)
            if x < 0 and y >= 0 or x < 0 and y < 0: self.angle = math.atan((1.0*y)/x) + math.pi        
    
    def update(self,msecs):
        self.timer += msecs
        # The line below slows the explosion down a bit
        if self.timer > self.draw_time + 20:   
            self.current_radius += 2
            self.draw_time = self.timer

        if self.current_radius >= self.final_radius:
            # Explosion has reached maximum size - get rid of it
            self.clear()
            Explosion.explosions.remove(self)
            self.kill()

class Text(pygame.sprite.Sprite):
    def __init__(self):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.font = pygame.font.Font(None, 36)
        text_string = ''
        self.image = self.font.render(text_string, 0, WHITE, BLACK)
        self.image.set_colorkey(BLACK) # make the black background transparent
        self.rect = self.image.get_rect()
        
    def update(self):
        # Draw new text.  Important to make sure the text isn't transparent so we can clear it
        fuel = "Fuel (%d)" % game.ball.fuel
        shield = "Shield (%d)" % game.ball.shield
        #position = "Position (%d,%d)" % (game.ball.rect.centerx,game.ball.rect.centery)
        velocity = "Velocity (%0.1f, %0.1f)" % (game.ball.x_vel,game.ball.y_vel)
        speed = "Speed (%0.1f)" % (math.sqrt(game.ball.x_vel ** 2 + game.ball.y_vel ** 2))
        #acceleration = "Acceleration (%0.1f, %0.1f)" % (game.ball.x_accel,game.ball.y_accel)
        fps = "FPS: %0.1f" % clock.get_fps()
        level = "Level: %s" % game.level
        text_string = fuel.ljust(20) + shield.ljust(20) + fps.ljust(20) + velocity.ljust(30) + speed.ljust(20) + level.ljust(20)
        self.image = self.font.render(text_string, 0, WHITE, BLACK)

class LandingStrip(pygame.sprite.Sprite):
    def __init__(self,topleft=(0,0),length=30):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface((length, 10))
        self.length = length
        self.maxLandingSpeed = 30
        self.image.set_colorkey(BLACK) # make the black background transparent
        self.rect = self.image.get_rect()
        pygame.draw.rect(self.image, BLUE, (0,0,length,10))
        self.image = self.image.convert_alpha()
        self.mask = pygame.mask.from_surface(self.image)
        self.rect.topleft = topleft
    
    def update(self):
        # If the ship is close and moving too fast or not in position, go red
        # if the ship is close, in right x,y position and moving slow enough, go green
        # if ship is too far away, go back to normal colour
        if math.sqrt((game.ball.x - self.rect.center[0]) ** 2 + (game.ball.y - self.rect.center[1]) ** 2) < 100:
            if abs(math.sqrt(game.ball.x_vel ** 2 + game.ball.y_vel ** 2)) > self.maxLandingSpeed:
                pygame.draw.rect(self.image,RED,(0,0,self.length,10))
            else:
                pygame.draw.rect(self.image,YELLOW,(0,0,self.length,10))
        else:
            pygame.draw.rect(self.image,BLUE,(0,0,self.length,10))
        
        


#############################################################################################

# set up the window
screen = pygame.display.set_mode((1300, 650), 0, 32)    # Can use pygame.FULLSCREEN instead of 0

background = pygame.Surface(screen.get_size())  # Create empty pygame surface
background.fill(BLACK)     # Fill the background white color (red,green,blue)
background = background.convert()  # Convert Surface to make blitting faster
screen.blit(background, (0, 0))

pygame.display.set_caption('Lander')
gameRect = screen.get_rect()
clock = pygame.time.Clock()
NOT_YET = True



###############################################################################################

# run the game loop
while True:

    msecs = clock.tick(100) 
    # Get events from the event queue
    for event in pygame.event.get():
        if event.type == var.QUIT:
            pygame.quit()
            sys.exit()
    
    
    keystate = pygame.key.get_pressed()
    
    # Currently, hitting return starts a new game
    if keystate[var.K_RETURN]:
        game = Game()
        NOT_YET = False
    #if keystate[var.K_n]:   # registers several hits, so can jump many levels in one!
    #    game.next_level()   
    if NOT_YET == True: continue
            
    game.keystate = keystate    


    # COLLISIONS        
    # First we do a quick cheap check to see if anything might be colliding with the ball ...
    ballStaticSolidsCols_dict = pygame.sprite.groupcollide(game.ballGroup,game.staticSolidsGroup,False,False)
    missilesStaticSolidsCols_dict = pygame.sprite.groupcollide(game.missileGroup, game.staticSolidsGroup, False, False)
    ballMissileCols_dict = pygame.sprite.groupcollide(game.ballGroup, game.missileGroup,False,False)
    ballLauncherCols_dict = pygame.sprite.groupcollide(game.ballGroup, game.launcherGroup,False,False)
    missileMissileCols_dict = pygame.sprite.groupcollide(game.missileGroup, game.missileGroup,False,False)
    ballExplosionCols_dict = pygame.sprite.groupcollide(game.ballGroup,game.explosionGroup,False,False)
    missilesExplosionCols_dict = pygame.sprite.groupcollide(game.missileGroup,game.explosionGroup,False,False)
    launcherExplosionCols_dict = pygame.sprite.groupcollide(game.launcherGroup,game.explosionGroup,False,False)
    asteroidExplosionCols_dict = pygame.sprite.groupcollide(game.asteroidGroup,game.explosionGroup,False,False)
    missileLauncherCols_dict = pygame.sprite.groupcollide(game.missileGroup, game.launcherGroup,False,False)
    

    
    # Has the ball collided with anything that isn't a missile?
    # There's only one ball, but using the group is useful because if we die I can remove the ball
    # from the group and these checks stops being applicable.
    for (ball,items) in ballStaticSolidsCols_dict.items():
        for item in items:
            # Now we accurately check out those possible collisions
            if pygame.sprite.collide_mask(ball,item):
                # Below is the coordinate in the ball mask where the overlap has hit
                (x,y) = ball.mask.overlap(item.mask, (item.rect.topleft[0] - ball.rect.topleft[0],item.rect.topleft[1] - ball.rect.topleft[1]))
                if ball.shield_active == False and ball.landed(game.landingStrip) == False and game.game_over == False:
                    # We have no shield up and we've not landed ...
                    game.it_is_game_over()
                elif ball.landed(game.landingStrip) == True:
                    print "You've landed!"
                    game.next_level()
                else:
                    # We are colliding with something solid!
                    ball.fixed_collision((x,y))
    
    # Has a missile collided with anything solid - ground or asteroid or landing pad - that isn't the ball or another missile?
    for (missile, items) in missilesStaticSolidsCols_dict.items():
        for item in items:
            # Now we accurately check out those possible collisions
            if pygame.sprite.collide_mask(missile,item):
                # Below is the coordinate in the missile mask where the overlap has hit
                (x,y) = missile.mask.overlap(item.mask, (item.rect.topleft[0] - missile.rect.topleft[0],item.rect.topleft[1] - missile.rect.topleft[1]))
                if missile.shield_active == False:
                    # Remove missile from all groups and have an explosion
                    missile.kill()
                    Explosion(missile.rect.center,missile.radius,6*missile.radius)
                else:                 
                    # There's a bug where, due to the land shape, missiles can kind of be funnelled into the ground and get stuck there.
                    # So if there's not only a collision but also the centre of the missile is within the static solid, it explodes
                    # whether it's shield is up or not
                    if item.rect.collidepoint(missile.rect.center):
                        if item.mask.get_at((missile.rect.centerx - item.rect.left,missile.rect.centery - item.rect.top)):
                            missile.kill()
                            Explosion(missile.rect.center,missile.radius,6*missile.radius)
                        else:
                            missile.fixed_collision((x,y))
                    else:
                        # Missile is colliding in a normal way (ie. it's centre point is not within the item rect) with it's shield on ...
                        missile.fixed_collision((x,y))

    # Has a missile collided with the ball!?
    for (ball,missiles) in ballMissileCols_dict.items():
        for missile in missiles:
            # Now we accurately check out those possible collisions
            if pygame.sprite.collide_mask(ball,missile):
                # Missile should blow up
                missile.kill()
                Explosion(missile.rect.center,missile.radius,6*missile.radius)    ###
                # Ball survives if shield is on, blows up if it isn't
                if ball.shield_active == False:
                    game.it_is_game_over()
                # If we have our shield on, missile blows up and nothing directly 
                # happens to ship.  However, the explosion will push us away, so
                # next step is to test for explosion collisions.
               
    for (ball,launchers) in ballLauncherCols_dict.items():
        for launcher in launchers:
            # Now we accurately check out those possible collisions
            if pygame.sprite.collide_mask(ball,launcher):
                launcher.kill()
                Explosion(launcher.rect.center,launcher.size/2.0,2*launcher.size)  
                # Ball survives if shield is on, blows up if it isn't
                if ball.shield_active == False:
                    game.it_is_game_over()
                
    # Has a missile collided with another missile!?
    # I currently don't bother to get a missile to turn on it's shield and bounce off other missiles
    for (miss,missiles) in missileMissileCols_dict.items():
        # Check they are both still in the group, as we may have treated
        # this collision already
        for missile in missiles:
            if game.missileGroup.has([miss,missile]):
                if missile != miss:
                    if pygame.sprite.collide_mask(miss,missile):
                        # Missile should blow up
                        missile.kill()
                        Explosion(missile.rect.center,missile.radius,6*missile.radius)    ###
                        miss.kill()
                        Explosion(miss.rect.center,miss.radius,6*miss.radius)                    
        
        # For now, if two missiles collide, rather than treating each as though they've
        # hit a static object, I'll just make them both blow up.

    for (missile,launchers) in missileLauncherCols_dict.items():
        # Check they are both still in the group, as we may have treated
        # this collision already
        if game.missileGroup.has([missile]) and game.launcherGroup.has(launchers):
            for launcher in launchers:
                if missile not in launcher.immune_missiles:
                    if pygame.sprite.collide_mask(miss,missile):
                        # Missile and launcher should blow up
                        missile.kill()
                        Explosion(missile.rect.center,missile.radius,6*missile.radius)    ###
                        launcher.kill()
                        Explosion(launcher.rect.center,launcher.size/2.0,2*launcher.size)  
        
    # Has a missile, ball or launcher collided with any explosions?
    # In this case, they should be propelled away from the centre of the explosion
    # Perhaps a stronger force should be applied the closer they are to the centre of
    # the explosion
    for (ball,explosions) in ballExplosionCols_dict.items():
        for explosion in explosions:
            if pygame.sprite.collide_mask(ball,explosion):
                # Contact with an explosion kills you if it's not shielded  
                if ball.shield_active == False:
                    game.it_is_game_over()
                else:
                    # Ball should get pushed away from the cente of the explosion
                    explosion.update_angle_to_explosion(ball)
                    ball.external_acceleration(100,explosion.angle) # (value,explosion.angle)
                    
    for (missile,explosions) in missilesExplosionCols_dict.items():
        for explosion in explosions:
            if pygame.sprite.collide_mask(missile,explosion):
                # Missile should blow up if it's shield isn't on
                if missile.shield_active == False:
                    missile.kill()
                    Explosion(missile.rect.center,missile.radius,6*missile.radius)
                else:
                    explosion.update_angle_to_explosion(missile)
                    missile.external_acceleration(100,explosion.angle) # (value,explosion.angle)

    for (launcher,explosions) in launcherExplosionCols_dict.items():
        for explosion in explosions:
            if pygame.sprite.collide_mask(launcher,explosion):
                    launcher.kill()
                    Explosion(launcher.rect.center,launcher.size/2.0,2*launcher.size)

    for (asteroid,explosions) in asteroidExplosionCols_dict.items():
        for explosion in explosions:
            if pygame.sprite.collide_mask(asteroid,explosion):
                    asteroid.lose_life(1)
                    if asteroid.current_life <= 0:
                        asteroid.kill()
                        asteroid.earthquake.kill()
                        Explosion(asteroid.rect.center,asteroid.radius,int(1.5*asteroid.radius))                     
            
    

        
    # UPDATE THE SCREEN
    # First job is to rub everything out
    for explosion in Explosion.explosions:
        explosion.clear()
    game.textGroup.clear(screen,background)
    game.groundGroup.clear(screen,background)
    game.ballGroup.clear(screen,background)
    game.missileGroup.clear(screen,background)
    game.asteroidGroup.clear(screen,background)
    game.landingStripGroup.clear(screen,background)
    game.launcherGroup.clear(screen,background)
    #game.explosionGroup.clear(screen,background)
    for engine in Engine.engines:
        engine.clear()
    game.earthquakeGroup.clear(screen,background)
    

    
    # Then draw everything again
    # Draw function for asteroids will be needed when explosions go over them
    for explosion in Explosion.explosions:
        explosion.draw()    
    #game.explosionGroup.draw(screen)
    game.textGroup.draw(screen)
    game.groundGroup.draw(screen)
    game.launcherGroup.draw(screen)
    game.asteroidGroup.draw(screen)
    game.landingStripGroup.draw(screen)
    for engine in Engine.engines:
        engine.draw()
    game.missileGroup.draw(screen)
    game.ballGroup.draw(screen)
    game.earthquakeGroup.draw(screen)
    
    # Update everything that needs updating
    for explosion in Explosion.explosions:
        explosion.update(msecs)
    #game.explosionGroup.update(msecs)
    game.ballGroup.update(msecs)
    game.missileGroup.update(msecs)
    game.textGroup.update()
    game.launcherGroup.update(msecs)
    game.landingStripGroup.update()
    game.earthquakeGroup.update()
    
    # Currently, the update below draws the earthquakes.
    # Should move this to the draw updates above.
    #game.asteroidGroup.update(msecs)



    
    # draw the window onto the screen
    pygame.display.update()  