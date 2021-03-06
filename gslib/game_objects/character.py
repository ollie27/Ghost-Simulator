from __future__ import absolute_import, division, print_function

import io
import random
import os.path
import json

from gslib.engine import textures, text, sprite, primitives
from gslib.game_objects.game_object import GameObject
from gslib.constants import *
from gslib.character_functions import ai_functions
from pyglet import image


WHITE = (255, 255, 255, 255)
GREY = (60, 60, 60, 255)


def load_stats(fname):
    with io.open(os.path.join(CHARACTERS_DIR, fname), 'rt', encoding='utf-8') as f:
        age = f.readline().strip()
        age = int(age)

        bio = u''
        fears = []
        start_bio = False
        for l in f:
            if l.strip() == '#':
                start_bio = True
            else:
                if start_bio:
                    bio += l
                else:
                    fears.append(l.strip())

    print(fears)
    return age, bio, fears


def gen_character(stats=None):
    """Generate a character based on the stats dictionary.

    Any missing parameters in the dictionary are generated randomly.

      - age: integer
      - bio: string
      - fears: list of strings
      - name: string
      - gender: 'm' or 'f'
    """
    if stats is None:
        stats = {}
    stats.setdefault('age', random.randrange(151))
    stats.setdefault('bio', gen_bio())
    stats.setdefault('fears', gen_fears())
    stats.setdefault('scared_of', gen_fears())
    stats.setdefault('gender', random.choice(('m', 'f')))
    stats.setdefault('name', gen_name(stats['gender']))
    stats.setdefault('image_name', os.path.join(CHARACTERS_DIR, 'Sprite_front.png'))
    return stats


def choose_n_lines(n, fname):
    res = []
    with io.open(fname, 'rt', encoding='utf-8') as f:
        lines = f.readlines()
        for i in range(n):
            ix = random.randrange(len(lines))
            res.append(lines.pop(ix).strip())
    return res


def gen_bio():
    return u' '.join(choose_n_lines(3, os.path.join(DATA_DIR, "bio.txt")))


def gen_fears():
    f = choose_n_lines(random.randrange(1, 4), os.path.join(DATA_DIR, "fear_description.txt"))
    fears = []
    for i in f:
        name = i[:i.find(':')]
        fears.append(name)
    return fears

def gen_name(gender):
    fname = os.path.join(DATA_DIR, "first_names_{}.txt".format(gender))

    first_name = choose_n_lines(1, fname)[0]
    second_name = choose_n_lines(1, os.path.join(DATA_DIR, "second_names.txt"))[0]

    while random.random() > 0.9:
        second_name = u"{}-{}".format(second_name, choose_n_lines(1, os.path.join(DATA_DIR, "second_names.txt"))[0])

    return u"{} {}".format(first_name, second_name)


def draw_info_sheet(stats):
    if not stats:
        return None
    font_size = 20
    #dim = w, h = (GAME_WIDTH - LEVEL_WIDTH, int((GAME_WIDTH - LEVEL_WIDTH) / 1.6))

    x = 0
    y = 0

    sprites = []

    h = 200.0
    w = h / 1.6
    dim = (w, h)

    border = 8
    #fill_background(surf, border) # TODO PYGLET

    # draw character image
    im = textures.get(stats['image_name'])
    im_sprite = sprite.Sprite(im)
    im_sprite.scale_x = w / im_sprite.width
    im_sprite.scale_y = h / im_sprite.height


    # draw name/age and text boxes
    name_text = text.new('comic sans', font_size, u'Name: ' + stats['name'])
    age_text = text.new('comic sans', font_size, u'Age: ' + str(stats['age']))


    # age_text.x = name_text.x
    # age_text.y = name_text.y - name_text.content_height

    # draw background
    background_sprite = primitives.RectPrimitive(width=w + name_text.content_width + border * 2,
                                                 height=h + 2 * border,  # - name_text.content_height - age_text.content_height - 3 * border
                                                 color=GREY)

    sprites.append(background_sprite)
    sprites.append(im_sprite)
    sprites.append(name_text)
    sprites.append(age_text)

    return sprites


#@save_this(self)
def save_this(obj):
    def g(func):
        obj._to_save.add(func.func_name)
        def f(*args, **kwargs):
            func(*args, **kwargs)
        return f
    return g


