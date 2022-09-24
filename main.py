from distutils.log import debug
from turtle import heading
import pygame as pg
import os
import sys
import logging
import time
from src.bf import BFInterpreter, BFRuntimeError

# see if we can load more than standard BMP
if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")

# Constants
## Rendering Display
SCREENRECT = pg.Rect(0, 0, 640, 480)

## Cell Rendering Constants
CELL_INITIAL_X = 50
CELL_INITIAL_Y = 520
CELL_OFFSET = 25
CELL_WIDTH = 50

CELL_UNIT_HEIGHT = 25

## Pointer Rendering
PTRRECT = pg.Rect(0, CELL_INITIAL_Y+10, CELL_WIDTH, CELL_WIDTH)

## Some handy color references
CLR_WHITE = (255,255,255)
CLR_RED = (255,0,0)
CLR_GREEN = (0,255,0)
CLR_BLUE = (0,0,255)
CLR_BLACK = (0,0,0)

## Execution Control
STEP_HERTZ = 1
STEP_MAX_HERTZ = 32

## UI Control Values
UI_INIT_TOPLEFT = (20,20)

main_dir = os.path.split(os.path.abspath(__file__))[0]

def load_image(file):
    
    file = os.path.join(main_dir, "images", file)
    try:
        surface = pg.image.load(file)
    except pg.error:
        raise SystemExit(f'Could not load image "{file}" {pg.get_error()}')
    return surface.convert()


class Pointer(pg.sprite.Sprite):
    
    images = []

    def __init__(self):
        pg.sprite.Sprite.__init__(self, self.containers)
        self.image = self.images[0]
        self.rect = self.image.get_rect(midbottom=SCREENRECT.midbottom)
        self.reloading = 0
        self.origtop = self.rect.top
        self.facing = -1

def initPyGame():
    logging.info("Initializing PyGame")
    # Initialize pygame
    if pg.get_sdl_version()[0] == 2:
        pg.mixer.pre_init(44100, 32, 2, 1024)
    pg.init()
    if pg.mixer and not pg.mixer.get_init():
        logging.warning("Warning, no sound")
        pg.mixer = None

def initWindow(width = 800, height = 600) -> pg.Surface:
    global SCREENRECT

    SCREENRECT = pg.Rect(0, 0, width, height)
    winstyle = 0  # |FULLSCREEN
    bestdepth = pg.display.mode_ok(SCREENRECT.size, winstyle, 32)
    return pg.display.set_mode(SCREENRECT.size, winstyle, bestdepth)

def initLogging():
    logging.basicConfig(level=logging.INFO)

def setStepHz(step_hz: int, loop_on_overflow: bool = False):
    global STEP_HERTZ, STEP_MAX_HERTZ
    
    if step_hz < 1:
        step_hz = 1
    elif step_hz > STEP_MAX_HERTZ:
        if loop_on_overflow:
            step_hz = 1
        else:
            step_hz = STEP_MAX_HERTZ

    STEP_HERTZ = step_hz
    logging.info(f"Setting execution speed to {STEP_HERTZ}Hz.")


def incrementStepHz():
    setStepHz(step_hz=STEP_HERTZ * 2, loop_on_overflow=True)


