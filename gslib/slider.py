import pyglet

from gslib import graphics
from gslib import sprite

def create_property(var):  # creates a member variable that redraws the button when changed.
    def _setter(self, val):
        old_val = getattr(self, '_' + var)
        if old_val != val:
            setattr(self, '_' + var, val)
            self.redraw()

    def _getter(self):
        return getattr(self, '_' + var)

    return property(_getter, _setter)


class Slider(object):
    """
    Basic example:
        s = Slider(self, self.function)
    self.function:
    if slider.enabled == True:
        Function passed in will be called with 1 argument (current value of slider).
        Create function in class that creates the slider and pass it in as second argument.
    """

    back_group = pyglet.graphics.OrderedGroup(0)
    fore_group = pyglet.graphics.OrderedGroup(1)

    def __init__(self, owner, func, pos=(0, 0), range=(0, 100), value=50, size=(100, 20), back_colour=(120, 0, 0),
                 fore_colour=(0, 120, 0), order=(0, 0), enabled=True, visible=True, sprite_batch=None, sprite_group=None):

        self.owner = owner
        self.min, self.max = range
        self._value = value
        self._fore_colour = fore_colour
        self._back_colour = back_colour
        self._size = size
        self._visible = visible
        self.enabled = enabled
        self._pos = pos
        self.sprite_batch = sprite_batch
        self.sprites = [graphics.new_rect_sprite(), graphics.new_rect_sprite()]

        if sprite_group:
            self.back_group = pyglet.graphics.OrderedGroup(0, sprite_group)
            self.fore_group = pyglet.graphics.OrderedGroup(1, sprite_group)
        self.sprites[0].group = self.back_group
        self.sprites[1].group = self.fore_group
        self.order = order

        self.isClicked = False

        self.func = func

        self.redraw()

    def get_value(self):
        return self._value
    def set_value(self, val):
        self._value = val
        if self._value > self.max:
            self._value = self.max
        if self._value < self.min:
            self._value = self.min
        self.redraw()
    value = property(get_value, set_value)

    fore_colour = create_property('fore_colour')
    back_colour = create_property('back_colour')
    size = create_property('size')
    visible = create_property('visible')
    pos = create_property('pos')

    def redraw(self):
        self.sprites[0].color_rgb = self.back_colour
        self.sprites[1].color_rgb = self.fore_colour
        if not self.visible:
            self.sprites[0].batch = None
            self.sprites[1].batch = None
            return

        # background sprite
        self.sprites[0].color_rgb = self.back_colour
        self.sprites[0].batch = self.sprite_batch
        self.sprites[0].set_position(self.pos[0], self.pos[1])
        self.sprites[0].scale_x = self.size[0]
        self.sprites[0].scale_y = self.size[1]

        # foreground sprite
        self.sprites[1].color_rgb = self.fore_colour
        self.sprites[1].batch = self.sprite_batch
        self.sprites[1].set_position(self.pos[0], self.pos[1])
        self.sprites[1].scale_x = self.size[0] * (self.value - self.min) / float(self.max - self.min)
        self.sprites[1].scale_y = self.size[1]

    def check_clicked(self, pos, typ):
        if not self.enabled:
            return
        click_pos = pos
        w, h = self.size
        w /= 2
        h /= 2

        if typ == 'up':
            self.isClicked = False
            return

        if typ == 'down' and abs(click_pos[0] - (self.pos[0] + w)) < w and abs(click_pos[1] - (self.pos[1] + h)) < h:
            self.isClicked = True

        if self.isClicked:
            frac = (click_pos[0] - self.pos[0]) / float(self.size[0])
            self.value = self.min + (self.max - self.min) * frac
            self.func(self.value)

