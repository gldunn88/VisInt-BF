
import pygame as pg
import os
import sys
import logging
import time
import json
from src.bf import BFInterpreter, BFRuntimeError, ProgramState
from src.hud_render import HudRenderer
from src.interpreter_render import BFRenderer
from src.io_prompt import IOPrompt
import src.rendering_contants as rc
from src.gamestate import Gamestate


class CliInitError(Exception):
    pass


class EnvironmentInitError(Exception):
    pass


# see if we can load more than standard BMP
if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")

# Constants
# Rendering Display
SCREENRECT = pg.Rect(0, 0, 640, 480)

# Cell Rendering Constants
CELL_INITIAL_X = 50
CELL_INITIAL_Y = 520
CELL_OFFSET = 25
CELL_WIDTH = 50

CELL_UNIT_HEIGHT = 25

# Pointer Rendering
PTRRECT = pg.Rect(0, CELL_INITIAL_Y+10, CELL_WIDTH, CELL_WIDTH)
CAMERA_OFFSET = 0
CAMERA_OFFSET_TARGET = 0
CAMERA_X_SPEED = 100

# UI Control Values
UI_INIT_TOPLEFT = (20, 20)

# Interpreter Control Values
INT_SRC = ""
INT_CELL_COUNT = 8
INT_CELL_MAX_VALUE = 16
INT_CELL_DEFAULT_VALUE = 0
INT_INITIAL_VALUES = []

main_dir = os.path.split(os.path.abspath(__file__))[0]


def load_image(file):

    file = os.path.join(main_dir, "images", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit(f'Could not load image "{file}" {pg.get_error()}')
    return surface.convert()


def initPyGame():
    logging.info("Initializing PyGame")
    # Initialize pygame
    if pg.get_sdl_version()[0] == 2:
        pg.mixer.pre_init(44100, 32, 2, 1024)
    pg.init()
    if pg.mixer and not pg.mixer.get_init():
        logging.warning("Warning, no sound")
        pg.mixer = None


def initWindow(width=800, height=600) -> pg.Surface:
    global SCREENRECT

    SCREENRECT = pg.Rect(0, 0, width, height)
    winstyle = 0  # |FULLSCREEN
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    return pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)


def initLogging(verbose: bool):
    if verbose:
        logging.basicConfig(level=logging.DEBUG)
    else:
        logging.basicConfig(level=logging.INFO)


def openSrcFile(path: str):
    global INT_SRC
    logging.info(f"Loading source file from: {path}")

    with open(path, 'r') as f:
        INT_SRC = f.read()


def raiseEnvFileException(message: str):
    logging.error(message)
    raise EnvironmentInitError(message)


def openEnvFile(path: str):
    global INT_CELL_COUNT, INT_CELL_MAX_VALUE, INT_CELL_DEFAULT_VALUE, INT_INITIAL_VALUES

    logging.info(f"Loading environment file from: {path}")

    with open(path, 'r') as f:
        content_json = json.loads(f.read())

        # Setting cell maximum allowed value
        cell_max = content_json["memory"]["cell_max_value"]
        if type(cell_max) is not int or cell_max < 1:
            raiseEnvFileException("Value 'cell_max_value' must be an integer greater than 0")
        INT_CELL_MAX_VALUE = cell_max

        # Setting cell count
        cell_count = content_json["memory"]["cell_count"]
        if type(cell_count) is not int or cell_count < 1:
            raiseEnvFileException("Value 'cell_count' must be an integer greater than 0")
        INT_CELL_COUNT = cell_count

        # Setting cell default values
        cell_default = content_json["memory"]["cell_default_value"]
        if type(cell_default) is not int or cell_default < 0 or cell_default > INT_CELL_MAX_VALUE:
            raiseEnvFileException(f"Value 'cell_default_value' must be an integer in the range -> {INT_CELL_MAX_VALUE}")
        INT_CELL_DEFAULT_VALUE = cell_default

        # Setting cell initial values
        initial_values = content_json["memory"]["cell_initial_values"]

        # Do basic type and length validation with the settings already loaded
        if type(initial_values) is not list:
            raiseEnvFileException(f"List 'cell_initial_values' must be a list of integers in the range 0 -> {INT_CELL_MAX_VALUE}") # noqa

        if len(initial_values) > INT_CELL_COUNT:
            raiseEnvFileException("List 'cell_initial_values' cannot have more entries that the number of cells")

        for v in initial_values:
            if type(v) is not int or v < 0 or v > INT_CELL_MAX_VALUE:
                raiseEnvFileException("Values in list 'cell_initial_values' must be integers in the range 0 -> {INT_CELL_MAX_VALUE}") # noqa
        INT_INITIAL_VALUES = initial_values


def processCLI():

    verbose = False

    for i in range(1, len(sys.argv)):
        if sys.argv[i] in ["-v", "--verbose"]:
            verbose = True

    initLogging(verbose)

    # Load Command Line Arguments
    last_cmd = ""
    for i in range(1, len(sys.argv)):
        # Prepare to process next parameter set. May be one or two tokens
        if last_cmd == "":
            # Ignore verbose commands
            if sys.argv[i] in ["-v", "--verbose"]:
                continue

            # Explicitely allow only - parameters that are supported
            elif sys.argv[i] in ["-s", "--src-file", "-e", "--env-file"]:
                last_cmd = sys.argv[i]

            else:
                message = f"Unexpected cli parameter '{sys.argv[i]}' found"
                logging.error(message)
                raise CliInitError(message)

        # Process the second token in a two token parameter set.
        elif last_cmd in ["-s", "--src-file"]:
            openSrcFile(sys.argv[i])
            last_cmd = ""

        elif last_cmd in ["-e", "--env-file"]:
            openEnvFile(sys.argv[i])
            last_cmd = ""
        else:
            message = f"Unexpected cli parameter '{last_cmd}' found"
            logging.error(message)
            raise CliInitError(message)


