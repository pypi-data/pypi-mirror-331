# PyFunc Logger - Quick Start Guide

## Installation

### Option 1: Copy the package

Simply copy the `pyfunc_logger` directory to your project.

### Option 2: Install using pip

```bash
# From the directory containing setup.py
pip install .

# Or directly from GitHub
pip install git+https://github.com/yourusername/pyfunc_logger.git
```

## Basic Usage

### Step 1: Import the decorator

```python
from pyfunc_logger import log_function
```

### Step 2: Decorate your functions

```python
@log_function
def my_function(x, y):
    return x + y
```

### Step 3: Use your functions normally

```python
result = my_function(10, 20)
```

That's it! The logger will automatically:
- Record when the function starts and ends
- Track function arguments
- Measure execution time
- Capture return values
- Log everything to a CSV file

## Finding your logs

Logs are saved in the `func_logs` directory by default (created in the current working directory).

Each log file is named with a timestamp: `func_log_YYYYMMDD_HHMMSS.csv`

## Viewing log files

You can:
1. Open the CSV file directly in Excel, Google Sheets, or similar
2. Use the provided analysis script: `python examples/analyze_logs.py`
3. Write your own analysis script using pandas or other tools

## Example output

The analyze_logs.py script provides the following insights:

```
SUMMARY STATISTICS:
Total function calls: 9
Successful calls: 8
Errored calls: 1

FUNCTION TIMING ANALYSIS:
Function Name             Calls    Min (ms)   Max (ms)   Avg (ms)   Errors  
---------------------------------------------------------------------------
add                       2        0.06       0.11       0.09       0       
complex_calculation       1        300.38     300.38     300.38     0       
concatenate_strings       1        0.05       0.05       0.05       0       
multiply                  2        0.05       0.07       0.06       0       
process_large_data        1        503.36     503.36     503.36     0       
risky_function            2        0.05       0.11       0.08       1       

POTENTIAL BOTTLENECKS:
- process_large_data: max time 503.36ms, called 1 times
- complex_calculation: max time 300.38ms, called 1 times
```

## Next Steps

See the full README.md for more detailed information on configuration options, advanced usage, and performance considerations.
