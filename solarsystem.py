"""
Idea: create a solar system with acceptable physic in python3
capable of different rendering different planets.
Graphic Viewer seperated from Game engine, later hopefully different
Viewers will be coded. At the moment only pygame
authors: Horst JENS, DI Johannes Nedwich
email: horstjens@gmail.com
contact: see http://spielend-programmieren.at/de:kontakt
license: gpl, see http://www.gnu.org/licenses/gpl-3.0.de.html
download: https://github.com/horstjens/roguebasin_python3
"""

import pygame
import random
#import math
# import inspect

import os


def float_range(A, L=None, D=None):
    """
    Desc : This function generates a float range of numbers w/o using any library.
    source: https://www.techbeamers.com/python-float-range/#using-float-value-in-step-parameter

    Params :
    A (int/float) : First number in the range
    L (int/float) : Last number in the range
    D (int/float) : Step or the common difference
    """
    #Use float number in range() function
    # if L and D argument is null set A=0.0 and D = 1.0
    if L == None:
        L = A + 0.0
        A = 0.0
    if D == None:
        D = 1.0
    while True:
        if D > 0 and A >= L:
            break
        elif D < 0 and A <= L:
            break
        yield float("%g" % A) # return float number
        A = A + D



def gridpos_to_pixelvector(gridpos):
    x,y,z = gridpos
    px = Viewer.zero[0]+ Viewer.grid_size[0] * x
    py = Viewer.zero[1]+ Viewer.grid_size[1] * y
    return pygame.math.Vector2(px,py)

def pixel_to_gridvector(pixelpos):
    px, py = pixelpos
    x = (px - Viewer.zero[0]) / Viewer.grid_size[0]
    y = (py - Viewer.zero[1]) / Viewer.grid_size[1]
    return pygame.math.Vector3(x,y,0)



def minmax(value, lower_limit=-1, upper_limit=1):
    """constrains a value inside two limits"""
    value = max(lower_limit, value)
    value = min(upper_limit, value)
    return value


def make_text(text="@", font_color=(255, 0, 255), font_size=48, font_name="mono", bold=True, grid_size=None):
    """returns pygame surface with text and x, y dimensions in pixel
       grid_size must be None or a tuple with positive integers.
       Use grid_size to scale the text to your desired dimension or None to just render it
       You still need to blit the surface.
       Example: text with one char for font_size 48 returns the dimensions 29,49
    """
    myfont = pygame.font.SysFont(font_name, font_size, bold)
    size_x, size_y = myfont.size(text)
    mytext = myfont.render(text, True, font_color)
    mytext = mytext.convert_alpha()  # pygame surface, use for blitting
    if grid_size is not None:
        # TODO error handler if grid_size is not a tuple of positive integers
        mytext = pygame.transform.scale(mytext, grid_size)
        mytext = mytext.convert_alpha()  # pygame surface, use for blitting
        return mytext, (grid_size[0], grid_size[1])

    return mytext, (size_x, size_y)


