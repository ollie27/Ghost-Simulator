from __future__ import absolute_import, division, print_function

import os.path

import pyglet

from gslib.constants import *
from gslib.engine import textures, text, sprite, primitives, rect, camera
from gslib.game_objects.player import Player
from gslib import options, window
from gslib.ui import drop_down_list


circle_tex = None
def draw_circle(r, color):
    global circle_tex
    if circle_tex is None:
        circle_tex = textures.get(os.path.join(SPRITES_DIR, 'circle_solid.png'))
    sprit = sprite.Sprite(circle_tex)
    sprit.scale_x = 2 * r / 1024
    sprit.scale_y = 2 * r / 1024
    sprit.color_rgba = color + (120,)
    return sprit


class Graphics(object):
    """
    see Game class for how to add things to be drawn.
    """
    def __init__(self, game):
        self.game = game

        self.field = sprite.Sprite(pyglet.image.load(os.path.join(SPRITES_DIR, 'field.png')).get_texture())
        self.field.opacity = options['VOF_opacity']
        self.field.scale_x = window.width / self.field.image.width
        self.field.scale_y = window.height / self.field.image.height

        self.light = sprite.Sprite(pyglet.image.load(os.path.join(SPRITES_DIR, 'light.png')).get_texture())
        self.light.scale_x = self.light.scale_y = 200 / self.light.image.height
        self.light_size = (self.light.width, self.light.height)

        self.fear_text = text.new(FONT, 20, u'FEAR')

        self.map_texture = {}
        self.tile_sprite = {}

        self.camera_group = camera.CameraGroup(self.game.camera)

        options.push_handlers(self)
        window.push_handlers(self)
        self.game.push_handlers(self)

    def on_option_change(self, key, value):
        if key == 'VOF_opacity':
            self.field.opacity = value

    def on_resize(self, width, height):
        self.field.scale_x = width / self.field.image.width
        self.field.scale_y = height / self.field.image.height

    def on_map_change(self, m):
        self._draw_map(m)

    def main_game_draw(self):

        window.clear()

        self.draw_map_early()
        self.draw_objects()
        self.draw_map_late()
        if options['torch']:
            self.draw_torch()

        self.draw_buttons()
        if self.game.state == EDITOR:
            self.draw_editor()

        self.draw_fear_bar()
        self.draw_character_stats()

        if self.game.show_fears:
            self.say_fears()
        if self.game.show_ranges:
            self.show_fear_ranges()

        if self.game.dialogue is not None:
            self.game.dialogue.draw()

        if self.game.message_box is not None:
            self.game.screen_objects_to_draw.append(self.game.message_box)

        if options['FOV']:
            self.draw_world_objects()
            self.draw_screen_objects()
        else:
            self.game.world_objects_to_draw = []
            self.game.screen_objects_to_draw = []

    def _draw_map(self, m):
        grid_size = TILE_SIZE

        self.map_texture = {}
        self.tile_sprite = {}

        for layer_name, layer in m.grid.iteritems():
            self.map_texture[layer_name] = pyglet.image.Texture.create(grid_size * m.grid_width, grid_size * m.grid_height,
                                                                       mag_filter=pyglet.gl.GL_NEAREST)
            self.tile_sprite[layer_name] = sprite.Sprite(self.map_texture[layer_name])

        for layer_name, layer_texture in self.map_texture.iteritems():
            for y in range(m.grid_height):
                for x in range(m.grid_width):
                    layer_texture.blit_into(m.tileset_seq[m.grid[layer_name][y][x].tileset_coord], x * grid_size, y * grid_size, 0)

    def draw_map_early(self):
        for layer_name, layer_sprite in self.tile_sprite.iteritems():
            if layer_name.startswith("ground"):
                self.game.world_objects_to_draw.insert(0, layer_sprite)

    def draw_map_late(self):
        for layer_name, layer_sprite in self.tile_sprite.iteritems():
            if layer_name.startswith("sky"):
                self.game.world_objects_to_draw.append(layer_sprite)

    def draw_editor(self):
        self.game.screen_objects_to_draw.append(self.game.editor)
        trig = self.game.editor.trigger_editor.drop_lists['triggers'].selected
        if not trig is None:
            zone = self.game.editor.trigger_editor.drop_lists['zones'].selected
            for z in trig.zones:
                r = primitives.RectPrimitive(rect=z, color=(135, 206, 250, 50))
                if not zone is None:
                    if z == zone:
                        r = primitives.RectPrimitive(rect=z, color=(65, 105, 225, 100))

                self.game.world_objects_to_draw.append(r)

    def draw_buttons(self):
        self.game.screen_objects_to_draw.extend(self.game.game_buttons.values())

    def draw_objects(self):
        for o in sorted(self.game.objects.values() + self.game.map.static_objects, key=(lambda obj: -obj.coord[1])):
            x = o.coord[0]
            y = o.coord[1]
            object_sprite = o.sprite
            self.game.world_objects_to_draw.append(object_sprite)

            for s, p in o.flair.itervalues():
                # s.set_position(x + p[0] + object_sprite.width // 2, y + p[1] + object_sprite.height // 2)
                s.x = x + p[0] + object_sprite.width // 2
                s.y = y + p[1] + object_sprite.height // 2
                self.game.world_objects_to_draw.append(s)

            if hasattr(o, 'held_props'):
                for prop in o.held_props:
                    self.game.world_objects_to_draw.append(prop.sprite)

            if o == self.game.selected_object:
                r = o.highlight_radius
                sprit = draw_circle(r, (200, 0, 0))
                sprit.x = o.coord[0] + o.sprite_width // 2 - r
                sprit.y = o.coord[1] + o.sprite_height // 2 - r
                self.game.world_objects_to_draw.append(sprit)

    def draw_character_stats(self):
        if self.game.disp_object_stats:
            if self.game.object_stats is None:
                return
            border = 4
            o = self.game.object_stats  # background, image, name, age
            o[1].x = window.width - o[1].width - o[2].content_width - border
            o[1].y = window.height - o[1].height - border
            o[0].x, o[0].y = o[1].x - border, o[1].y - border
            o[2].x = o[1].x + o[1].width
            o[2].y = window.height - o[2].content_height
            o[3].x = o[2].x
            o[3].y = o[2].y - o[2].content_height
            self.game.screen_objects_to_draw += o  # self.game.object_stats

    def draw_fear_bar(self):
        nplayers = len(self.game.players)
        self.game.screen_objects_to_draw.append(self.fear_text)
        w = window.width - self.fear_text.content_width
        h = 32
        for i, p in enumerate(self.game.players.itervalues()):
            sp = primitives.RectPrimitive(x=self.fear_text.content_width,
                                          y=h * i,
                                          width=w * (p.fear / MAX_FEAR),
                                          height=h,
                                          color=(255, 0, 0, 255))
            self.game.screen_objects_to_draw.append(sp)

    def draw_world_objects(self):  # stuff relative to camera
        self.camera_group.set_state_recursive()
        for f in self.game.world_objects_to_draw:
            f.draw()
        self.camera_group.unset_state_recursive()
        self.game.world_objects_to_draw = []

    def draw_screen_objects(self):  # stuff relative to screen
        for f in self.game.screen_objects_to_draw:
            f.draw()
        self.game.screen_objects_to_draw = []

    def draw_torch(self):
        # TODO: do this in a sane/clever way
        ppos = (self.game.players['player1'].coord[0] + self.game.players['player1'].dimensions[0] // 2,
                self.game.players['player1'].coord[1] + self.game.players['player1'].dimensions[1] // 2)

        hole = rect.Rect(
            self.game.camera.apply_camera((ppos[0] - self.light_size[0] // 2, ppos[1] - self.light_size[1] // 2)),
            self.light_size)

        hole.width *= self.game.camera.zoom
        hole.height *= self.game.camera.zoom

        self.light.scale_x = (200 / self.light.image.height) * self.game.camera.zoom
        self.light.scale_y = (200 / self.light.image.height) * self.game.camera.zoom

        self.light.position = hole.bottomleft

        self.game.screen_objects_to_draw.append(
            primitives.RectPrimitive(x=0, y=0, width=hole.right, height=hole.bottom, color=(0, 0, 0, 255)))

        self.game.screen_objects_to_draw.append(
            primitives.RectPrimitive(x=hole.right, y=0, width=window.width - hole.right, height=hole.top,
                                     color=(0, 0, 0, 255)))

        self.game.screen_objects_to_draw.append(
            primitives.RectPrimitive(x=hole.left, y=hole.top, width=window.width - hole.left,
                                     height=window.height - hole.top, color=(0, 0, 0, 255)))

        self.game.screen_objects_to_draw.append(
            primitives.RectPrimitive(x=0, y=hole.bottom, width=hole.left, height=window.height - hole.bottom,
                                     color=(0, 0, 0, 255)))

        self.game.screen_objects_to_draw.append(self.light)

    def say_fears(self):
        for o in self.game.objects.itervalues():
            if isinstance(o, Player):
                surf = text.speech_bubble("Oonce oonce oonce oonce!", 200)
                pos = (o.coord[0] + o.dimensions[0], o.coord[1] - surf.get_height())
                self.game.world_objects_to_draw.append((surf, pos))
                continue

            message = ''
            for f in o.scared_of:
                if f != 'player':
                    message += f + '\n'
            surf = text.speech_bubble(message, 300)
            pos = (o.coord[0] + o.dimensions[0], o.coord[1] - surf.get_height())
            self.game.world_objects_to_draw.append((surf, pos))

    def show_fear_ranges(self):
        for o in self.game.objects.itervalues():
            if isinstance(o, Player):
                r = o.fear_collection_radius
                sprit = draw_circle(r, (64, 224, 208))
                sprit.set_position(o.coord[0] + o.sprite_width // 2 - r, o.coord[1] + o.sprite_height // 2 - r)
                self.game.world_objects_to_draw.append(sprit)
            else:
                r = o.fear_radius
                sprit = draw_circle(r, (75, 0, 130))
                sprit.set_position(o.coord[0] + o.dimensions[0] // 2 - r, o.coord[1] + o.dimensions[0] // 2 - r)
                self.game.world_objects_to_draw.append(sprit)
