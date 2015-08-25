from __future__ import absolute_import, division, print_function

from pyglet import gl

from gslib.engine import primitives


class ButtonPrimitive(primitives.Primitive):

    num_verts = 8
    mode = gl.GL_QUADS

    def __init__(self, width=0, height=0, color=(0, 0, 0), border_color=(0, 0, 0), border_width=3, pressed=False,
                 visible=True, **kwargs):
        self._width = width
        self._height = height
        self._border_color = border_color + (255,)
        self._border_width = border_width
        self._pressed = pressed
        self._visible = visible

        super(ButtonPrimitive, self).__init__(color=(color + (255,)), **kwargs)

    @property
    def width(self):
        return self._width

    @width.setter
    def width(self, value):
        self._width = value
        self._update_verticies()

    @property
    def height(self):
        return self._height

    @height.setter
    def height(self, value):
        self._height = value
        self._update_verticies()

    @property
    def color(self):
        return tuple(self._color[:3])

    @color.setter
    def color(self, value):
        self._color = value + (255,)
        self._update_colors()

    @property
    def border_color(self):
        return tuple(self._border_color[:3])

    @border_color.setter
    def border_color(self, value):
        self._border_color = value + (255,)
        self._update_colors()

    @property
    def border_width(self):
        return self._border_width

    @border_width.setter
    def border_width(self, value):
        self._border_width = value
        self._update_verticies()

    @property
    def pressed(self):
        return self._pressed

    @pressed.setter
    def pressed(self, value):
        self._pressed = value
        self._update_colors()

    @property
    def visible(self):
        return self._visible

    @visible.setter
    def visible(self, value):
        self._visible = value
        if value:
            self._update_verticies()
        else:
            self._vertex_list.vertices[:] = [0] * 16

    def _update_colors(self):
        colors = list((self.border_color + (255,)) * 4 + (self.color + (255,)) * 4)
        if self.pressed:
            colors[4:7] = [min(int(x * 1.5), 255) for x in colors[4:7]]
            colors[20:23] = [min(int(x * 1.5), 255) for x in colors[20:23]]
        else:
            colors[12:15] = [min(int(x * 1.5), 255) for x in colors[12:15]]
            colors[28:31] = [min(int(x * 1.5), 255) for x in colors[28:31]]
        self._vertex_list.colors[:] = colors

    def _update_verticies(self):
        outer_rect = [
            self.x, self.y,
            self.x + self.width, self.y,
            self.x + self.width, self.y + self.height,
            self.x, self.y + self.height]
        inner_rect = [
            self.x + self.border_width, self.y + self.border_width,
            self.x + self.width - self.border_width, self.y + self.border_width,
            self.x + self.width - self.border_width, self.y + self.height - self.border_width,
            self.x + self.border_width, self.y + self.height - self.border_width]

        self._vertex_list.vertices[:] = map(int, outer_rect + inner_rect)