# class Character_old(GameObject):
#     def __init__(self, game_class, x, y, w, h, stats=None, **kwargs):
#         """
#         Characters have various functions to determine their behaviour when things happen.
#         self.feared_function - when the character is scared
#         self.possessed_function - occurs when the character becomes possessed
#         self.unpossessed_function - occurs when the character becomes unpossessed
#         self.harvested_function - when the character has had its fear harvested (ooga booga'd)
#
#         Make these functions in character_functions
#          - Function should take in any parameters and return a function.
#         """
#         super(Character_old, self).__init__(game_class, x, y, w, h, **kwargs)
#         if stats:
#             for f in stats['fears']:
#                 self.fears.append(f)
#             for f in stats['scared_of']:
#                 self.scared_of.append(f)
#             # self.scared_of.append(u'player')
#
#         self.stats = stats
#         self.info_sheet = draw_info_sheet(self.stats)
#
#         self.feared_function = []
#         self.possessed_function = []
#         self.unpossessed_function = []
#         self.harvested_function = []
#         # self.idle_functions = [AI_functions.all_functions_dict['idle_functions']['StandStill'](self)]
#         self.fainted = False
#         self.feared_by_obj = None
#         self.feared_from_pos = (0, 0)
#
#         self.patrol_path = []
#         self.patrol_index = 0
#
#         self.possessed_by = []
#
#         self.held_props = []
#
#         # TODO make easy way to add desired variables to this, perhaps using the decorator above this class and setter's?
#         self._to_save = {'feared_function', 'possessed_function', 'unpossessed_function', 'harvested_function',
#                          'has_touched_function', 'is_touched_function', 'has_untouched_function', 'is_untouched_function',
#                          'stats', 'fears', 'scared_of', 'feared_speed', 'normal_speed',
#                          'states', 'coord', 'collision_weight', 'idle_functions', 'patrol_path', 'patrol_index'}
#
#     def get_stats(self, name):
#         name = name
#         image = 'characters/torch.png' # os.path.join(CHARACTERS_DIR, name) + '_front.png'
#         age, bio, self.fears = load_stats(name)
#         return {'name': name, 'age': age, 'image_name': image, 'bio': bio}
#
#     def update(self, dt):
#
#         if not self.cutscene_controlling:
#             if not self.possessed_by:
#                 self.update_timer += 1
#                 #pick random direction (currently only one of 8 directions, but at a random speed)
#
#                 if self.update_timer >= 50 and not self.fear_timer:
#                     self.update_timer = 0
#
#                     self.move_down = False
#                     self.move_up = False
#                     self.move_left = False
#                     self.move_right = False
#
#                     for i in self.idle_functions:
#                         i()
#
#                 if self.fear_timer:
#                     for f in self.feared_function:
#                         f()
#                     self.fear_timer -= 1
#
#             else:
#                 # self.possessed_function(self)
#                 self.current_speed = self.normal_speed
#                 # tie move to possessing player move
#                 self.move_down = self.possessed_by[-1].move_down  # last player to possess get control
#                 self.move_up = self.possessed_by[-1].move_up
#                 self.move_left = self.possessed_by[-1].move_left
#                 self.move_right = self.possessed_by[-1].move_right
#
#         GameObject.update(self, dt)
#
#
#     def create_save_dict(self):
#         to_save = self._to_save
#
#         save_dict = {}
#         for s in to_save:
#             o = getattr(self, s)
#             if isinstance(o, list):
#                 if o:
#                     if hasattr(o[0], '__call__'): # check if function
#                         t_list = [f.__name__ for f in o]
#                         save_dict[s] = json.dumps(t_list)
#                         continue
#
#             if s == u'fears':
#                 o = list(o)
#             save_dict[s] = json.dumps(o)
#
#         save_dict[u'object_type'] = self.__class__.__name__
#         return save_dict
#
#     def activate(self):
#         pass