def main(winstyle=0):
    # Load Command Line Arguments
    cmd_args = ""
    for arg in sys.argv:
        cmd_args = f"{cmd_args} {arg}"
    
    initLogging()
    logging.debug(cmd_args)

    # Init a BF program
    bf_interpreter = BFInterpreter(5, 16)
    bf_interpreter.setTape("+++++[->+++<]")

    # Init the engine and display window
    initPyGame()
    screen = initWindow(800,600)

    clock = pg.time.Clock()

    # Set up auto-execute values
    ## We always start with 1 op per second
    setStepHz(1)

    ## Set up the step execution values
    step_delay = 1.0/STEP_HERTZ
    step_next_time = time.time() + step_delay
    step_run = False

    # Set up state tracking
    last_state = bf_interpreter.state
    last_step_hz = STEP_HERTZ
    last_step_count = 0
    
    # Init the UI elements
    ui_font = pg.font.Font('freesansbold.ttf', 32)
    
    ui_hertz_text = ui_font.render(f"CPU: {STEP_HERTZ}Hz", True, CLR_WHITE, CLR_BLACK)
    ui_hertz_rect = ui_hertz_text.get_rect()
    
    ui_state_text = ui_font.render(f"State: {bf_interpreter.state._name_}", True, CLR_WHITE, CLR_BLACK)
    ui_state_rect = ui_state_text.get_rect()

    ui_step_count_text = ui_font.render(f"Step Count: {bf_interpreter.step_count}", True, CLR_WHITE, CLR_BLACK)
    ui_step_count_rect =  ui_step_count_text.get_rect()

    while True:
        # Hold Framerate to 30 fps
        clock.tick(40)     

        # Handle Input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return

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
                
                incrementStepHz()

                step_delay = 1.0/STEP_HERTZ
                step_next_time = time.time() + step_delay                

        
        keystate = pg.key.get_pressed()

        # Execute Instructions
        if step_run and not bf_interpreter.halted() and time.time() >= step_next_time:
            try:
                bf_interpreter.step()
                step_next_time = step_next_time + step_delay

            except BFRuntimeError as runtime_error:
                logging.warning(f"Program execution failed due to runtime error:\r\n\t{runtime_error}")

        # Update Screen Elements
        ## Memory Pointer
        PTRRECT.left = CELL_INITIAL_X + bf_interpreter.ptr*(CELL_OFFSET + CELL_WIDTH)
        
        ## UI Elements
        
        ### Regenerate the UI Hertz display if it has changed
        if last_step_hz != STEP_HERTZ:
            ui_hertz_text = ui_font.render(f"CPU: {STEP_HERTZ}Hz", True, CLR_WHITE, CLR_BLACK)
            ui_hertz_rect = ui_hertz_text.get_rect()
            last_step_hz = STEP_HERTZ

        ui_hertz_rect.topleft = UI_INIT_TOPLEFT
        
        ### Regenerate the state if it has changed
        if bf_interpreter.state != last_state:
            ui_state_text = ui_font.render(f"{bf_interpreter.state._name_}", True, CLR_WHITE, CLR_BLACK)
            ui_state_rect = ui_state_text.get_rect()
            last_state = bf_interpreter.state

        ui_state_rect.topleft = (ui_hertz_rect.left,ui_hertz_rect.bottom)
        
        ### Regenerate the step count if it has changed
        if bf_interpreter.step_count != last_step_count:
            ui_step_count_text = ui_font.render(f"Step Count: {bf_interpreter.step_count}", True, CLR_WHITE, CLR_BLACK)
            ui_step_count_rect =  ui_step_count_text.get_rect()
            last_step_count = bf_interpreter.step_count

        ui_step_count_rect.topleft = (ui_hertz_rect.left,ui_state_rect.bottom)

        # Render Screen
        screen.fill(CLR_BLACK)
        
        # Render UI Elements
        screen.blit(ui_hertz_text, ui_hertz_rect)
        screen.blit(ui_state_text, ui_state_rect)
        screen.blit(ui_step_count_text, ui_step_count_rect)

        # Render PC
        ptr_color = CLR_WHITE

        ## The program execution has completed
        if bf_interpreter.halted():
            ptr_color = CLR_RED
        
        ## The program is auto executing
        elif step_run:
            ptr_color = CLR_GREEN

        ## The program is paused
        else:
            ptr_color = CLR_BLUE

        pg.draw.polygon(
            surface=screen, 
            color=ptr_color,
            points=[
                PTRRECT.bottomleft, 
                (PTRRECT.centerx, PTRRECT.top),
                PTRRECT.bottomright])
        
        # Render Memory
        for i in range(0, len(bf_interpreter.memory)):
            height = bf_interpreter.memory[i] * CELL_UNIT_HEIGHT 
            
            # Draw cell reference base
            cell_base_rect = pg.Rect(CELL_INITIAL_X + i*(CELL_OFFSET + CELL_WIDTH), CELL_INITIAL_Y, CELL_WIDTH, 10)
            pg.draw.rect(screen, rect=cell_base_rect, color=(255,0,0))

            # Draw memory
            cell_rect = pg.Rect(CELL_INITIAL_X + i*(CELL_OFFSET + CELL_WIDTH), CELL_INITIAL_Y - height, CELL_WIDTH, height)
            pg.draw.rect(screen, rect=cell_rect, color=(255,255,255))
            
        # Flip the display
        pg.display.flip()
        

# call the "main" function if running this script
if __name__ == "__main__":
    main()
    pg.quit()