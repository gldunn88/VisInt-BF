import pytest

from src.bf import BFCommand, BFInitError, BFInterpreter, BFRuntimeError, ProgramState


# Groups tests related to initialization of a BF Interpreter
class TestBFInit:

    def test_initialization(self):
        interpreter = BFInterpreter(5)
        interpreter.setTape("+++")

        assert interpreter.ptr == 0
        assert interpreter.pc == 0
        assert interpreter.state == ProgramState.Ready
        for cell in interpreter.memory:
            assert cell == 0

    def test_setTape(self):
        interpreter = BFInterpreter(1)
        interpreter.setTape("+-<>[].,")
        print(interpreter.tapeString())

        assert len(interpreter.tape) == len("+-<>[].,")
        assert interpreter.tape[0] == BFCommand.Increment
        assert interpreter.tape[1] == BFCommand.Decrement
        assert interpreter.tape[2] == BFCommand.CellPtrLeft
        assert interpreter.tape[3] == BFCommand.CellPtrRight
        assert interpreter.tape[4] == BFCommand.StartWhile
        assert interpreter.tape[5] == BFCommand.EndWhile
        assert interpreter.tape[6] == BFCommand.PrintByte
        assert interpreter.tape[7] == BFCommand.ReadByte

    def test_init_memory_size_error(self):

        with pytest.raises(BFInitError):
            BFInterpreter(0)

    def test_init_max_value_error(self):

        with pytest.raises(BFInitError):
            BFInterpreter(1, 0)

    def test_init_empty_tape_error(self):

        with pytest.raises(BFInitError):
            BFInterpreter(1).setTape("")


