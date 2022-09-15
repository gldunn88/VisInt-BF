import logging
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
            BFInterpreter(1,0)

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