
import pygame as pg
import src.rendering_contants as rc
from src.bf import BFInterpreter


class HudRenderer():

    def __init__(self, interpreter: BFInterpreter, typeface: str = "freesansbold.ttf", point_size: int = 32):

        self.interpreter = interpreter

        self.font = pg.font.Font(typeface, point_size)
        self.last_hertz = -1
        self.last_interpreter_state = -1
        self.last_step_count = -1

        self.hertz_text_surface: pg.Surface = None
        self.step_text_surface: pg.Surface = None
        self.state_text_surface: pg.Surface = None

    def renderHud(self, screen: pg.Surface, hud_rect: pg.Rect, hertz: int):
        if self.last_hertz != hertz:
            self.hertz_text_surface = self.font.render(f"CPU: {hertz}Hz", True, rc.CLR_WHITE, rc.CLR_BLACK)
            self.last_hertz = hertz

        if self.interpreter.state != self.last_interpreter_state:
            self.state_text_surface = self.font.render(f"State: {self.interpreter.state._name_}", True, rc.CLR_WHITE, rc.CLR_BLACK) # noqa 
            self.last_interpreter_state = self.interpreter.state

        if self.last_step_count != self.interpreter.step_count:
            self.step_text_surface = self.font.render(f"Step Count: {self.interpreter.step_count}", True, rc.CLR_WHITE, rc.CLR_BLACK) # noqa
            self.last_step_count = self.interpreter.step_count

        hertz_rect = self.hertz_text_surface.get_rect()
        state_rect = self.state_text_surface.get_rect()
        step_rect = self.step_text_surface.get_rect()

        hertz_rect.topleft = (10 + hud_rect.left, 10 + hud_rect.top)
        state_rect.topleft = (hertz_rect.left, hertz_rect.bottom + 10)
        step_rect.topleft = (state_rect.left, state_rect.bottom + 10)

        screen.blit(self.hertz_text_surface, hertz_rect)
        screen.blit(self.state_text_surface, state_rect)
        screen.blit(self.step_text_surface, step_rect)
