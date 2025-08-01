# KERMA (Kernel Extraction and Replay for Micro-Analysis)

**KERMA** is a tool for automatically extracting C++ functions (or class methods) from source files into standalone `.cpp` files with their minimal required dependencies (`#include` directives).  
This enables:

- Isolated **performance profiling**
- Simplified **unit testing**
- Easy **reduction of complex cases**

---

## Prerequisites

### Build with `compile_commands.json`

Make sure your CMake project generates a `compile_commands.json` file:

```bash
cmake -DCMAKE_EXPORT_COMPILE_COMMANDS=ON -B build
```

#### Dependencies

Install required system packages and Python bindings:

```bash
sudo apt install clang libclang-dev
pip install libclang
```

##### Usage

Run the following command to extract a function:

```bash
python3 extract_and_export.py \
  path/to/source.cpp \
  path/to/compile_commands.json \
  FunctionName
```

This will generate a file like:

```bash
extracted_ServerIsLive.cpp
```