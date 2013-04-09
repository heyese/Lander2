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


class Earthquake():
    '''An earthquake is simply a list of points'''
    def __init__(self,planet_centre,planet_radius,planet_life,starting_point,orientation):
        self.planet_centre = planet_centre
        self.planet_radius = planet_radius
        self.initial_planet_life = planet_life
        self.points = []
        self.target_point = starting_point
        self.current_point = starting_point
        #self.orientation = [-1,1][random.randrange(2)]
        self.orientation = orientation
        self.initial_distance_to_edge = self.planet_radius - math.sqrt(sum([ (starting_point[i] - planet_centre[i])**2 for i in [0,1] ]))

    def update(self,planet_life):
        # Are we at the end of a line - if so, choose a new point
        print "self.current_point is %s, self.target_point is %s" % (str(self.current_point),str(self.target_point))
        if self.current_point == self.target_point:
            self.points.append(self.target_point)
            self.orientation = -1 * self.orientation
            self.target_point = self.next_target_point(self.target_point,self.planet_centre,self.points[0],self.planet_radius,self.orientation)
            print "new target_point is %s" % str(self.target_point)

        # Calculate the current point we should be drawing to        
        self.current_point = self.next_current_point(planet_life,self.initial_planet_life,self.planet_radius,self.planet_centre,self.points[0],self.points[-1],self.target_point)
        
        # Return the list of points which draw out the earthquake
        return self.points + [self.current_point]
        
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
        
        distance_of_current_point = math.sqrt(sum([ (current_target_point[i] - initial_point[i]) ** 2 for i in [0,1] ]))
        distance_proportion = float(distance_of_current_point) / self.initial_distance_to_edge
        
        if distance_proportion + 0.1 >= 1:
            new_distance_proportion = 1
        else:
            #new_distance_proportion = random.randrange(math.floor((distance_proportion + 0.1)*100),100)/100.0
            new_distance_proportion = random.randrange(math.floor((distance_proportion + 0.1)*100),min([math.floor((distance_proportion + 0.5)*100),100]))/100.0
            print "New distance proportion is %s" % new_distance_proportion
        distance = new_distance_proportion * self.initial_distance_to_edge

        
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
        
        OA = tuple([ (self.current_point[i] - planet_centre[i]) for i in [0,1] ])
        mod_OA = math.sqrt(sum([ OA[i]**2 for i in [0,1] ]))           
        if current_target_point == planet_centre:
            # choose n1 to be in direction of angle
            #n1 = (math.sin(angle * math.pi / 180.0),math.cos(angle * math.pi / 180.0))
            n1 = (1,0)
        else:
            # n1 = OA / |OA|
            n1 = tuple([ OA[i]/mod_OA for i in [0,1] ])
        
        
        # n2 is obtained by n1 by rotating 90 degrees.  ie. using the matrix [ [0,1],[-1,0] ]
        if orientation == 1: n2 = tuple([n1[1],-n1[0]])
        else: n2 = tuple([-n1[1],n1[0]])
        
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
        
        # Distance from initial point to 
        mod_OP = (1 - float(current_life) / original_life) * self.initial_distance_to_edge
        if mod_OP == 0: return last_point
        O = initial_point  # this should be earthquake starting point
        A = last_point
        B = next_point
        OA = tuple([ A[i] - O[i] for i in [0,1] ]) # vector from centre to the last (corner) point of earthquake
        AB = tuple([ B[i] - A[i] for i in [0,1] ]) # vecor from last corner point to next target point
        OB = tuple([ B[i] - O[i] for i in [0,1] ]) # vector from centre to next point
        
        # Bit of a hack - if I've gone too far, I just reset
        if mod(OB) <= mod(OA):
            P = B
        # If the next_point is already not far enough away from the centre, we jump straight to it
        elif mod_OP >= mod(OB):
            P = B
        elif mod_OP <= mod(OA):
            # This shouldn't happen, but there's some rounding somewhere, perhaps
            print "Set P = A since mod_OA was %s and mod_OA was %s" % (str(mod_OP),str(mod(OA)))
            P = A
        else:
            # solving |OA + xAB| = mod_OP
            # (OA + xAB) dot (OA + xAB) = mod_OP ^ 2
            # ax^2 + bx + c = 0 where:
            (a,b,c) = (mod(AB)**2, 2*dot(OA,AB), mod(OA)**2 - mod_OP**2)
            #print "(a,b,c) are (%s,%s,%s)" % (a,b,c)
            
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
        
class Planet(pygame.sprite.Sprite):
    def __init__(self,(x,y),radius):
        pygame.sprite.Sprite.__init__(self, self.groups)
        self.image = pygame.Surface((2*radius, 2*radius))
        self.radius = radius
        self.image.set_colorkey(BLACK)
        self.rect = self.image.get_rect()
        self.planet_centre = self.rect.center
        pygame.draw.circle(self.image, WHITE, self.rect.center, radius, 0)

        self.mask = pygame.mask.from_surface(self.image)
        self.original_life = 300
        self.current_life = self.original_life
        
        self.rect.center = (x,y)
        self.earthquakes = []
        self.earthquakes.append(Earthquake(self.planet_centre,self.radius,self.current_life,self.planet_centre,[-1,1][random.randrange(2)]))        

            
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
        print "self.current_life is %s" % self.current_life
        # Every so often, if planet is destroyed a bit, another earthquake starts
        # Say we want an average of five earthquakes per planet?
        # And that this function gets called every time planet loses 1 health.
        
        if random.randrange(self.original_life / 5) == 0 and self.current_life != 0:
            print "New earthquake!!"
            # Pick a random point on an existing earthquake or the centre
            starting_points = []
            for quake in self.earthquakes:
                starting_points.extend(quake.points)
            starting_points = list(set(starting_points))
            starting_point = self.planet_centre #starting_points[random.randrange(len(starting_points))]
            self.earthquakes.append(Earthquake(self.planet_centre,self.radius,self.current_life,starting_point,[-1,1][random.randrange(2)]))
        
        
        if self.current_life != 0:
            for quake in self.earthquakes:
                points = quake.update(self.current_life)
                # Draw the earthquake
                pygame.draw.lines(self.image, RED, False, points,4)


        


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
    if pygame.mouse.get_pressed()[2] == True:
        # Earthquake !!!
        planetGroup.remove(planet)
        planet = Planet((600,300),100)
    
    
    
    # draw the window onto the screen
    pygame.display.update()  