def write(background, text, x=50, y=150, color=(0, 0, 0),
          font_size=None, font_name="mono", bold=True, origin="topleft"):
    """blit text on a given pygame surface (given as 'background')
       the origin is the alignement of the text surface
    """
    if font_size is None:
        font_size = 24
    font = pygame.font.SysFont(font_name, font_size, bold)
    width, height = font.size(text)
    surface = font.render(text, True, color)

    if origin == "center" or origin == "centercenter":
        background.blit(surface, (x - width // 2, y - height // 2))
    elif origin == "topleft":
        background.blit(surface, (x, y))
    elif origin == "topcenter":
        background.blit(surface, (x - width // 2, y))
    elif origin == "topright":
        background.blit(surface, (x - width, y))
    elif origin == "centerleft":
        background.blit(surface, (x, y - height // 2))
    elif origin == "centerright":
        background.blit(surface, (x - width, y - height // 2))
    elif origin == "bottomleft":
        background.blit(surface, (x, y - height))
    elif origin == "bottomcenter":
        background.blit(surface, (x - width // 2, y))
    elif origin == "bottomright":
        background.blit(surface, (x - width, y - height))


# declare constants
class Game:
    """solar system"""
    gravconst = 1.1857e-4 # AU³ / M_E * a²    .. is the same as 0.000118...
    objects = {}
    deltas = [(1/365.25/24/60/60, "1 second"),(1/365.25/24/60, "1 minute"), (1/365.25/24, "1 hour"),
              (1/365.25, "1 day"), (2/365.25, "2 days"), (3/365.25, "3 days"),
              (4/365.25, "4 days"),(5/365.25, "5 days"), (6/365.25, "6 days"),
              (7/365.25, "1 week"),(14/365.25, "2 weeks"), (21/365.25, "3 weeks"),
              (28/365.25, "4 weeks"), (1/4, "1/4 year"), (1/2, "1/2 year"), (1, "1 year"),
              ]
    i = 3
    delta_t = deltas[i][0] #1 / 365.25  # = 1 day
    paused = False

    def __init__(self):
        print("Planet system intitalized...")
        # sun
        CelestialBody(mass=332937, position=pygame.math.Vector3(0,0,0),
                      velocity=pygame.math.Vector3(0,0,0))
        # earth
        CelestialBody() # default values

        CelestialBody(mass=0.7, position=pygame.math.Vector3(-2,0,0),
                      velocity = pygame.math.Vector3(0,-4,0))
        CelestialBody(mass=2.5, position=pygame.math.Vector3(2.6,2.5,0),
                      velocity=pygame.math.Vector3(1, -3, 0))

        #self.timestep()

    def timestep(self, seconds):
        if self.paused:
            return
        for a in Game.objects.values():
            acc = pygame.Vector3(0,0,0)
            for b in Game.objects.values():
                if a == b:
                    continue
                #distance_vector = a.position - b.position # vec3
                distance_vector = b.position - a.position
                acc += self.gravconst * b.mass / distance_vector.length()**3 * distance_vector # vec3
            a.position += self.delta_t * seconds *  (a.velocity + acc * self.delta_t * seconds /2)
            a.velocity += acc * self.delta_t * seconds


class CelestialBody:

    number = 0

    def __init__(self, mass=1,
                 position=pygame.math.Vector3(1,0,0),
                 velocity=pygame.math.Vector3(0,6.28,0)):
        self.mass = mass # earth units
        self.position = position # astronomical units (sol->earth distance)
        self.velocity = velocity # astronomical units per year
        # automatically assign a number
        self.number = CelestialBody.number
        CelestialBody.number += 1
        # automatically insert into Game.objects
        Game.objects[self.number] = self

class VectorSprite(pygame.sprite.Sprite):
    """base class for sprites. this class inherits from pygames sprite class"""
    number = 0
    numbers = {}  # { number, Sprite }

    def __init__(self, **kwargs):
        self._default_parameters(**kwargs)
        self._overwrite_parameters()
        pygame.sprite.Sprite.__init__(self, self.groups)  # call parent class. NEVER FORGET !
        self.number = VectorSprite.number  # unique number for each sprite
        VectorSprite.number += 1
        VectorSprite.numbers[self.number] = self
        self.create_image()
        self.distance_traveled = 0  # in pixel
        self.rect.center = (-300, -300)  # avoid blinking image in topleft corner
        if self.angle != 0:
            self.set_angle(self.angle)
        #self.visible = False # will be changed to True when age becomes positive

    def _overwrite_parameters(self):
        """change parameters before create_image is called"""
        pass

    def _default_parameters(self, **kwargs):
        """get unlimited named arguments and turn them into attributes
           default values for missing keywords"""

        for key, arg in kwargs.items():
            setattr(self, key, arg)
        if "layer" not in kwargs:
            self._layer = 4
        else:
            self._layer = self.layer
        # if "static" not in kwargs:
        #    self.static = False
        if "pos" not in kwargs:
            self.pos = pygame.math.Vector2(x=150, y=150)
        if "move" not in kwargs:
            self.move = pygame.math.Vector2(x=0, y=0)
        #if "acceleration" not in kwargs:
        #    self.acc = 0.0 # pixel/second speed is constant
        # TODO: acc, gravity-vector
        if "radius" not in kwargs:
            self.radius = 5
        if "width" not in kwargs:
            self.width = self.radius * 2
        if "height" not in kwargs:
            self.height = self.radius * 2
        if "color" not in kwargs:
            # self.color = None
            self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        if "bounce_on_edge" not in kwargs:
            self.bounce_on_edge = False
        if "kill_on_edge" not in kwargs:
            self.kill_on_edge = False
        if "warp_on_edge" not in kwargs:
            self.warp_on_edge = False
        if "angle" not in kwargs:
            self.angle = 0  # facing right?
        if "max_age" not in kwargs:
            self.max_age = None
        if "max_distance" not in kwargs:
            self.max_distance = None
        if "picture" not in kwargs:
            self.picture = None
        if "bossnumber" not in kwargs:
            self.bossnumber = None
        if "kill_with_boss" not in kwargs:
            self.kill_with_boss = False
        if "sticky_with_boss" not in kwargs:
            self.sticky_with_boss = False
        if "speed" not in kwargs:
            self.speed = None
        if "age" not in kwargs:
            self.age = 0  # age in seconds
        if "visible" not in kwargs:
            self.visible = False # becomes True when self.age becomes >= 0

    def kill(self):
        if self.number in self.numbers:
            del VectorSprite.numbers[self.number]  # remove Sprite from numbers dict
        pygame.sprite.Sprite.kill(self)

    def create_image(self):
        if self.picture is not None:
            self.image = self.picture.copy()
        else:
            self.image = pygame.Surface((self.width, self.height))
            self.image.fill((self.color))
        # self.image = self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()
        self.width = self.rect.width
        self.height = self.rect.height

    def rotate(self, by_degree):
        """rotates a sprite and changes it's angle by by_degree"""
        self.angle += by_degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter

    def set_angle(self, degree):
        """rotates a sprite and changes it's angle to degree"""
        self.angle = degree
        oldcenter = self.rect.center
        self.image = pygame.transform.rotate(self.image0, self.angle)
        self.image.convert_alpha()
        self.rect = self.image.get_rect()
        self.rect.center = oldcenter

    def update(self, seconds):
        """calculate movement, position and bouncing on edge"""
        # position and move are pygame.math.Vector2 objects
        # ----- kill because... ------
        # if self.hitpoints <= 0:
        #    self.kill()
        # TODO: pygame.DirtySprite verwenden, mit dirty und visible flag
        if self.age < 0:
            self.visible = False
        else:
            self.visible = True
        if self.max_age is not None and self.age > self.max_age:
            self.kill()
        if self.max_distance is not None and self.distance_traveled > self.max_distance:
            self.kill()
        # ---- movement with/without boss ----
        if self.bossnumber is not None:
            if self.kill_with_boss:
                if self.bossnumber not in VectorSprite.numbers:
                    self.kill()
            if self.sticky_with_boss:
                boss = VectorSprite.numbers[self.bossnumber]
                # self.pos = v.Vec2d(boss.pos.x, boss.pos.y)
                self.pos = pygame.math.Vector2(x=boss.pos.x, y=boss.pos.y)
        if self.age > 0:
            self.pos += self.move * seconds
            self.distance_traveled += self.move.length() * seconds
        self.age += seconds
        if not self.visible:
            self.rect.center = (-200,-200)
        else:
            self.wallbounce()
            self.rect.center = (round(self.pos.x, 0), round(self.pos.y, 0))

    def wallbounce(self):
        # ---- bounce / kill on screen edge ----
        # ------- left edge ----
        if self.pos.x < 0:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.x = 0
                self.move.x *= -1
            elif self.warp_on_edge:
                self.pos.x = Viewer.width
        # -------- upper edge -----
        if self.pos.y < 0:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.y = 0
                self.move.y *= -1
            elif self.warp_on_edge:
                self.pos.y = Viewer.height
        # -------- right edge -----
        if self.pos.x > Viewer.width:
            if self.kill_on_edge:
                self.kill()
            elif self.bounce_on_edge:
                self.pos.x = Viewer.width
                self.move.x *= -1
            elif self.warp_on_edge:
                self.pos.x = 0
        # --------- lower edge ------------
        if self.pos.y > Viewer.height:
            if self.kill_on_edge:
                self.hitpoints = 0
                self.kill()
            elif self.bounce_on_edge:
                self.pos.y = Viewer.height
                self.move.y *= -1
            elif self.warp_on_edge:
                self.pos.y = 0

class PlanetSprite(VectorSprite):

    history = 300 # how many positions are saved to draw tracer lines

    def _overwrite_parameters(self):
        super()._overwrite_parameters()
        self.oldposlist = [self.pos, self.pos]

    def create_image(self):
        self.image = pygame.Surface((2*self.radius,2*self.radius))
        pygame.draw.circle(self.image, self.color, (self.radius,self.radius), self.radius)
        self.image.set_colorkey((0,0,0))
        self.image.convert_alpha()
        self.image0 = self.image.copy()
        self.rect = self.image.get_rect()

    def update(self, seconds):
        super().update(seconds)
        self.oldposlist.append(self.pos)
        if len(self.oldposlist)> self.history:
            self.oldposlist.pop(0)


class Flytext(VectorSprite):
    def __init__(self, text, fontsize=22, acceleration_factor=1.02, max_speed=300, **kwargs):
        """a text flying upward and for a short time and disappearing"""

        VectorSprite.__init__(self, **kwargs)
        ##self._layer = 7  # order of sprite layers (before / behind other sprites)
        ##pygame.sprite.Sprite.__init__(self, self.groups)  # THIS LINE IS IMPORTANT !!
        self.text = text
        self.acceleartion_factor = acceleration_factor
        self.max_speed = max_speed
        self.kill_on_edge = True
        self.image = make_text(self.text, self.color, fontsize)[0]  # font 22
        self.rect = self.image.get_rect()

    def update(self, seconds):
        self.move *= self.acceleartion_factor
        if self.move.length() > self.max_speed:
            self.move.normalize_ip()
            self.move *= self.max_speed
        VectorSprite.update(self, seconds)


class Viewer():
    width = 0  # screen x resolution in pixel
    height = 0  # screen y resolution in pixel
    log_height = 0 # log/gui area below screen
    images = {}
    grid_size = (0,0) # how many pixel lenght has a grid cell x,y
    intervals = (0, 0) # how many cells on screen (x, y)
    zero = [0,0] # origin of coordinate system in pixel x, y


    def __init__(self, game, width=640, height=400, fps=60, ):
        """Initialize pygame, window, background, font,...
           default arguments """
        self.game = game
        self.fps = fps
        Viewer.width = width
        Viewer.height = height
        Viewer.zero = [Viewer.width//2, Viewer.height//2]
        #self.resize_grid((Viewer.width- 6) // 8)
        self.resize_grid(200)

        pygame.init()
        # player center in pixel

        self.screen = pygame.display.set_mode((self.width, self.height), pygame.DOUBLEBUF)
        Viewer.logscreen = pygame.Surface( (Viewer.width, Viewer.height - Viewer.log_height))
        self.clock = pygame.time.Clock()
        self.help = [" -*-*- Welcome to Solar System Simulation -*-*-   ",
                     "press [h] to see this help text again",
                     "move around with Keypad [4],[8],[6],[2] keys",
                     "center on origin with Keypad [5] key",
                     "zoom in with Keypad [+] key or mousewheel",
                     "zoom out with Keypad [-] key or mousewheel",
                     "return to standard zoom with Keypad [ENTER] key",
                     "toggle pause of simulation with [SPACE] key",
                     "toggle drawing mode with [BACKSPACE] key",
                     "change simulation speed with [PageUp] / [PageDown] keys",
                     "change tracer length with [Ins] / [Del] keys",
                     ]
        #"edit planets by editing class Game in the source code",
        # "playing instructions:",

        self.playtime = 0.0
        # ------ surfaces for radar, panel and log ----
        # all surfaces are black by default

        # ------ background images ------
        self.backgroundfilenames = []  # every .jpg or .jpeg file in the folder 'data'
        self.make_background()
        # ------ joysticks ----
        pygame.joystick.init()
        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]
        for j in self.joysticks:
            j.init()
        # ------ create bitmaps for player and dungeon tiles ----
        # print("fontsize dim values")
        # test = make_text("@")

        #self.legend = {}
        # self.load_images()

        self.prepare_spritegroups()
        #self.cursor = CursorSprite(pos=pygame.math.Vector2(x=Viewer.pcx, y=Viewer.pcy))
        self.prepare_sprites()
        self.run()

    def resize_grid(self, lenght):

        Viewer.grid_size = (lenght, lenght)
        Viewer.intervals = ((Viewer.width - 0)/Viewer.grid_size[0],  (Viewer.height - 0) / Viewer.grid_size[1])
        print("grid, intervals, zero", self.grid_size, self.intervals, self.zero)



    def prepare_sprites(self):
        for i, planet in enumerate(Game.objects.values()):
            if i == 0:
                c, r =(255,255,0), 30
            else:
                c, r = (random.randint(50,200), random.randint(50,200), random.randint(50,200)), 15
            PlanetSprite(pos=gridpos_to_pixelvector(planet.position),
                         move=pygame.math.Vector2(0,0), color=c, radius=r, planet=planet)

    def prepare_spritegroups(self):
        self.allgroup = pygame.sprite.LayeredUpdates()  # for drawing
        #self.whole_screen_group = pygame.sprite.Group()
        self.flytextgroup = pygame.sprite.LayeredUpdates()
        #self.cursorgroup = pygame.sprite.Group()
        self.planetgroup = pygame.sprite.Group()
        VectorSprite.groups = self.allgroup
        Flytext.groups =  self.flytextgroup # NOT in allgroup!
        PlanetSprite.groups = self.allgroup, self.planetgroup
        #CursorSprite.groups = self.allgroup


    def make_background(self):
        """scans the subfolder 'data' for .jpg files, randomly selects
        one of those as background image. If no files are found, makes a
        white screen"""
        try:
            for root, dirs, files in os.walk("data"):
                for file in files:
                    if file[-4:].lower() == ".jpg" or file[-5:].lower() == ".jpeg":
                        self.backgroundfilenames.append(os.path.join(root, file))
            random.shuffle(self.backgroundfilenames)  # remix sort order
            self.background = pygame.image.load(self.backgroundfilenames[0])

        except:
            print("no folder 'data' or no jpg files in it")
            self.background = pygame.Surface(self.screen.get_size()).convert()
            self.background.fill((0, 0, 0))  # fill background white

        self.background = pygame.transform.scale(self.background,
                                                 (Viewer.width, Viewer.height-Viewer.log_height))
        self.background.convert()



    def draw_log(self):
        # fill logscreen with color
        if self.log_height > 0:
            self.logscreen.fill((150, 150, 150))
            textsf = make_text("sandwich solar system")[0]

            self.logscreen.blit(textsf, (5, 5))
            # ---- blit logscreen ------
            self.screen.blit(self.logscreen, (0, Viewer.height - self.log_height))

    def draw_grid(self):
        self.background.fill((0, 0, 0))
        c = (0,128,0) # dark green color of grid
        step = self.grid_size[0]
        precision = 0
        axis_string = "{:.0f}"
        if self.grid_size[0] > 350:
            step = self.grid_size[0] / (self.grid_size[0] / 350)
            precision = 3
            axis_string = "{:.3f}"
        elif self.grid_size[0] < 60:
            step = 60
        # right
        c2 = (255,255,255)
        for fx in float_range(Viewer.zero[0], Viewer.width+1, step):
            x = int(round(fx,0))
            pygame.draw.line(self.background, c, (x,0), (x, Viewer.height-Viewer.log_height),1)
            write(self.background, axis_string.format(round(pixel_to_gridvector((x,0))[0],precision)),
                  color=c2, font_size=10, x= x-15, y=5, origin="topright")
        # left
        for fx in float_range(Viewer.zero[0], -1, -step):
            x = int(round(fx, 0))
            pygame.draw.line(self.background, c, (x, 0), (x, Viewer.height - Viewer.log_height), 1)
            write(self.background, axis_string.format(round(pixel_to_gridvector((x, 0))[0],precision)),
                  color=c2, font_size=10, x=x - 15, y= 5, origin="topright")
        # lower
        for fy in float_range(Viewer.zero[1], Viewer.height+1, step):
            y = int(round(fy,0))
            pygame.draw.line(self.background, c, (0,y), (Viewer.width, y),1)
            write(self.background, axis_string.format(round(pixel_to_gridvector((0,y))[1],precision)),
                  color=c2, font_size=10, x= 5, y=y+2, origin="topleft")
        # upper
        for fy in float_range(Viewer.zero[1], -1, -step):
            y = int(round(fy,0))
            pygame.draw.line(self.background, c, (0,y), (Viewer.width, y),1)
            write(self.background, axis_string.format(round(pixel_to_gridvector((0,y))[1],precision)),
                  color=c2, font_size=10, x= 5, y=y+2, origin="topleft")
        # --axis--
        write(self.background, "X-axis --->", color=(255,255,255), font_size=10, x=Viewer.width-5, y=15, origin="topright")
        textsurface = make_text("Y-axis -->", font_color=(255,255,255), font_size=10)[0]
        textsurface = pygame.transform.rotate(textsurface, -90)
        self.background.blit(textsurface, (15, Viewer.height - Viewer.log_height -75))
        # --legend on x-axis
        write(self.background, "{} pixel = {:.8f} AU".format(Viewer.width, Viewer.width / Viewer.grid_size[0]),
                       color=c2, font_size=10,x=Viewer.width, y=Viewer.height , origin="bottomright")
        # blit new background on screen, deleting everything
        self.screen.blit(self.background, (0, 0))  # overwrite everything
        self.dirtyrects = [self.background.get_rect()]
        if not self.draw_lazy:
            for p in self.planetgroup:
                p.oldposlist = [] # kill old tracers

    def display_help(self):
        for i, line in enumerate(self.help):
            Flytext(text=line, pos=pygame.math.Vector2(600, 200 + i * 50), move=pygame.math.Vector2(0, -40),
                    kill_on_edge = True, acceleration_factor=1.00, color=(minmax(255-i*10,10,255),minmax(255-i*10,10,255), 255))

    def run(self):
        """The mainloop"""
        running = True
        pygame.mouse.set_visible(True)
        #oldleft, oldmiddle, oldright = False, False, False
        self.draw_lazy = False
        self.dirtyrects = []
        self.draw_grid()
        self.drag = False # dragging with mouse to pan the starmap
        self.display_help()
        while running:


            milliseconds = self.clock.tick(self.fps)  #
            seconds = milliseconds / 1000

            self.playtime += seconds
            # -----update planet positions-----
            self.game.timestep(seconds)
            # iterate planet sprites
            for p in self.planetgroup:
                p.pos = gridpos_to_pixelvector(p.planet.position)

        # ------ mouse handler ------
            #left, middle, right = pygame.mouse.get_pressed()

            #oldleft, oldmiddle, oldright = left, middle, right

            # ------ joystick handler -------
            # for number, j in enumerate(self.joysticks):
            #    if number == 0:
            #        x = j.get_axis(0)
            #        y = j.get_axis(1)
            #        buttons = j.get_numbuttons()
            #        for b in range(buttons):
            #            pushed = j.get_button(b)

            # ------------ pressed keys (in this moment pressed down)------
            pressed_keys = pygame.key.get_pressed()

            # -------- events ------
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    running = False
                # ---- mouse events ----
                if event.type == pygame.MOUSEBUTTONUP and event.button == 3:
                    self.drag = False
                if event.type == pygame.MOUSEBUTTONDOWN:
                    if event.button == 3:
                        self.drag = True
                    if event.button == 4: # mouse wheel scroll up
                        self.resize_grid(Viewer.grid_size[0] * 1.1) # zoom in
                        self.draw_grid()
                    elif event.button == 5: # mouse wheel scroll down
                        self.resize_grid(Viewer.grid_size[0] * 0.9)  # zoom out
                        self.draw_grid()
                #if event.type == pygame.MOUSEMOTION and self.drag:
                #    # move the map
                #    Viewer.zero[0] += event.pos[0]
                #    Viewer.zero[1] += event.pos[1]
                #    self.draw_grid()

                # ------- pressed and released key ------
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_ESCAPE:
                        running = False
                    if event.key == pygame.K_SPACE:
                        self.game.paused = not self.game.paused
                    if event.key == pygame.K_h:
                        if len(self.flytextgroup) > 0:
                            self.flytextgroup.empty()
                        else:
                            self.display_help()
                    if event.key == pygame.K_PAGEUP:
                        Game.i += 1
                        Game.i = minmax(Game.i, 0, len(Game.deltas)-1)
                        Game.delta_t = Game.deltas[Game.i][0]
                    if event.key == pygame.K_PAGEDOWN:
                        Game.i -= 1
                        Game.i = minmax(Game.i, 0, len(Game.deltas) - 1)
                        Game.delta_t = Game.deltas[Game.i][0]
                    if event.key == pygame.K_BACKSPACE:
                        self.draw_lazy = not self.draw_lazy
                    if event.key == pygame.K_INSERT:
                        PlanetSprite.history += 100
                        PlanetSprite.history = minmax(PlanetSprite.history, 0, 10000)
                    if event.key == pygame.K_DELETE:
                        PlanetSprite.history -= 100
                        PlanetSprite.history = minmax(PlanetSprite.history, 0, 10000)
                        for p in self.planetgroup:
                            p.oldposlist = p.oldposlist[len(p.oldposlist)-PlanetSprite.history:]

                    # ----------- magic with ctrl key and dynamic key -----
                    # if pressed_keys[pygame.K_RCTRL] or pressed_keys[pygame.K_LCTRL]:
                    #if event.mod & pygame.KMOD_CTRL:  # any or both ctrl keys are pressed
                    if event.key == pygame.K_KP_PLUS:
                        self.resize_grid(Viewer.grid_size[0]*1.1)
                        self.draw_grid()
                    if event.key == pygame.K_KP_MINUS:
                        self.resize_grid(Viewer.grid_size[0]*0.9)
                        self.draw_grid()
                    if event.key == pygame.K_KP_ENTER:
                        self.resize_grid(200)
                        self.draw_grid()
                    if event.key == pygame.K_KP5:
                        Viewer.zero = [Viewer.width//2, Viewer.height // 2]
                        self.draw_grid()
                    if event.key == pygame.K_KP4:
                        Viewer.zero[0] += 100 #Viewer.grid_size[0]
                        self.draw_grid()
                    if event.key == pygame.K_KP6:
                        Viewer.zero[0] -= 100 #Viewer.grid_size[0]
                        self.draw_grid()
                    if event.key == pygame.K_KP8:
                        Viewer.zero[1] += 100 #Viewer.grid_size[1]
                        self.draw_grid()
                    if event.key == pygame.K_KP2:
                        Viewer.zero[1] -= 100 #Viewer.grid_size[1]
                        self.draw_grid()


            # ============== draw screen =================
            if self.draw_lazy:
               self.allgroup.clear(self.screen, bgd=self.background)
               self.flytextgroup.clear(self.screen, bgd=self.background)
            else:
               self.screen.blit(self.background, (0,0) ) # overwrite everything
            #self.draw_grid()
            self.allgroup.update(seconds)
            self.flytextgroup.update(seconds)
            self.dirtyrects.extend(self.allgroup.draw(self.screen))
            self.dirtyrects.extend(self.flytextgroup.draw(self.screen))

            for planet in self.planetgroup:
                for i, pos in enumerate(planet.oldposlist):
                    if i < 3:
                        continue
                    x,y = pos
                    x2, y2 = planet.oldposlist[i-1]

                    pygame.draw.line(self.screen, planet.color, (x,y),(x2,y2))

            # write text below sprites

            status = "[h]: help "
            status += "[PgUp/PgDown]: timescale: 1 second = {} ".format(Game.deltas[Game.i][1])
            status += "[BACKSPACE]: {} drawing ".format("lazy" if self.draw_lazy else "clean")
            status += "[INS/DEL]: tracer length: {} ".format(PlanetSprite.history)
            status += "[SPACE]: Simulation {} ".format("paused" if self.game.paused else "running")
            status += "FPS: {:5.3} ".format(self.clock.get_fps())
            textsurface, pos = make_text(status, font_color=(255,255,255),font_size=12, bold=True)
            pygame.draw.rect(self.screen, (0, 0, 0), (5, Viewer.height- pos[1], pos[0], pos[1]))
            self.screen.blit(textsurface, (5, Viewer.height - pos[1]))

            self.dirtyrects.append(  pygame.Rect(5, Viewer.height-pos[1], pos[0], pos[1]))
            if self.draw_lazy:
                pygame.display.update(self.dirtyrects)
                self.dirtyrects = []
            else:
                pygame.display.flip()
        # -----------------------------------------------------
        pygame.mouse.set_visible(True)
        pygame.quit()


if __name__ == '__main__':
    g = Game()
    Viewer(g, width=1200, height=800, )  # , (35,35))
