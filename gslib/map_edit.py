import pygame
from gslib import drop_down_list
from gslib import button
from gslib import character_objects
from gslib import game_object
from gslib import graphics
from gslib import triggers
from gslib.constants import *


def none():
    pass


class Cursor(game_object.GameObject):
    def __init__(self, game, surface):
        game_object.GameObject.__init__(self, game, 0, 0, 0, 0, surface)
        self.frame_rect = pygame.Rect((0, 0), surface.get_size())
        self.max_frames = 0
        self.sprite_height = surface.get_height()
        self.sprite_width = surface.get_width()
        self.current_speed = 0
        self.normal_speed = 0

        self.update = none




class Editor(object):
    def __init__(self, game, pos=(0, 0)):
        self.game = game
        self.pos = pos

        self.buttons = {}
        self.drop_lists = {}

        ###################################################################
        # Place new object
        ###################################################################

        self.possible_characters = {'Small Door': character_objects.SmallDoor,
                                    'Dude': character_objects.Dude}

        self.buttons['pick_object_label'] = button.DefaultButton(self, None, pos=(100, 0), text="Place Object")
        self.drop_lists['pick_object'] = drop_down_list.DropDownList(self, self.possible_characters,
                                                                     self.update_object_prototype, pos=(200, 0))
        self.object_prototype = None

        ###################################################################
        # View existing Trigger
        ###################################################################

        self.buttons['view_triggers_label'] = button.DefaultButton(self, None, pos=(320, 0), size=(120, 20),
                                                                   text="Current Triggers")
        self.drop_lists['view_triggers'] = drop_down_list.DropDownList(self, self.game.map.triggers,
                                                                       self.display_trigger, pos=(440, 0),
                                                                       labels='classname', size=(300, 20))
        self.trigger_display_colours = ((120, 0, 0), (0, 120, 0), (0, 0, 120), (120, 120, 0), (120, 0, 120), (0, 120, 120), (120, 120, 120))
        self.trigger_display_circles = []
        self.trigger_display_text = []

        ###################################################################
        # Create new Trigger
        ###################################################################

        self.possible_triggers = {0: triggers.FlipStateOnHarvest,
                                  1: triggers.FlipStateWhenTouchedConditional,
                                  2: triggers.FlipStateWhenUnTouchedConditional}
        self.buttons['new_trigger_label'] = button.DefaultButton(self, None, pos=(100, 20), size=(100, 20),
                                                                 text="New trigger")
        self.drop_lists['new_triggers'] = drop_down_list.DropDownList(self, self.game.map.triggers,
                                                                      self.new_trigger, pos=(200, 20),
                                                                      labels='classname', size=(300, 20))
        # self.new_trigger_objects = []
        self.trigger_prototype = None

    def update_object_prototype(self):
        if self.drop_lists['pick_object'].selected:
            self.object_prototype = self.drop_lists['pick_object'].selected(self.game)
            self.object_prototype.current_speed = 0
            self.object_prototype.normal_speed = 0
            #set everything to None when i can be bothered
        else:
            self.object_prototype = None
        self.game.cursor = self.object_prototype
        self.game.gather_buttons_and_drop_lists_and_objects()

    def draw_trigger(self, t):
        self.trigger_display_circles = []
        self.trigger_display_text = []
        # t = self.drop_lists['view_triggers'].selected
        if t:
            font = pygame.font.SysFont(FONT, 20)
            for i, o in enumerate(t.objects):
                circ = graphics.draw_circle(25, self.trigger_display_colours[i], 2)
                text = font.render(t.legend[i], True, (255, 255, 255))
                self.trigger_display_circles.append((circ, o))
                self.trigger_display_text.append((text, o))

    def display_trigger(self):
        self.draw_trigger(self.drop_lists['view_triggers'].selected)

    def create_trigger_cursor(self, tex):
        font = pygame.font.SysFont(FONT, 20)
        text = font.render(tex, True, (255, 255, 255))
        w = text.get_width()
        h = text.get_height()

        surf = pygame.Surface((w, h))
        surf.fill((255, 0, 255))
        surf.blit(text, (w/2 - text.get_width()/2, 0))
        self.game.cursor = Cursor(self.game, surf)
        self.game.gather_buttons_and_drop_lists_and_objects()

    def new_trigger(self):
        if self.drop_lists['new_triggers'].selected:
            self.trigger_prototype = triggers.Trigger(None, [])  # self.drop_lists['new_triggers'].selected
            self.trigger_prototype.legend = self.drop_lists['new_triggers'].selected.legend
            self.game.new_trigger_capture = True
            self.create_trigger_cursor(self.trigger_prototype.legend[0])

    def update_new_trigger(self, o):
        t = self.trigger_prototype
        l = t.objects
        if o in l:
            l.remove(o)
        else:
            l.append(o)

        target_number = len(self.drop_lists['new_triggers'].selected.legend)
        if len(l) == target_number:
            name = 0
            for n in self.game.map.triggers.keys():
                if isinstance(n, int):
                    if n >= name:
                        name = n + 1
            self.game.map.triggers[name] = type(self.drop_lists['new_triggers'].selected)(tuple(l))
            self.draw_trigger(None)
            self.game.cursor = None
            self.game.gather_buttons_and_drop_lists_and_objects()
        else:
            self.create_trigger_cursor(self.trigger_prototype.legend[len(l)])

            self.draw_trigger(t)


