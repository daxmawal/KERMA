# KERMA (Kernel Extraction and Replay for Micro-Analysis)
 
KERMA is a small utility that extracts a single C++ function from an existing code base and writes it to its own `.cpp` file with the minimum set of `#include` directives. The project goal is to make micro benchmarks and focused debugging of complex code easier.

This enables:
 
- Isolated **performance profiling**
- Simplified **unit testing**
 
---

## Installation
 
1. Ensure your CMake project exports a `compile_commands.json` file:
 
```bash
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -B build
```

2. Install the required packages and Python bindings:
 
```bash
sudo apt install clang libclang-dev
pip install -r requirements.txt
```

---

### Usage
 
Run `extract_and_export.py` to isolate a single function:
 
```bash
python3 extract_and_export.py \
path/to/source.cpp \
path/to/compile_commands.json \
FunctionName
```
 
This will generate a new file, for example:
 
```bash
extracted_FunctionName.cpp
```

The produced file contains all necessary includes and the requested function so
that you can build and analyze it in isolation.
