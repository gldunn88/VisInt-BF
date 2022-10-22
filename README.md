# BF Visual Interpreter [1.0.0]

## Purpose

This Python Application is a visual interpreter for the [Brainfuck](https://en.wikipedia.org/wiki/Brainfuck) programming language. It is intended as a way to solve pointless problems in a useless language in a way that will not make your head explode. Because if you gamify something horrible and useless, you get something tolerable and useless.

### Notes

- The ultimate goal is to set *challenges* by providing and initial memory set and a expected results. 
- The user(see: [masochist](https://en.wikipedia.org/wiki/Masochism_(disambiguation))) then provides the program to transition from the initial to target states when the program halts.
- At this point you need to make a goal on your own and provide your own critique

## Instructions

This interpreter takes its initial memory layout and instruction set from command line values, and runs them through what is hopefully a reasonable-ish user interface. This section defines available inputs and controls.

### Command Line Arguments

| Short | Long | Effect |
| --- | --- | --- |
| -v | --verbose | Sets logging to *DEBUG* for in depth execution information. |
| -s | --src-file | **REQUIRED** Specifies a file containing a BF program source file. |
| -e | --env-file | Specifies a file defining the environment the BF program will execute within. If not specified will default to 8 cells with a maximum value of 16 |

### Source Files

Source files must be in restricted BF format, containing only the following characters. If you wanted comments and easy readability, I have to question your judgement in learning this particular lenguage. 

In seriousness, this is a concious choice to facilitate future additions for the [Brain Function](https://github.com/ryanfox/brainfunction) extensions.

`+-><[].,`

#### Notes

- No whitespaces, newlines, or other characters are accepted in this version.
- The character ',' will prompt for user input in the visualizer
- The character '.' will print the value of the current cell to the console regardless of verbosity. 
    - There is a planned update to display this to the screen in a popup for full visual support

### Environment Configurations

The environment configurations are provided by JSON files. All of the tags must be included. Several samples are shown below for reference.

An environment with:
- 4 cells
- Max value per cell of 24
- All cell values set to 3 at the start

```json
{
    "version": "1",
    "memory": {
        "cell_count": 4,
        "cell_max_value": 24,
        "cell_default_value": 3,
        "cell_initial_values": []
    }
}
```

An environment with:
- 8 cells
- Max value per cell of 16
- All unspecified cell values set to 0 at the start
- The first six values are set to the sequence 1,2,3,4,5,6

```json
{
    "version": "1",
    "memory": {
        "cell_count": 8,
        "cell_max_value": 16,
        "cell_default_value": 0,
        "cell_initial_values": [1,2,3,4,5,6]
    }
}
```

### Sample Executions

Specifying all values with detailed outputs.

```ps1
VisInt> python.exe .\main.py -s "samples/prg_1.bf" -e "samples/env_1.json" --verbose
VisInt> python.exe .\main.py --src-file "samples/prg_1.bf" --env-file "samples/env_1.json" --verbose
```

Executing *samples/prg_1.bf* in the default environment.

```ps1
VisInt> python.exe .\main.py -s "samples/prg_1.bf"
```

### Controls

In the interpreter itself, there are a few controls you have during program execution.

#### Execution Speed

| Control | Effect | Detail |
| --- | --- | --- |
| Spacebar | Toggle Pause | The interpreter starts *Paused*. You must press spacebar to begin running the Brainfuck program |
| Tab | Increment Execution Speed | Pressing *TAB* will double the instructions per second speed. It will go from 1HZ to a maximum of 32 HZ, before rolling over back to 1 HZ. |

#### Entering values on Prompt

Entering cell values via the `,` command is supported by an on-screen prompt. When the interpreter executes this command the execution will pause until a number in the allowed value range (0 -> maximum value, default 16) is entered. Once entered the current cell will be assigned that value provided.

Entering an illegal value (outside of the allowed range) will result in a program execution error.