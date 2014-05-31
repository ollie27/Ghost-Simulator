__author__ = 'Martin'

from gslib.ui import button, drop_down_list
from gslib.editor import controls, controls_basic
from gslib.constants import *
from gslib.game_objects import character
from gslib.ui import msg_box
from gslib import window

import io
import os.path

def get_fears_from_file():  # load all possible fears from file, without descriptions
    possible_fears = []
    with io.open(os.path.join(DATA_DIR, "fear_description.txt"), 'rt', encoding='utf-8') as f:
        for l in f:
            fear = l[:l.find(':')]
            if not fear in possible_fears:
                possible_fears.append(fear)
    return possible_fears


class BasicEditor(object):
    def __init__(self, game, toggle_button_text, pos=(0, 0), toggle_pos=(0, 0), toggle_order=None):
        """
        Set .pre = unique identifying sting to prevent name conflicts when combined into update list in .game

        Toggle button for the editor appears at toggle_pos.
        If toggle_order != None, then overrides toggle_pos. Then toggle button for this editor is aligned to the grid of owning editor.

        Append editors that stem from this editor in self.sub_editors.
            - sub_editors_pos is top-left of where it will appear when enabled

        Positions of buttons/lists are done on a grid basis, set with order=(y, x) in declaration.
             - top left of grid is self.pos
             - button size and spacing set with .size, .vert_spacing, .horizontal_spacing
        """
        self.game = game
        self.pre = '' # button/list name prefix - prevents name conflicts when combined into update list in .game

        self.toggle_button_text = toggle_button_text
        self.toggle_button_name = self.toggle_button_text.lower()
        self.toggle_button_name = self.toggle_button_name.replace(' ', '_')
        self.toggle_button_name = 'toggle_' + self.toggle_button_name

        self.buttons = {}
        self.drop_lists = {}

        self.sub_editors = []
        self.sub_editors_pos = (0, 0)

        self.enabled = False

        self.size = (120, 20)
        self.vert_spacing = 5
        self.horizontal_spacing = 5

        self._pos = (0, 0)
        self.toggle_pos = toggle_pos
        self.toggle_order = toggle_order
        self.buttons[self.toggle_button_name] = button.DefaultButton(self, self.toggle_self, text=toggle_button_text, pos=toggle_pos)

        self.pos = pos

    @property
    def pos(self):
        return self._pos

    @pos.setter
    def pos(self, p):
        self._pos = p
        self.update_element_positions()

    def update_element_positions(self):
        self.buttons[self.toggle_button_name].pos = self.toggle_pos

        size = self.size
        vert_spacing = self.vert_spacing
        horizontal_spacing = self.horizontal_spacing
        p1 = self.pos[1] - size[1] # pos of Editor is then top-left of first button
        for n, b in self.buttons.iteritems():
            if n == self.toggle_button_name:
                continue
            pos = (self.pos[0] + b.order[1] * (size[0] + horizontal_spacing), p1 - b.order[0] * (size[1] + vert_spacing))
            b.pos = pos
            b.size = size


        for b in self.drop_lists.itervalues():
            pos = (self.pos[0] + b.order[1] * (size[0] + horizontal_spacing), p1 - b.order[0] * (size[1] + vert_spacing))
            b.pos = pos
            b.size = size


        for e in self.sub_editors:
            if not e.toggle_order is None: # set toggle button position of sub-editor in grid of owning editor
                pos = (self.pos[0] + e.toggle_order[1] * (size[0] + horizontal_spacing), p1 - e.toggle_order[0] * (size[1] + vert_spacing))
                e.toggle_pos = pos

            e.pos = self.sub_editors_pos
            e.update_element_positions()


        self.toggle_self(self.enabled)

    def toggle_self(self, value=None):
        if value is None:
            self.enabled = not self.enabled
        else:
            self.enabled = value
        for k, v in self.buttons.iteritems():
            if not k == self.toggle_button_name:
                v.visible = self.enabled
                v.enabled = self.enabled

        for v in self.drop_lists.itervalues():
            v.visible = self.enabled
            v.enabled = self.enabled

        self.buttons[self.toggle_button_name].flip_color_rg(self.enabled)

        for t in self.sub_editors:
            t.toggle_self(value)


    def create_elements(self): # placeholder for auto-complete
        pass


    def get_buttons(self):
        edit_buttons_prefixed = {}
        for k, v in self.buttons.iteritems():
            edit_buttons_prefixed[self.pre + k] = v

        for t in self.sub_editors:
            edit_buttons_prefixed = dict(edit_buttons_prefixed, **t.get_buttons())

        return edit_buttons_prefixed


    def get_lists(self):
        edit_lists_prefixed = {}
        for k, v in self.drop_lists.iteritems():
            edit_lists_prefixed[self.pre + k] = v

        for t in self.sub_editors:
            edit_lists_prefixed = dict(edit_lists_prefixed, **t.get_lists())

        return edit_lists_prefixed


