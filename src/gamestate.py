class Gamestate():

    maxHertz = 32
    minHertz = 1

    def __init__(self, step_hertz: int):

        self.step_hertz = step_hertz

    def setStepHertz(self, step_hertz: int, loop_on_overflow: bool = False, loop_on_underflow: bool = False):

        self.step_hertz = step_hertz

        if self.step_hertz < self.minHertz:
            if loop_on_underflow:
                self.step_hertz = self.maxHertz
            else:
                self.step_hertz = self.minHertz
        elif self.step_hertz > self.maxHertz:
            if loop_on_overflow:
                self.step_hertz = self.minHertz
            else:
                self.step_hertz = self.maxHertz

    def multiplyStepHertz(self, factor: float = 2.0, loop: bool = True):
        self.setStepHertz(int(self.step_hertz * factor), loop_on_overflow=loop, loop_on_underflow=loop)

    def incrementStepHertz(self, increment: int = 1, loop: bool = True):
        self.setStepHertz(self.step_hertz + increment, loop_on_overflow=loop, loop_on_underflow=loop)
