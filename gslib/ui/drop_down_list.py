from __future__ import absolute_import, division, print_function

import pyglet

from gslib.ui import button, slider
from gslib.utils import ExecOnChange, exec_on_change_meta
from gslib.ui import control
from gslib import window


class DropDownList(control.Control):

    __metaclass__ = exec_on_change_meta(["update_buttons"])

    color = ExecOnChange
    border_color = ExecOnChange
    border_width = ExecOnChange
    text = ExecOnChange
    font_size = ExecOnChange
    selected_name = ExecOnChange

    def __init__(self, owner=None, items=None, function=None, color=(120, 0, 0),
                 border_color=(120, 50, 80), border_width=2, text=None, font_size=10, labels='dictkey', order=(0, 0),
                 window=window, **kwargs):
        super(DropDownList, self).__init__(window=window, **kwargs)
        self.color = color
        self.border_color = border_color
        self.border_width = border_width
        self.text = text
        self.font_size = font_size
        self.labels = labels
        self._open = False

        self._drop_group = pyglet.graphics.OrderedGroup(99, self._group)

        self.function = function

        self.order = order
        self.owner = owner  # container that created the button, allows for the button function to interact with its creator

        self.items = items
        self.selected_name = "<None>"
        self.selected = None
        self.main_button = button.DefaultButton(owner=self, function=self.main_button_click, pos=self.pos,
                                                size=self.size, font_size=font_size, visible=self.visible,
                                                text=u"<None>", border_color=self.border_color,
                                                border_width=self.border_width, color=self.color, batch=self._batch,
                                                group=self._group)
        self.drop_buttons = []

        self.first_time = True
        self.refresh()

        self.high_color = (0, 120, 0)
        self.high_border_color = (0, 200, 0)

        self.update_buttons()
        # self.redraw()

    @property
    def open(self):
        return self._open

    @open.setter
    def open(self, value):
        self._open = value

        if self._window is not None:
            if value:
                self._window.push_handlers(on_mouse_motion=self.on_mouse_motion)
            else:
                self._window.remove_handlers(on_mouse_motion=self.on_mouse_motion)
        for b in self.drop_buttons:
            b.visible = not b.visible
            b.enabled = not b.enabled
        self.update_buttons()

    def refresh(self, new_items=None):  # call if the list changes
        if not new_items is None:
            self.items = new_items

        for b in self.drop_buttons:
            b.delete()

        self.drop_buttons = [
            button.DefaultButton(self, self.list_func(None), size=self.size, font_size=self.font_size, visible=False,
                                 text=u"<None>", border_color=self.border_color, border_width=self.border_width,
                                 color=self.color, batch=self._batch, group=self._drop_group)]

        if isinstance(self.items, list):
            for i in self.items:
                if self.labels == 'func_name':
                    t = i.func_name
                elif self.labels == 'classname':
                    t = i.__class__.__name__
                else:
                    t = str(i)
                self.drop_buttons.append(
                    button.DefaultButton(self, self.list_func(i, t), size=self.size, font_size=self.font_size,
                                         visible=False, text=t, border_color=self.border_color,
                                         border_width=self.border_width, color=self.color, batch=self._batch,
                                         group=self._drop_group))
        else:
            for k, v in self.items.iteritems():
                if self.labels == 'classname':
                    t = v.__class__.__name__
                    t += ': '
                    t += unicode(k)
                else:
                    t = unicode(k)
                self.drop_buttons.append(
                    button.DefaultButton(self, self.list_func(k, t), size=self.size, font_size=self.font_size,
                                         visible=False, text=t, border_color=self.border_color,
                                         border_width=self.border_width, color=self.color, batch=self._batch,
                                         group=self._drop_group))

        if not self.first_time: # prevent self.function() being run before the owner of this list is fully initialised
            self.set_to_default()
        else:
            self.first_time = False

        if self.open:
            self.update_buttons()

    def update_buttons(self):
        self.main_button.text = self.selected_name
        self.main_button.color = self.color
        self.main_button.border_color = self.border_color
        self.main_button.size = self.size
        self.main_button.visible = self.visible
        self.main_button.font_size = self.font_size
        self.main_button.pos = self.pos
        for i, b in enumerate(self.drop_buttons):
            b.color = self.color
            b.border_color = self.border_color
            b.size = self.size
            b.visible = self.open and self.visible
            b.font_size = self.font_size
            b.pos = (self.pos[0], self.pos[1] - (1 + i) * self.size[1])

    def main_button_click(self):
        self.open = not self.open

    def on_mouse_motion(self, x, y, dx, dy):
        pos = self.pos
        w, h = self.size
        w //= 2

        eh = pos[1] + h - y
        h_ind = eh // h

        n_drop_button = len(self.drop_buttons)
        if hasattr(self, 'slider'):
            n_drop_button = self.max_display + 1

        # if move off edge, close list
        # if move off bottom or top, close list
        if not self.x <= x < self.x + self.width:
            self.open = False
            return

        # highlight the moused-over button

        high_b = None
        for b in self.drop_buttons:
            if b.color != self.color:
                b.color = self.color
            if b.border_color != self.border_color:
                b.border_color = self.border_color

            if b.in_bounds(x, y):
                high_b = b

        if high_b is not None:
            if high_b.border_color != self.high_border_color:
                high_b.border_color = self.high_border_color
            if high_b.color != self.high_color:
                high_b.color = self.high_color

    def set_to_default(self):
        self.set_to_value(None)

    def set_to_value(self, value):
        self.list_func(value)()

    def _update_position(self):
        self.update_buttons()

    def _update_size(self):
        self.update_buttons()

    def _update_enabled(self):
        self.main_button.enabled = self.enabled
        if not self.enabled and self._window is not None:
            self._window.remove_handlers(on_mouse_motion=self.on_mouse_motion)

    def draw(self):
        if self.visible:
            self.main_button.draw()
            if self.open:
                for b in self.drop_buttons:
                    b.draw()

    def in_bounds(self, x, y):
        if self.open:
            height = self.height
        else:
            height = self.height
        return (self.x <= x < self.x + self.width and
                self.y <= y < self.y + height)

    def list_func(self, val, text=None):
        def func():
            if val is None:
                self.selected_name = "<None>"
                self.selected = None
            else:
                if text is None:
                    self.selected_name = str(val)
                else:
                    self.selected_name = text
                if isinstance(self.items, list):
                    self.selected = val
                else:
                    self.selected = self.items[val]
            if self.function is not None:
                self.function()
        return func


