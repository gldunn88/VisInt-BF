import pygame as pg
import src.rendering_contants as rc


class IOPromptError(Exception):
    pass


class IOPrompt():

    def __init__(self, prompt: str, def_response: str = "", typeface: str = "freesansbold.ttf", point_size: int = 32):
        self.prompt = prompt
        self.response = def_response
        self.font = pg.font.Font(typeface, point_size)

        self.text_surface = pg.Surface = None
        self.redraw = True

    def renderPrompt(self, screen: pg.Surface, prompt_rect: pg.Rect):

        if self.redraw:
            self.text_surface = self.font.render(self.toString(), True, rc.CLR_WHITE, rc.CLR_BLACK)
            self.redraw = False

        pg.draw.rect(screen, rc.CLR_RED, prompt_rect, width=1)

        text_rect = self.text_surface.get_rect()
        text_rect.topleft = (prompt_rect.left + 5, prompt_rect.top + 5)
        screen.blit(self.text_surface, text_rect)

    def appendResponse(self, text: str):
        self.response = f"{self.response}{text}"
        self.redraw = True

    def setResponse(self, text: str):
        self.response = text
        self.redraw = True

    def setPrompt(self, prompt: str):
        self.prompt = prompt
        self.redraw = True

    def backspaceResponse(self):
        if len(self.response) > 0:
            self.response = self.response[:len(self.response)-1]
            self.redraw = True

    def toString(self):
        return f"{self.prompt} {self.response}"
