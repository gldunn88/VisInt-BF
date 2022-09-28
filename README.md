# BF Visual Interpreter [1.0.0]

## Purpose

This Python Application is a visual interpreter for the [Brainfuck]() programming language. It is intended as a way to solve pointless problems in a useless language in a way that will not make your head explode. 

## Instructions

The intended use case is to prepare some set of data and environment values in advance via an *environment configuration file*, and supply a BF *source file* which will be executed against that environment. 

### Command Line Arguments

| Short | Long | Effect |
| --- | --- | --- |
| -v | --verbose | Sets logging to *DEBUG* for in depth execution information |
| -s | --src-file | Specifies a file containing a BF program |
| -e | --env-file | Specifies a file defining the environment the BF program will execute within. If not specified will default to 8 cells with a maximum value of 16 |

### Source Files

Source files must be in restricted BF format, containing only the following characters: 

```
+-><[].,
```

- No whitespaces, newlines, or other characters are accepted in this version.
- The character ',' has not been implemented. Inputs cannot be provided during execution

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

