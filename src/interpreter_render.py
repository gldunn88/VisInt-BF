import logging
from operator import le
import pygame as pg
import src.rendering_contants as rc
from src.bf import BFInterpreter


class BFRenderer():

    def __init__(self,
                 interpreter: BFInterpreter,
                 camera_speed: int = 100,
                 cell_width: int = 50,
                 cell_buffer: int = 25,
                 cell_max_height: int = 400,
                 typeface: str = "freesansbold.ttf",
                 point_size: int = 32):
        self.interpreter = interpreter

        # Camera Tracking
        self.camera_offset: float = 0
        self.camera_target: int = 0
        self.camera_speed = camera_speed

        # Derive rendering constants
        self.cell_width = cell_width
        self.cell_buffer = cell_buffer
        self.cell_unit_height = cell_max_height/interpreter.max_value
        self.cell_base_y = cell_max_height
        
        self.first_render = True
    def setCameraOffset(self, x: float):
        self.camera_offset = x

    def setCameraTarget(self, x: int):
        self.camera_target = x

    def moveCamera(self, tick_time: float):
        movement = tick_time * self.camera_speed

        if abs(self.camera_offset - self.camera_target) < movement:
            self.camera_offset = self.camera_target
        elif self.camera_offset < self.camera_target:
            self.camera_offset += movement
        else:
            self.camera_offset -= movement

    def render(self, screen: pg.Surface, interpreter_rect: pg.Rect, tick_time: float):
        
        # Calculate the gamespace ptr position
        ptr_rect = pg.Rect((self.cell_width + self.cell_buffer) * self.interpreter.ptr, # noqa
                           self.cell_base_y + 20,
                           self.cell_width,
                           self.cell_width)

        # Update Camera Position to target the ptr in gamespace
        if self.first_render:
            self.setCameraOffset(ptr_rect.left - (screen.get_width()/2 - (self.cell_buffer + self.cell_width)/2))
            self.first_render = False
        else:
            self.setCameraTarget(ptr_rect.left - (screen.get_width()/2 - (self.cell_buffer + self.cell_width)/2))
        self.moveCamera(tick_time)

        # Apply offsets to the ptr
        ptr_rect.left += interpreter_rect.left - self.camera_offset
        ptr_rect.top += interpreter_rect.top
        # Render the ptr
        ptr_color = rc.CLR_WHITE
        pg.draw.polygon(
            surface=screen,
            color=ptr_color,
            points=[
                ptr_rect.bottomleft,
                (ptr_rect.centerx, ptr_rect.top),
                ptr_rect.bottomright])

        # Render the memory cells
        for i in range(0, len(self.interpreter.memory)):
            height = self.interpreter.memory[i] * self.cell_unit_height
            draw_x = interpreter_rect.left + (self.cell_width + self.cell_buffer) * i - self.camera_offset

            # Draw cell reference base
            cell_base_rect = pg.Rect(draw_x - self.cell_buffer/4,
                                     interpreter_rect.top + self.cell_base_y,
                                     self.cell_width + self.cell_buffer/2,
                                     10)

            pg.draw.rect(screen, rect=cell_base_rect, color=rc.CLR_RED)

            # Draw memory
            cell_rect = pg.Rect(draw_x,
                                interpreter_rect.top + self.cell_base_y - height,
                                self.cell_width,
                                height)

            pg.draw.rect(screen, rect=cell_rect, color=rc.CLR_WHITE)