# Groups tests related to execution of a BF Interpreter
class TestBFRuntime:

    def test_step_to_halt(self):
        interpreter = BFInterpreter(1)
        interpreter.setTape("+++")

        assert interpreter.pc == 0
        assert interpreter.state == ProgramState.Ready

        interpreter.step()

        assert interpreter.pc == 1
        assert interpreter.state == ProgramState.Running

        interpreter.step()

        assert interpreter.pc == 2
        assert interpreter.state == ProgramState.Running

        interpreter.step()

        assert interpreter.pc == 3
        assert interpreter.state == ProgramState.Halted

    def test_pointer_commands(self):
        interpreter = BFInterpreter(2)
        interpreter.setTape("><")

        assert interpreter.ptr == 0
        interpreter.step()
        assert interpreter.ptr == 1
        interpreter.step()
        assert interpreter.ptr == 0

    def test_increment_decrement_commands(self):
        interpreter = BFInterpreter(1)
        interpreter.setTape("+-")

        assert interpreter.memory[interpreter.ptr] == 0
        interpreter.step()
        assert interpreter.memory[interpreter.ptr] == 1
        interpreter.step()
        assert interpreter.memory[interpreter.ptr] == 0

    def test_simple_loop_commands(self):
        interpreter = BFInterpreter(1)
        interpreter.setTape("+[-]")

        assert interpreter.pc == 0

        interpreter.step()
        assert interpreter.pc == 1

        interpreter.step()
        assert interpreter.pc == 2

        interpreter.step()
        assert interpreter.pc == 3

        interpreter.step()
        assert interpreter.pc == 1

        interpreter.step()
        assert interpreter.pc == 4
        assert interpreter.state == ProgramState.Halted

    def test_nested_loop_commands(self):
        interpreter = BFInterpreter(1)
        interpreter.setTape("+[[-]]")

        assert interpreter.pc == 0

        interpreter.step()
        assert interpreter.pc == 1

        interpreter.step()
        assert interpreter.pc == 2

        interpreter.step()
        assert interpreter.pc == 3

        interpreter.step()
        assert interpreter.pc == 4

        interpreter.step()
        assert interpreter.pc == 2

        interpreter.step()
        assert interpreter.pc == 5

        interpreter.step()
        assert interpreter.pc == 1

        interpreter.step()
        assert interpreter.pc == 6
        assert interpreter.state == ProgramState.Halted

    def test_runtime_underflow_error(self):
        interpreter = BFInterpreter(1)
        interpreter.setTape("-")

        with pytest.raises(BFRuntimeError):
            interpreter.step()

    def test_runtime_overflow_error(self):
        interpreter = BFInterpreter(1, 1)
        interpreter.setTape("++")

        with pytest.raises(BFRuntimeError):
            interpreter.step()
            interpreter.step()

    def test_runtime_ptr_less_than_zero_error(self):
        interpreter = BFInterpreter(1)
        interpreter.setTape("<")

        with pytest.raises(BFRuntimeError):
            interpreter.step()

    def test_runtime_ptr_out_of_bounds_error(self):
        interpreter = BFInterpreter(1)
        interpreter.setTape(">")

        with pytest.raises(BFRuntimeError):
            interpreter.step()

    def test_runtime_step_after_halt_error(self):
        interpreter = BFInterpreter(1)
        interpreter.setTape("+")

        interpreter.step()

        with pytest.raises(BFRuntimeError):
            interpreter.step()

    def test_runtime_step_after_error_error(self):
        interpreter = BFInterpreter(1)
        interpreter.setTape("+")

        interpreter.step()

        # Initial Error
        with pytest.raises(BFRuntimeError):
            interpreter.step()

        # Error caused by trying to step again
        with pytest.raises(BFRuntimeError):
            interpreter.step()

    def test_setMemory_defaults_only(self):
        interpreter = BFInterpreter(8, 16)
        interpreter.setMemory(values=[], default=0)

        assert len(interpreter.memory) == 8
        for cell in interpreter.memory:
            assert cell == 0

    def test_setMemory_initialized_and_default(self):
        interpreter = BFInterpreter(8, 16)
        interpreter.setMemory(values=[1, 2, 3, 4], default=8)

        assert len(interpreter.memory) == 8
        assert interpreter.memory[0] == 1
        assert interpreter.memory[1] == 2
        assert interpreter.memory[2] == 3
        assert interpreter.memory[3] == 4

        for i in range(4, len(interpreter.memory)):
            assert interpreter.memory[i] == 8

    def test_setMemory_fully_initialized(self):
        interpreter = BFInterpreter(8, 16)
        interpreter.setMemory(values=[1, 2, 3, 4, 5, 6, 7, 8], default=0)

        assert len(interpreter.memory) == 8
        assert interpreter.memory[0] == 1
        assert interpreter.memory[1] == 2
        assert interpreter.memory[2] == 3
        assert interpreter.memory[3] == 4
        assert interpreter.memory[4] == 5
        assert interpreter.memory[5] == 6
        assert interpreter.memory[6] == 7
        assert interpreter.memory[7] == 8

    def test_setMemory_negative_default_error(self):
        interpreter = BFInterpreter(8, 16)
        with pytest.raises(BFInitError):
            interpreter.setMemory(values=[], default=-1)

    def test_setMemory_large_default_error(self):
        interpreter = BFInterpreter(8, 16)
        with pytest.raises(BFInitError):
            interpreter.setMemory(values=[], default=17)

    def test_setMemory_long_values_error(self):
        interpreter = BFInterpreter(8, 16)
        with pytest.raises(BFInitError):
            interpreter.setMemory(values=[1, 2, 3, 4, 5, 6, 7, 8, 9], default=0)

    def test_setMemory_negative_values_error(self):
        interpreter = BFInterpreter(8, 16)
        with pytest.raises(BFInitError):
            interpreter.setMemory(values=[1, -1], default=0)

    def test_setMemory_large_values_error(self):
        interpreter = BFInterpreter(8, 16)
        with pytest.raises(BFInitError):
            interpreter.setMemory(values=[1, 17], default=0)

    def test_readByte_success_readLastStep(self):
        interpreter = BFInterpreter(8, 16)
        interpreter.setMemory([], 0)
        interpreter.setTape(",")

        interpreter.step()
        assert interpreter.state == ProgramState.WaitingForInput
        assert interpreter.pc == 0
        assert interpreter.memory[interpreter.ptr] == 0

        interpreter.readByte(5)
        interpreter.state == ProgramState.Halted
        assert interpreter.pc == 1
        assert interpreter.memory[interpreter.ptr] == 5

    def test_readByte_success_stepAfterInput(self):
        interpreter = BFInterpreter(8, 16)
        interpreter.setMemory([], 0)
        interpreter.setTape(",")

        interpreter.step()
        assert interpreter.state == ProgramState.WaitingForInput
        assert interpreter.pc == 0
        assert interpreter.memory[interpreter.ptr] == 0

        interpreter.readByte(5)
        interpreter.state == ProgramState.Running
        assert interpreter.pc == 1
        assert interpreter.memory[interpreter.ptr] == 5

    def test_readByte_error_readyStatus(self):
        interpreter = BFInterpreter(8, 16)
        interpreter.setMemory([], 0)
        interpreter.setTape("++")

        assert interpreter.state == ProgramState.Ready
        with pytest.raises(BFRuntimeError):
            interpreter.readByte(0)

    def test_readByte_error_runningStatus(self):
        interpreter = BFInterpreter(8, 16)
        interpreter.setMemory([], 0)
        interpreter.setTape("++")

        interpreter.step()
        assert interpreter.state == ProgramState.Running
        with pytest.raises(BFRuntimeError):
            interpreter.readByte(0)

    def test_readByte_error_haltedStatus(self):
        interpreter = BFInterpreter(8, 16)
        interpreter.setMemory([], 0)
        interpreter.setTape("+")

        interpreter.step()
        assert interpreter.state == ProgramState.Halted
        with pytest.raises(BFRuntimeError):
            interpreter.readByte(0)

    def test_halted(self):
        interpreter = BFInterpreter(8, 16)
        interpreter.setMemory([], 0)
        interpreter.setTape(",+")

        assert interpreter.state == ProgramState.Ready
        assert not interpreter.halted()

        interpreter.step()

        assert interpreter.state == ProgramState.WaitingForInput
        assert not interpreter.halted()

        interpreter.readByte(5)
        assert interpreter.state == ProgramState.Running
        assert not interpreter.halted()

        interpreter.step()
        assert interpreter.state == ProgramState.Halted
        assert interpreter.halted()

        with pytest.raises(BFRuntimeError):
            interpreter.step()

        assert interpreter.state == ProgramState.Error
        assert interpreter.halted()

    def test_waitingForInput(self):
        interpreter = BFInterpreter(8, 16)
        interpreter.setMemory([], 0)
        interpreter.setTape(",+")

        assert interpreter.state == ProgramState.Ready
        assert not interpreter.waitingForInput()

        interpreter.step()

        assert interpreter.state == ProgramState.WaitingForInput
        assert interpreter.waitingForInput()

        interpreter.readByte(5)
        assert interpreter.state == ProgramState.Running
        assert not interpreter.waitingForInput()

        interpreter.step()
        assert interpreter.state == ProgramState.Halted
        assert not interpreter.waitingForInput()

        with pytest.raises(BFRuntimeError):
            interpreter.step()

        assert interpreter.state == ProgramState.Error
        assert not interpreter.waitingForInput()

    def test_canStep(self):
        interpreter = BFInterpreter(8, 16)
        interpreter.setMemory([], 0)
        interpreter.setTape(",+")

        assert interpreter.state == ProgramState.Ready
        assert interpreter.canStep()

        interpreter.step()

        assert interpreter.state == ProgramState.WaitingForInput
        assert not interpreter.canStep()

        interpreter.readByte(5)
        assert interpreter.state == ProgramState.Running
        assert interpreter.canStep()

        interpreter.step()
        assert interpreter.state == ProgramState.Halted
        assert not interpreter.canStep()

        with pytest.raises(BFRuntimeError):
            interpreter.step()

        assert interpreter.state == ProgramState.Error
        assert not interpreter.canStep()
