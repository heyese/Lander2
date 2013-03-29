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

# set up the window
windowSurface = pygame.display.set_mode((1200, 650), 0, 32)
pygame.display.set_caption('Broken Planet')
gameRect = windowSurface.get_rect()

background = pygame.Surface(windowSurface.get_size())  # Create empty pygame surface
background.fill(BLACK)     # Fill the background white color (red,green,blue)
background = background.convert()  # Convert Surface to make blitting faster
windowSurface.blit(background, (0, 0))



class Planet(pygame.sprite.Sprite):
    def __init__(self,(x,y),radius):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface((2*radius, 2*radius))
        self.radius = radius
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.image_copy = self.image.copy()
        pygame.draw.circle(self.image, WHITE, self.rect.center, radius, 0)
        self.rect.center = (x,y)

        self.mask = pygame.mask.from_surface(self.image)
        self.points = [(x,y)]
        self.target_point = None
        self.current_point = (x,y)
        self.original_life = 1000
        self.current_life = self.original_life
        
    def update(self,msecs):
        # Idea is that an earthquake slowly spreads out from the centre
        # Do this by slowly drawing a series of lines from the centre
        # We draw each line gradually - point by point - until we finish off one line.
        # Then we choose the end point for the next line gradually make our way along that.
        # As you go along each line, you have to always be getting further away from the centre
        # At any point, your distance from the centre of the circle has to be inversely proportional to the life left of the planet.
        # Once I've worked this out, I want to be able to have multiple earthquakes, starting at different times.
        # But maybe all reaching the edge at the same time, or maybe all increasing at same rate with planet being destroyed when first reaches the edge.
        
        # Planet is being destroyed
        self.current_life = self.current_life - 1  # Actually, the explosion function should decrease this - eg. if in contact with two explosions, life you decrease at twice rate
        
        # Are we at the end of a line - if so, choose a new point
        if self.current_point == self.target_point or self.target_point == None:
            if self.target_point != None:  self.points.append(self.target_point)
            # choose a new target_point:
            #  * in the circle (inc. on edge)
            #  * calculate distance from centre of current target point and say this is x percent of full planet radius.  Then new point
            #    must be at a distance from the centre of at least x + 10 percent of full planet radius (or be on the planet edge)
            #  * imagine line from centre to old target point.  Now imagine perpendicular bisector to that which also passes through old target point.
            #    New point must be on the far side of this bisector (from the circle centre).
            #    Point is that this means no point on the new line will have a shorter distance to circle centre than current point
            
            # Choose distance from centre of new point
            if self.target_point == None: distance_proportion = 0
            else:
                distance_of_current_point = math.sqrt(sum([ (self.target_point[i] - self.rect.center[i]) ** 2 for i in [0,1] ]))
                distance_proportion = distance_of_current_point / self.radius
            if distance_proportion + 0.1 >= 1:
                new_distance_proportion = 1
            else:
                new_distance_proportion = random.randrange(math.floor((distance_proportion + 0.1)*100),100)/100.0
            new_distance = int(new_distance_proportion * self.radius)
            print "New distance is %s" % new_distance
            
            # Draw a circle with new_distance radius on the copied surface and use mask.outline to get coordinates
            self.temp_image = self.image_copy.copy()
            self.temp_rect = self.temp_image.get_rect()
            pygame.draw.circle(self.temp_image, WHITE, self.temp_rect.center, new_distance, 2)
            self.temp_mask = pygame.mask.from_surface(self.temp_image)
            pixels = self.temp_mask.outline(10)
            pixel = pixels[random.randrange(len(pixels))]
            print "pixel is %s" % str(pixel)
            self.target_point = [ sum([pixel[i],self.rect.topleft[i]]) for i in [0,1] ]
            print "target point is %s" % str(self.target_point)
            
            
            '''
            # Now pick the new point
            if self.target_point = self.rect.center:
                # pick any point
            else:
                # Pick a point on other side of the perpendicular bisector to line centre -> target_point.
            #next_point = ...
            #self.current_point = next_point
            return
            '''
        '''
        # Now we have next destination point
        # Choose how far along the line self.points[-1] -> self.target_point we should be drawing
        #ratio = float(self.current_life) / self.original_life
        #circle_radius = ratio * self.radius
        
        # Draw line self.points[-1] -> self.target_point
        # Draw circle (rect.center),circle_radius
        # Make masks of both and use mask.overlap to get the point of intersection.  If there isn't one, draw all the way to self.target_point
        
        # want the point of intersection of above circle and line segment self.points[-1] -> self.target_point
        #next_point = ...
        
        
        
        
        line_start = self.points[-1]
        line_end = self.target_point
        pygame.draw.line(self.image, RED, self.points[-1], next_point, width=2)
        '''

        


planetGroup = pygame.sprite.Group()
Planet.groups = planetGroup
planet = Planet((600,300),100)





# run the game loop
while True:


    # Update the screen
    planetGroup.clear(windowSurface,background)
    msecs = clock.tick(100) 
    planetGroup.draw(windowSurface)



    
    for event in pygame.event.get():
        if event.type == var.QUIT:
            pygame.quit()
            sys.exit()
    if pygame.mouse.get_pressed()[0] == True:
        # Earthquake !!!
        planetGroup.update(msecs)
    
    
    
    # draw the window onto the screen
    pygame.display.update()  