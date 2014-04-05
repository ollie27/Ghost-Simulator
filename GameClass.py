import pygame
import PlayerClass
from Constants import *
import Menus

blackColour = pygame.Color(0, 0, 0)
blueColour = pygame.Color(0, 0, 255)

class Game:
    def __init__(self, width, height):
        self.Menu = Menus.MainMenu(self)
        self.GameState = MAIN_MENU
        self.gameRunning = True
        self.dimensions = (width, height)
        self.surface = pygame.display.set_mode(self.dimensions)

        self.clock = pygame.time.Clock()
        self.msPassed = 0

        self.player1 = PlayerClass.Player(100,100,40,40)

        self.keys = { pygame.K_DOWN: False, pygame.K_UP: False, pygame.K_LEFT: False, pygame.K_RIGHT: False }

        self.event_map = {
            pygame.KEYDOWN: self.handle_keys,
            pygame.KEYUP: self.handle_keys,
            pygame.QUIT: self.quit_game,
            pygame.MOUSEBUTTONDOWN: self.mouse_click,
        }

    def gameLoop(self):
        while self.gameRunning:
            if self.GameState == STARTUP:
                pass
            elif self.GameState == MAIN_MENU:
                self.Menu.display()
            elif self.GameState == MAIN_GAME:
                self.clock.tick()
                self.msPassed += self.clock.get_time()

            # poll event queue
            for event in pygame.event.get():
                response = self.event_map.get(event.type)
                if response is not None:
                    response(event)

            if self.msPassed > 30:
                self.update()
                self.msPassed = 0

            self.draw()


    def update(self):
        # this is fixed timestep, 30 FPS. if game runs slower, we lag.
        # PHYSICS & COLLISION MUST BE DONE WITH FIXED TIMESTEP.
        self.player1.update(self)

    def draw(self):
        # this runs faster than game update. animation can be done here with no problems.
        self.surface.fill(blackColour)
        temp_surf = pygame.Surface((40, 40))

        pygame.draw.circle(temp_surf, blueColour, (20, 20), 20, 0)
        self.surface.blit(temp_surf, self.player1.coord)

        # now double!
        pygame.display.update()

    def handle_keys(self, event):

        if event.type == pygame.KEYDOWN:
            if event.key in self.keys:
                self.keys[event.key] = True
        if event.type == pygame.KEYUP:
            if event.key in self.keys:
                self.keys[event.key] = False

    def mouse_click(self, event):
        if self.GameState == MAIN_MENU:
            self.Menu.mouse_event(event)


    def quit_game(self, _):
        self.gameRunning = False