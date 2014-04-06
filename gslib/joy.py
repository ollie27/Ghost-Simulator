import pygame

from gslib import character
from gslib.constants import *

class JoyController(object):
    def __init__(self, game):
        self.game = game

        if not pygame.joystick.get_init():
            pygame.joystick.init()

        self.joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]

        if len(self.joysticks) == 0:
            pygame.joystick.quit()
        else:
            for joystick in self.joysticks:
                joystick.init()

    def handle_hat(self, event):
        x, y = event.value
        if x == -1:
            self.game.keys[pygame.K_LEFT] = True
        elif x == 1:
            self.game.keys[pygame.K_RIGHT] = True
        elif x == 0:
            self.game.keys[pygame.K_LEFT] = False
            self.game.keys[pygame.K_RIGHT] = False
        if y == -1:
            self.game.keys[pygame.K_DOWN] = True
        elif y == 1:
            self.game.keys[pygame.K_UP] = True
        elif y == 0:
            self.game.keys[pygame.K_DOWN] = False
            self.game.keys[pygame.K_UP] = False

    def handle_buttondown(self, event):
        if event.button == 0:
            self.game.objects.append(character.Character(self.game, self.game.player1.coord[0], self.game.player1.coord[1], 16, 16,
                                                         character.gen_character()))
        elif event.button == 1:
            if self.game.GameState == MAIN_MENU:
                self.game.GameState = MAIN_GAME
            elif self.game.GameState == MAIN_GAME:
                self.game.GameState = MAIN_MENU
        elif event.button == 2:
            self.game.options['FOV'] = not self.game.options['FOV']
        elif event.button == 3:
            self.game.options['VOF'] = not self.game.options['VOF']

    def handle_buttonup(self, event):
        pass

    def handle_axis(self, event):
        pass

    def handle_ball(self, event):
        pass

