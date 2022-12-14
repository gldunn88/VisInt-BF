import logging

from enum import Enum


class BFInitError(Exception):
    pass


class BFRuntimeError(Exception):
    pass


class BFCommand(Enum):
    Increment = 1
    Decrement = 2
    CellPtrLeft = 3
    CellPtrRight = 4
    StartWhile = 5
    EndWhile = 6
    ReadByte = 7
    PrintByte = 8


def StringToBFCommand(cmd):
    if cmd == "<":
        return BFCommand.CellPtrLeft
    elif cmd == ">":
        return BFCommand.CellPtrRight
    elif cmd == "+":
        return BFCommand.Increment
    elif cmd == "-":
        return BFCommand.Decrement
    elif cmd == "[":
        return BFCommand.StartWhile
    elif cmd == "]":
        return BFCommand.EndWhile
    elif cmd == ".":
        return BFCommand.PrintByte
    elif cmd == ",":
        return BFCommand.ReadByte


def BFCommandToString(cmd):
    if cmd == BFCommand.CellPtrLeft:
        return "<"
    elif cmd == BFCommand.CellPtrRight:
        return ">"
    elif cmd == BFCommand.Increment:
        return "+"
    elif cmd == BFCommand.Decrement:
        return "-"
    elif cmd == BFCommand.StartWhile:
        return "["
    elif cmd == BFCommand.EndWhile:
        return "]"
    elif cmd == BFCommand.PrintByte:
        return "."
    elif cmd == BFCommand.ReadByte:
        return ","


class ProgramState(Enum):
    Ready = 0,
    Running = 1
    WaitingForInput = 2
    Halted = 3
    Error = 4


