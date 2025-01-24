from typing import *
from pyray import *
READING_INTERVAL = 0.1
TEXT_SPACING = 10

DASH_INTERVAL = 2
class Button:
    def __init__(self, front_text: str, font_size: int, boundaries: Rectangle):
        self.front_text = front_text
        self.font_size = font_size
        self.boundaries = boundaries
        self._on = False
        self._enabled = False
    def update(self):
        if not self._enabled:
            return
        boundaries = self.boundaries
        current_position = get_mouse_position()
        if is_mouse_button_pressed(MouseButton.MOUSE_BUTTON_LEFT):
            if check_collision_point_rec(current_position, self.boundaries):
                self.toggle_light()
        if self._on:
            draw_rectangle(int(boundaries.x), int(boundaries.y), int(boundaries.width), int(boundaries.height), GREEN)
        else:
            draw_rectangle(int(boundaries.x), int(boundaries.y), int(boundaries.width), int(boundaries.height), RED)           
        draw_text(self.front_text, int(boundaries.x - measure_text(self.front_text, self.font_size) - 10), int(boundaries.y), self.font_size, WHITE)
    def toggle(self):
        self._enabled = not self._enabled
    def toggle_light(self):
        self._on = not self._on
class InputButton:
    def __init__(self, front_text: str, font_size: int, boundaries: Rectangle):
        self.front_text = front_text
        self.text = ""
        self.font_size = font_size
        self.boundaries = boundaries
        self._is_in_focus = False
        self._enabled = False
    def update(self):
        if not self._enabled:
            return
        boundaries = self.boundaries
        draw_rectangle(int(boundaries.x), int(boundaries.y), int(boundaries.width), self.font_size, WHITE)
        current_position = get_mouse_position()
        self._is_in_focus = check_collision_point_rec(current_position, self.boundaries)
        if self._is_in_focus:
            pressed_key = get_key_pressed()
            if pressed_key >= 48 and pressed_key <= 57:
                self.text += chr(pressed_key)
            if is_key_pressed(KeyboardKey.KEY_BACKSPACE):
                self.text = self.text[:-1]
        to_write = self.text
        if int(get_time()) % DASH_INTERVAL == 0:
            to_write += "_"
        draw_text(to_write, int(boundaries.x), int(boundaries.y), self.font_size, BLACK)
        draw_text(self.front_text, int(boundaries.x - measure_text(self.front_text, self.font_size) - 10), int(boundaries.y), self.font_size, WHITE)
    def toggle(self):
        self._enabled = not self._enabled 

class Dialogue:
    def __init__(self, interval: float, text: str, font_size: str, colors: List[Color], position: Vector2):
        self.colors = colors
        self.interval = interval
        self.text = text
        self.font_size = font_size
        self.position = position
        self._current_character = 0
        self._current_color = 0
        self._time_elapsed = 0
        self._character_clock = 0
        self._enabled = False
    def update(self):
        if not self._enabled:
            return
        self._time_elapsed += get_frame_time()
        self._character_clock += get_frame_time()
        if self._time_elapsed > self.interval:
            self._time_elapsed = self._time_elapsed % self.interval
            self._current_color = (self._current_color + 1) % len(self.colors)
        if self._character_clock > READING_INTERVAL:
            self._character_clock = self._character_clock % READING_INTERVAL
            if self._current_character < len(self.text):
                self._current_character += 1
        intermediate_color = color_lerp(self.colors[self._current_color], self.colors[(self._current_color + 1) % len(self.colors)], self._time_elapsed / self.interval)
        snippet = self.text[0:(self._current_character + 1)]
        accumulated_x_offset = 0
        for i, char in enumerate(snippet):
            if i > 0:
                accumulated_x_offset += measure_text(snippet[i - 1], self.font_size) + (self.font_size / TEXT_SPACING)
            draw_text(char, int(self.position.x + accumulated_x_offset), int(self.position.y), self.font_size, intermediate_color)
    def toggle(self):
        if self._enabled:
            self._current_character = 0
            self._current_color = 0
            self._time_elapsed = 0
            self._character_clock = 0
        self._enabled = not self._enabled 