class CharacterTemplateEditor(BasicEditor):
    """
    Sub-editors are re-created when a new template is created.
    """
    def __init__(self, game):
        super(CharacterTemplateEditor, self).__init__(game, 'Character Editor', (0, window.height - 160), (0, window.height - 60))

        self.pre = 'cte_'

        self.char_to_edit = None
        self.char_template_name = 'Default'
        self.char_state_to_edit = None

        self.sub_editors_pos = (300, window.height - 100)

        self.create_elements()

    def create_elements(self): # main buttons that are not character template-dependent
        bu = button.DefaultButton
        dl = drop_down_list.DropDownList

        self.buttons['new_character'] = bu(self, self.new_character_template, text='New Character Template', order=(-2, 0))

        self.update_element_positions()

    def create_character_elements(self): # re-create for new character
        bu = button.DefaultButton
        dl = drop_down_list.DropDownList

        if self.char_to_edit is None:
            return

        self.buttons['generic_properties_label'] = bu(self, None, text='Generic Properties', order=(-1, 0))
        self.buttons['generic_properties_toggle_label'] = bu(self, None, text='Detailed Editors', order=(-1, 1))

        def bool_flip(p):
            def func():
                new_p = not getattr(self.char_to_edit, p)
                setattr(self.char_to_edit, p, new_p)
                self.buttons[p].flip_color_rg(new_p) # set button colour to reflect true/false
            return func

        bool_properties = ['possessor_gets_motion_control', 'possessable', 'can_pick_up', 'can_be_picked_up',
                           'can_scare', 'can_be_scared', 'has_stats', 'can_walk', 'has_special_properties',
                           'has_ai', 'has_special_render_properties']

        sub_editors_creators = {'can_scare': self.create_can_scare_elements,
                                'can_be_scared': self.create_can_be_scared_elements,
                                'has_stats': self.create_has_stats_elements,
                                'can_walk': self.create_can_walk_elements,
                                'has_special_properties': self.create_has_special_properties_elements,
                                'has_special_render_properties': self.create_has_special_render_properties_elements,
                                'has_ai': self.create_has_ai_elements}

        for i, p in enumerate(bool_properties):
            str_p = p.replace('_', ' ')
            str_p = str_p.title()
            self.buttons[p] = bu(self, bool_flip(p), text=str_p, order=(i, 0)) # bool toggle of generic character abilities
            self.buttons[p].flip_color_rg(getattr(self.char_to_edit, p)) # set button colour to reflect true/false

            if p in sub_editors_creators.keys():
                sub_editors_creators[p]((i, 1))


        self.buttons['rename_character'] = bu(self, self.rename_character_template, text='Rename: Default', order=(i + 2, 0))


        self.update_element_positions()


    def create_can_scare_elements(self, toggle_order):
        # selection of what this char scares
        self.sub_editors.append(ScaresEditor(self.game, self.char_to_edit, pos=self.sub_editors_pos, toggle_order=toggle_order))

    def create_can_be_scared_elements(self, toggle_order):
        pass # selection of what this char is scared of

    def create_has_stats_elements(self, toggle_order):
        pass # bio, age, etc.

    def create_can_walk_elements(self, toggle_order):
        pass # show walk speed editors

    def create_has_special_properties_elements(self, toggle_order):
        pass # choice of "fire", "wet", etc. Text attributes to base conditional triggers off.

    def create_has_special_render_properties_elements(self, toggle_order):
        pass # trails, etc

    def create_has_ai_elements(self, toggle_order):
        pass # char function editor




    def new_character_template(self):
        self.char_to_edit = character.Character(self.game, 0, 0, 32, 32)
        self.sub_editors = []
        self.create_character_elements()

    def save_character_template(self):
        pass

    def load_character_template(self):
        pass

    def rename_character_template(self):
        def new_name(name):
            self.char_template_name = name
            self.buttons['rename_character'].text = 'Rename: ' + name

        msg_box.InputBox(self.game, 'Enter template name:', '', new_name).show()


    def add_character_state(self):
        def new_state(name):
            if name in self.char_to_edit.states.keys():
                msg_box.InfoBox(self.game, 'State name conflict').show()
            else:
                self.char_to_edit.states[name] = {}
                self.char_state_to_edit = name

        msg_box.InputBox(self.game, 'Enter new state name.', '', new_state).show()

    def select_character_state(self):
        pass

    def delete_character_state(self):
        pass


class ScaresEditor(BasicEditor):
    def __init__(self, game, char, pos, toggle_pos=(0, 0), toggle_order=None):
        super(ScaresEditor, self).__init__(game, 'Scares Editor', pos=pos, toggle_pos=toggle_pos, toggle_order=toggle_order)

        self.pre = 'scares_'
        self.character = char

        self.possible_fears = get_fears_from_file()
        self.possible_fears.append(u'player')

        self.create_elements()


    def create_elements(self):
        bu = button.DefaultButton
        dl = drop_down_list.DropDownList

        self.buttons['main_label'] = bu(self, None, text='Scares Editor', order=(0, 0))

        self.update_element_positions()