def setCameraSpeed(pixels_per_second: int):
    global CAMERA_X_SPEED
    CAMERA_X_SPEED = pixels_per_second


def setCameraOffset(x: int, hard_set: bool = False):
    global CAMERA_OFFSET, CAMERA_OFFSET_TARGET

    CAMERA_OFFSET_TARGET = x

    if hard_set:
        CAMERA_OFFSET = CAMERA_OFFSET_TARGET


def updateCameraPosition(tick_time: float):
    global CAMERA_OFFSET

    camera_shift = tick_time*CAMERA_X_SPEED

    if abs(CAMERA_OFFSET - CAMERA_OFFSET_TARGET) < camera_shift:
        CAMERA_OFFSET = CAMERA_OFFSET_TARGET
    else:
        if CAMERA_OFFSET > CAMERA_OFFSET_TARGET:
            CAMERA_OFFSET -= camera_shift
        else:
            CAMERA_OFFSET += camera_shift


def main(winstyle=0):

    processCLI()

    # Init the engine and display window
    initPyGame()
    screen = initWindow(800, 600)

    # Init a BF program
    bf_interpreter = BFInterpreter(INT_CELL_COUNT, INT_CELL_MAX_VALUE)
    bf_interpreter.setMemory(INT_INITIAL_VALUES, INT_CELL_DEFAULT_VALUE)
    bf_interpreter.setTape(INT_SRC)

    # Init Graphics Handlers
    bf_renderer = BFRenderer(interpreter=bf_interpreter,
                             cell_width=50,
                             cell_buffer=25,
                             camera_speed=100,
                             cell_max_height=300)

    hud_renderer = HudRenderer(interpreter=bf_interpreter)
    gs = Gamestate(step_hertz=1)

    clock = pg.time.Clock()

    # Set up the step execution values
    step_delay = 1.0/gs.step_hertz
    step_next_time = time.time() + step_delay
    step_run = False

    # Set up input handling
    readbyte_prompt_running = False

    # Set up Cursor Tracking
    PTRRECT.left = CELL_INITIAL_X + bf_interpreter.ptr*(CELL_OFFSET + CELL_WIDTH)
    setCameraOffset(PTRRECT.left - SCREENRECT.width/2, hard_set=True)
    setCameraSpeed(100)

    # Set up contextual UI elements
    readbyte_prompt = IOPrompt("Cell Value:")

    last_tick = time.time()
    
    while True:
        # Hold Framerate to 60 fps
        clock.tick(60)

        # Store the seconds elapsed since the last tick
        tick_time = time.time() - last_tick
        last_tick = time.time()

        # Handle Input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return
            if readbyte_prompt_running:
                if event.type == pg.KEYUP:

                    if (event.unicode in "0123456789"):
                        readbyte_prompt.appendResponse(event.unicode)
                    elif event.key == pg.K_BACKSPACE:
                        readbyte_prompt.backspaceResponse()
                    elif event.key == pg.K_RETURN and len(readbyte_prompt.response) > 0:
                        readbyte_prompt_running = False
                        bf_interpreter.readByte(int(readbyte_prompt.response))
                        step_next_time = time.time() + step_delay

            else:
                # Pressing SPACE will toggle the program run mode
                if event.type == pg.KEYUP and event.key == pg.K_SPACE:
                    step_run = not step_run
                    step_next_time = time.time() + step_delay

                    if bf_interpreter.halted():
                        logging.debug("Disabling auto-run on halted program")
                        step_run = False

                    logging.debug(f"Setting program auto exec to {step_run}")

                # Pressing TAB will increase the execution rate by powers of 2
                if event.type == pg.KEYUP and event.key == pg.K_TAB:
                    gs.multiplyStepHertz(factor=2, loop=True)

                    step_delay = 1.0/gs.step_hertz
                    step_next_time = time.time() + step_delay

        # Execute Instructions
        if step_run and bf_interpreter.canStep() and time.time() >= step_next_time:
            try:
                bf_interpreter.step()
                step_next_time = step_next_time + step_delay

            except BFRuntimeError as runtime_error:
                logging.warning(f"Program execution failed due to runtime error:\r\n\t{runtime_error}")

        # Update Screen Elements

        # Memory Pointer
        PTRRECT.left = CELL_INITIAL_X + bf_interpreter.ptr*(CELL_OFFSET + CELL_WIDTH)

        # Camera Position
        setCameraOffset(PTRRECT.left - SCREENRECT.width/2)
        updateCameraPosition(tick_time)

        # UI Elements

        if bf_interpreter.state == ProgramState.WaitingForInput and not readbyte_prompt_running:
            readbyte_prompt.setResponse("")
            readbyte_prompt_running = True

        # Render Screen
        screen.fill(rc.CLR_BLACK)

        # Render UI Elements
        hud_renderer.renderHud(screen, pg.Rect(50, 50, 0, 0), gs.step_hertz)

        if readbyte_prompt_running:
            readbyte_prompt.renderPrompt(screen, pg.Rect(100, 200, 400, 50))

        bf_renderer.render(screen, pg.Rect(50, 200, 0, 0), tick_time)

        # Flip the display      
        pg.display.flip()


# call the "main" function if running this script
if __name__ == "__main__":
    main()
    pg.quit()