class BFInterpreter():

    def __init__(self, memory_size: int, max_value: int = 256):

        if memory_size < 1:
            self.raiseInitError("Memory must be at least 1 cell")

        if max_value < 1:
            self.raiseInitError("Maximum cell value must be at least 1")

        self.state: ProgramState = ProgramState.Ready
        self.stateDetail: str = ""

        self.ptr: int = 0
        self.pc: int = 0

        self.tape: list = []
        self.whileStack: list = []

        self.max_value: int = max_value
        self.memory: list = [0] * memory_size

        self.step_count: int = 0

    def setMemory(self, values: list = [], default: int = 0):

        # Validate that the provided values are legal
        if len(values) > len(self.memory):
            self.raiseInitError(f"Attempting to initialize {len(values)} in memory size {len(self.memory)}")

        for i in range(0, len(values)):
            if type(values[i]) is not int or values[i] < 0 or values[i] > self.max_value:
                self.raiseInitError(f"Attempting to initialize memory to illegal inital value: {values[i]}. Must be integer in range 0-> {self.max_value}") # noqa

        if default < 0 or default > self.max_value:
            self.raiseInitError(f"Attempting to initialize memory to illegal default value: {default}. Must be integer in range 0-> {self.max_value}") # noqa

        logging.debug(f"Setting memory to initial values: \r\n\t{values}\r\nDefault Value for Remaining Values: {default}") # noqa

        # Assign memory, setting default after initial values are exhausted
        for i in range(0, len(self.memory)):
            if i < len(values):
                self.memory[i] = values[i]
            else:
                self.memory[i] = default

        logging.debug(f"Memory after initialization:\r\n\t{self.memory}")

    def setTape(self, program: str):
        if len(program) == 0:
            self.raiseInitError("Tape must contain at least one symbol")
        self.tape = []
        for cmd in program:
            self.appendTape(cmd)

    def appendTape(self, cmd: str):
        self.tape.append(StringToBFCommand(cmd))

    def halted(self) -> bool:
        return self.state in [ProgramState.Error, ProgramState.Halted]

    def waitingForInput(self) -> bool:
        return self.state in [ProgramState.WaitingForInput]

    def canStep(self) -> bool:
        return not (self.halted() or self.waitingForInput())

    def raiseRuntimeError(self, message):
        self.state = ProgramState.Error
        self.stateDetail = message
        logging.warning(f"BF Runtime Error: {message}")
        raise BFRuntimeError(message)

    def raiseInitError(self, message):
        self.state = ProgramState.Error
        self.stateDetail = message
        logging.warning(f"BF Initialization Error: {message}")
        raise BFInitError(message)

    def step(self):
        cmd: BFCommand

        # Kick off program execution
        if self.state == ProgramState.Ready:
            self.state = ProgramState.Running

        logging.debug(self.tapeString())
        logging.debug(self.memoryString())

        if self.state in [ProgramState.Error, ProgramState.Halted, ProgramState.WaitingForInput]:
            self.raiseRuntimeError(f"Attempting to step program in state {self.state._name_}")

        cmd = self.tape[self.pc]

        # These commands process, then increment the program counter
        if cmd in [BFCommand.CellPtrLeft,
                   BFCommand.CellPtrRight,
                   BFCommand.Increment,
                   BFCommand.Decrement,
                   BFCommand.PrintByte]:
            if cmd == BFCommand.CellPtrLeft:
                self.ptr -= 1
                if self.ptr < 0:
                    self.raiseRuntimeError(f"Memory pointer less than 0 at command {self.pc}")

            elif cmd == BFCommand.CellPtrRight:
                self.ptr += 1
                if self.ptr >= len(self.memory):
                    self.raiseRuntimeError(
                        f"Memory pointer out of bounds at command {self.pc}. Maximum allowed: {len(self.memory)-1}")

            elif cmd == BFCommand.Increment:
                self.memory[self.ptr] += 1
                if self.memory[self.ptr] > self.max_value:
                    self.raiseRuntimeError(f"Cell Overflow at command {self.pc}: Maximum value {self.max_value}")

            elif cmd == BFCommand.Decrement:
                self.memory[self.ptr] -= 1
                if self.memory[self.ptr] < 0:
                    self.raiseRuntimeError(f"Cell Underflow at command {self.pc}. Minimum value 0")

            elif cmd == BFCommand.PrintByte:
                print(format(f"Cell[{self.ptr}]: {self.memory[self.ptr]}"))

            # Read the next command
            self.pc += 1

        # These commands affect program execution by shifting the program counter
        elif cmd in [BFCommand.StartWhile, BFCommand.EndWhile]:
            if cmd == BFCommand.StartWhile:
                loopEnd = self.findLoopEnd()
                if loopEnd < 0:
                    self.raiseRuntimeError(f"No close found for loop start at command {self.pc}")

                # If the current value is 0, skip to end of loop
                else:
                    if self.memory[self.ptr] == 0:
                        self.pc = loopEnd + 1
                    else:
                        self.whileStack.append(self.pc)
                        self.pc += 1

            elif cmd == BFCommand.EndWhile:
                if len(self.whileStack) == 0:
                    self.raiseRuntimeError(f"End of loop with no matching start at command {self.pc}")

                else:
                    # Return to the start of the loop to reassess
                    self.pc = self.whileStack.pop()

        elif cmd in [BFCommand.ReadByte]:
            self.state = ProgramState.WaitingForInput
            logging.info("Waiting for User Input")

        # Detect end of program
        if self.pc >= len(self.tape):
            self.state = ProgramState.Halted
            self.stateDetail = "End of Tape"

        self.step_count += 1

    def readByte(self, value: int):
        if self.state != ProgramState.WaitingForInput:
            raise self.raiseRuntimeError(f"Attempting to accept user input in state {self.state._name_}")

        if value < 0 or value > self.max_value:
            raise self.raiseRuntimeError(f"Provided byte input ({value}) must be in the range 0 -> {self.max_value}")

        self.memory[self.ptr] = value

        # Increment the program counter and reset to steppable state
        self.state = ProgramState.Running
        self.pc += 1

        # Detect end of program
        if self.pc >= len(self.tape):
            self.state = ProgramState.Halted
            self.stateDetail = "End of Tape"

    def findLoopEnd(self) -> int:

        # Only attempt at an actual while start
        if (self.tape[self.pc] != BFCommand.StartWhile):
            return -2

        # Once the offset counterv reaches zero, the test_pc will be at the tape location for the while group end
        test_pc = self.pc
        offsetCounter = 1
        while offsetCounter > 0:
            test_pc += 1

            # End of tape is reached without finding matching closing command
            if test_pc >= len(self.tape):
                break

            # Update the the paren tracker based on the commands
            # Any non-loop command is ignored
            cmd = self.tape[test_pc]
            if cmd == BFCommand.EndWhile:
                offsetCounter -= 1
            elif cmd == BFCommand.StartWhile:
                offsetCounter += 1

        # The current while start at self.pc does not have a close
        if offsetCounter > 0:
            return -1

        return test_pc

    def tapeString(self):
        ret = "Tape: "
        for i in range(0, len(self.tape)):
            if i == self.pc:
                ret = format(f"{ret} ({BFCommandToString(self.tape[i])})")
            else:
                ret = format(f"{ret} {BFCommandToString(self.tape[i])}")

        if self.pc >= len(self.tape):
            ret = format(f"{ret} (HALT)")
        else:
            ret = format(f"{ret} HALT")
        return ret

    def memoryString(self):
        ret = "Memory Map: "
        for i in range(0, len(self.memory)):
            if i == self.ptr:
                ret = format(f"{ret} ({self.memory[i]})")
            else:
                ret = format(f"{ret} {self.memory[i]}")
        return ret
