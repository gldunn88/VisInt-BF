from distutils.log import debug
from turtle import heading
import pygame as pg
import os
import sys
import logging
from src.bf import BFInterpreter, ProgramState

# see if we can load more than standard BMP
if not pg.image.get_extended():
    raise SystemExit("Sorry, extended image module required")

# Constants
## Rendering Display
SCREENRECT = pg.Rect(0, 0, 640, 480)

## Cell Rendering Constants
INITIAL_CELL_X = 50
INITIAL_CELL_Y = 520
CELL_OFFSET = 25
CELL_WIDTH = 50

CELL_UNIT_HEIGHT = 25

## Pointer Rendering
PTRRECT = pg.Rect(0, INITIAL_CELL_Y+10, CELL_WIDTH, CELL_WIDTH)

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


def main(winstyle=0):

    # Load Command Line Arguments
    cmd_args = ""
    for arg in sys.argv:
        cmd_args = f"{cmd_args} {arg}"
    
    print(cmd_args)

    # Init a BF program
    bf_interpreter = BFInterpreter(5, 8)
    bf_interpreter.setTape("+>++>+++>++++>+++++")

    # Init the engine and display window
    initPyGame()
    screen = initWindow(800,600)

    clock = pg.time.Clock()

    # Load Images

    ## Load PTR
    ptr_img = load_image("ptr.png")
    ptr_img = pg.transform.scale(ptr_img, (PTRRECT.width, PTRRECT.height))
    Pointer.images = [ptr_img, pg.transform.flip(ptr_img, 1, 0)]

    all = pg.sprite.Group()
    Pointer.containers = all

    ptr = Pointer()
    
    while True:
        # Hold Framerate
        clock.tick(40)     

        # Handle Input
        for event in pg.event.get():
            if event.type == pg.QUIT:
                return
            if event.type == pg.KEYDOWN and event.key == pg.K_ESCAPE:
                return
            if event.type == pg.KEYUP and event.key == pg.K_SPACE:
                logging.debug("Manually Stepping Program")
                bf_interpreter.step()

        keystate = pg.key.get_pressed()

        # Update Screen Elements
        PTRRECT.left = INITIAL_CELL_X + bf_interpreter.ptr*(CELL_OFFSET + CELL_WIDTH)

        # Render Screen
        screen.fill((0,0,0))
        
        pg.draw.polygon(
            surface=screen, 
            color=(255,255,255),
            points=[
                PTRRECT.bottomleft, 
                (PTRRECT.centerx, PTRRECT.top),
                PTRRECT.bottomright])
        
        # Render Memory
        for i in range(0, len(bf_interpreter.memory)):
            height = bf_interpreter.memory[i] * CELL_UNIT_HEIGHT 
            
            # Draw cell reference base
            cell_base_rect = pg.Rect(INITIAL_CELL_X + i*(CELL_OFFSET + CELL_WIDTH), INITIAL_CELL_Y, CELL_WIDTH, 10)
            pg.draw.rect(screen, rect=cell_base_rect, color=(255,0,0))

            # Draw memory
            cell_rect = pg.Rect(INITIAL_CELL_X + i*(CELL_OFFSET + CELL_WIDTH), INITIAL_CELL_Y - height, CELL_WIDTH, height)
            pg.draw.rect(screen, rect=cell_rect, color=(255,255,255))
            

        # cap the framerate at 40fps. Also called 40HZ or 40 times per second.
        pg.display.flip()
        

# call the "main" function if running this script
if __name__ == "__main__":
    main()
    pg.quit()