class Character(GameObject):
    def __init__(self, game_class, x, y, w=32, h=32, stats=None, **kwargs):
        """
        Characters have various functions to determine their behaviour when things happen.
        self.feared_function - when the character is scared
        self.possessed_function - occurs when the character becomes possessed
        self.unpossessed_function - occurs when the character becomes unpossessed
        self.harvested_function - when the character has had its fear harvested (ooga booga'd)

        Make these functions in character_functions
         - Function should take in any parameters and return a function.
        """
        super(Character, self).__init__(game_class, x, y, w, h, **kwargs)
        if stats:
            for f in stats['fears']:
                self.fears.append(f)
            for f in stats['scared_of']:
                self.scared_of.append(f)

        self.stats = stats
        self.info_sheet = None # draw_info_sheet(self.stats)

        self.feared_function = []
        self.possessed_function = []
        self.unpossessed_function = []
        self.harvested_function = []
        self.idle_functions = []
        # self.idle_functions = [AI_functions.all_functions_dict['idle_functions']['StandStill'](self)]

        self.feared_by_obj = None
        self.feared_from_pos = (0, 0)

        self._held_by = None
        self._collision_weight = self.collision_weight
        self.held_offset = (8, 0) # offset from centre when held
        self.held_objects = [] # should not be edited directly - use .held_by on target object


        self.possessed_by = []


        # TODO make easy way to add desired variables to this, perhaps using the decorator above this class and setter's?
        self._to_save = {'feared_function', 'possessed_function', 'unpossessed_function', 'harvested_function',
                         'has_touched_function', 'is_touched_function', 'has_untouched_function', 'is_untouched_function',
                         'stats', 'fears', 'scared_of', 'feared_speed', 'normal_speed',
                         'states', 'coord', 'collision_weight', 'idle_functions', 'sprite_sheet_name', 'dimensions',
                         'sprite_width', 'sprite_height', 'can_be_picked_up', 'can_pick_up'}

        self.possessor_gets_motion_control = True
        self.possessable = True
        self.can_pick_up = True
        self.can_be_picked_up = False
        self.can_scare = True
        self.can_be_scared = True
        self.has_stats = True # age, bio, etc
        self.can_walk = True
        self.has_special_properties = False # such as "fire" or "wet"
        self.has_special_render_properties = False
        self.has_ai = True

        # self.has_touched_function.append(AI_functions.all_functions_dict['has_touched_functions']['PickUp'](self))

    @property
    def collision_weight(self):
        if self._held_by is None:
            return self._collision_weight
        else:
            return 0

    @collision_weight.setter
    def collision_weight(self, val):
        self._collision_weight = val

    @property
    def held_by(self):
        return self._held_by

    @held_by.setter
    def held_by(self, obj):
        if not self.can_be_picked_up or not obj.can_pick_up:
            return

        if obj is None:
            self._held_by = None
            return

        self._held_by = obj
        obj.held_objects.append(self)


    def update(self, dt):
        if not self.cutscene_controlling:
            if self.possessed_by:
                self.update_while_possessed(dt)
            else:
                self.update_idle_or_feared(dt)

        if not self.can_walk or self.held_by: # check this after, things other than walking may occur in above functions
            self.move_down = False
            self.move_up = False
            self.move_left = False
            self.move_right = False

        GameObject.update(self, dt)

        for o in self.held_objects:
            o.coord = self.coord[0] + self.held_offset[0], self.coord[1] + self.held_offset[1]

    def update_idle_or_feared(self, dt):
        self.update_timer += 1

        if self.fear_timer and len(self.feared_function): # do feared functions while scared

            self.move_down = False
            self.move_up = False
            self.move_left = False
            self.move_right = False

            for f in self.feared_function:
                f.function(None)
            self.fear_timer -= 1

        elif self.update_timer >= 50: # otherwise do idle functions
            self.update_timer = 0

            self.move_down = False
            self.move_up = False
            self.move_left = False
            self.move_right = False

            for i in self.idle_functions:
                i.function(None)

    def update_while_possessed(self, dt):
        if self.possessor_gets_motion_control:
            self.current_speed = self.normal_speed
            # tie move to possessing player move
            self.move_down = self.possessed_by[-1].move_down  # last player to possess get control
            self.move_up = self.possessed_by[-1].move_up
            self.move_left = self.possessed_by[-1].move_left
            self.move_right = self.possessed_by[-1].move_right
        else:
            self.update_idle_or_feared(dt)

    def activate(self):
        pass

    def create_save_dict(self):
        to_save = self._to_save

        save_dict = {}
        for s in to_save:
            o = getattr(self, s)
            if isinstance(o, list):
                if o and 'function' in s: # check not empty, and is list of functions
                    t_list = []
                    for f in o:
                        if not 'PerfTriggerActions' in f.__class__.__name__: # this makes sure we don't save the functions create from triggers
                            t_list.append(f.save_to_dict())
                    save_dict[s] = json.dumps(t_list)
                    continue

            if s == u'fears':
                o = list(o)
            save_dict[s] = json.dumps(o)

        save_dict[u'object_type'] = self.__class__.__name__
        return save_dict

    def load_from_dict(self, d):
        for k, v in d.iteritems():
            if '_function' in k:
                func_list = json.loads(v)
                for module_name, function_name, function_dict in func_list:
                    func = ai_functions.load_function(self, module_name, function_name, function_dict)
                    attr = getattr(self, func.function_type) # get the function list for this character
                    attr.append(func)

            elif k != u'object_type':
                if k == u'fears':
                    fears = json.loads(v)
                    self.fears.extend(fears)
                elif k == u'sprite_sheet_name':
                    setattr(self, 'sprite_sheet', image.load(os.path.join(CHARACTERS_DIR, json.loads(v))))
                setattr(self, k, json.loads(v))

        self._create_animations()
        self._update_animation()


if __name__ == "__main__":
    pass