class DropDownListSlider(DropDownList):
    def __init__(self, owner, items, function=None, max_display=6, *args,  **kwargs):
        self.max_display = max_display - 1

        self.slider = slider.Slider(self, self.set_scroll, horizontal=False)
        super(DropDownListSlider, self).__init__(owner, items, function, *args, **kwargs)

    def refresh(self, new_items=None):
        n_display = min(self.max_display, len(self.drop_buttons))
        n_display += 1
        self.slider.size = (20, n_display * self.size[1])

        self.slider.pos = self.pos[0] + self.size[0] - self.slider.size[0], self.pos[1] - self.slider.height

        self.slider.value = 0
        self.set_scroll(0)

        super(DropDownListSlider, self).refresh(new_items)

    def update_buttons(self):
        super(DropDownListSlider, self).update_buttons()
        self.slider.visible = self.open and len(self.drop_buttons) > self.max_display
        self.slider.enabled = self.open and len(self.drop_buttons) > self.max_display
        self.set_scroll(self.slider.value)

        if len(self.drop_buttons) > self.max_display:
            for b in self.drop_buttons:
                b.width -= self.slider.width

    def set_scroll(self, value):
        if not self.open:
            return
        n_scroll = len(self.drop_buttons) - self.max_display
        if n_scroll <= 0:
            return

        slider_range = (self.slider.max - self.slider.min)
        range_per_button = slider_range // n_scroll
        button_n = value // range_per_button # 1 indexed, 0 = show 0th drop button (no scroll)
        if button_n == n_scroll:
            button_n -= 1

        for i, b in enumerate(self.drop_buttons):
            if i < button_n or i > self.max_display + button_n:
                b.visible = False
                b.enabled = False
            else:
                j = i - button_n
                b.pos = self.pos[0], self.pos[1] - (j + 1) * self.size[1]
                b.visible = True
                b.enabled = True

    def draw(self):
        super(DropDownListSlider, self).draw()
        if self.open:
            self.slider.draw()
