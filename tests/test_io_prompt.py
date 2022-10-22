from src.io_prompt import IOPrompt
import pygame as pg


# Groups tests related to the IO Prompt
class TestIOPrompt:
    def initialize_pygame(self):
        if not pg.get_init():
            pg.init()

    def test_initialization_defaults(self):

        self.initialize_pygame()

        prompt = IOPrompt("test:")
        assert prompt.prompt == "test:"
        assert prompt.response == ""
        assert prompt.redraw is True
        assert prompt.toString() == "test: "

    def test_initialization_initresponse(self):

        self.initialize_pygame()

        prompt = IOPrompt("test:", "hello")
        assert prompt.prompt == "test:"
        assert prompt.response == "hello"
        assert prompt.redraw is True
        assert prompt.toString() == "test: hello"

    def test_setPrompt_empty(self):
        self.initialize_pygame()

        prompt = IOPrompt("test:")

        prompt.redraw = False
        prompt.setPrompt("")
        assert prompt.prompt == ""
        assert prompt.response == ""
        assert prompt.redraw is True

    def test_setPrompt_newValue(self):
        self.initialize_pygame()

        prompt = IOPrompt("test:")
        assert prompt.prompt == "test:"

        prompt.redraw = False
        prompt.setPrompt("newtest:")
        assert prompt.prompt == "newtest:"
        assert prompt.response == ""
        assert prompt.redraw is True
        assert prompt.toString() == "newtest: "

    def test_setResponse_empty(self):
        self.initialize_pygame()

        prompt = IOPrompt("test:", "hello")
        assert prompt.response == "hello"

        prompt.redraw = False
        prompt.setResponse("")
        assert prompt.prompt == "test:"
        assert prompt.response == ""
        assert prompt.redraw is True
        assert prompt.toString() == "test: "

    def test_setResponse_newValue(self):
        self.initialize_pygame()

        prompt = IOPrompt("test:")
        assert prompt.response == ""

        prompt.redraw = False
        prompt.setResponse("hello")
        assert prompt.prompt == "test:"
        assert prompt.response == "hello"
        assert prompt.redraw is True
        assert prompt.toString() == "test: hello"

    def test_appendResponse_empty(self):
        self.initialize_pygame()

        prompt = IOPrompt("test:", "hello")
        assert prompt.response == "hello"

        prompt.redraw = False
        prompt.appendResponse("")
        assert prompt.prompt == "test:"
        assert prompt.response == "hello"
        assert prompt.redraw is True
        assert prompt.toString() == "test: hello"

    def test_appendResponse_newText(self):
        self.initialize_pygame()

        prompt = IOPrompt("test:", "hello")
        assert prompt.response == "hello"

        prompt.redraw = False
        prompt.appendResponse(" world")
        assert prompt.prompt == "test:"
        assert prompt.response == "hello world"
        assert prompt.redraw is True
        assert prompt.toString() == "test: hello world"

    def test_backspace_empty(self):
        self.initialize_pygame()

        prompt = IOPrompt("test:")
        assert prompt.response == ""

        prompt.redraw = False
        prompt.backspaceResponse()
        assert prompt.prompt == "test:"
        assert prompt.response == ""
        assert prompt.redraw is False

    def test_backspace_withText(self):
        self.initialize_pygame()

        prompt = IOPrompt("test:", "hello")
        assert prompt.response == "hello"

        prompt.redraw = False
        prompt.backspaceResponse()
        assert prompt.prompt == "test:"
        assert prompt.response == "hell"
        assert prompt.redraw is True
