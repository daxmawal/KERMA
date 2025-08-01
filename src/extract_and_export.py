import sys
import os
import json
import shlex
import re
from clang import cindex


def extract_compile_args(source_file, compile_commands_path):
    if not os.path.exists(compile_commands_path):
        print(f"compile_commands.json not found at {compile_commands_path}")
        return []

    with open(compile_commands_path, "r") as f:
        compile_db = json.load(f)

    for entry in compile_db:
        try:
            if os.path.samefile(entry["file"], source_file):
                command = entry.get("command") or entry.get("arguments")
                if isinstance(command, str):
                    command = shlex.split(command)
                return [arg for arg in command if arg.startswith("-I") or arg.startswith("-D") or arg.startswith("-std")]
        except FileNotFoundError:
            continue

    print("No matching entry in compile_commands.json for this file.")
    return []


def find_function_and_includes(source_file, compile_commands_path, function_name):
    index = cindex.Index.create()
    compile_args = extract_compile_args(source_file, compile_commands_path)
    if not compile_args:
        compile_args = ["-std=c++17"]

    tu = index.parse(source_file, args=compile_args)

    includes = set()
    function_range = None
    namespace_stack = []
    class_name = None

    def visit(node):
        nonlocal function_range, class_name

        if node.kind == cindex.CursorKind.NAMESPACE:
            namespace_stack.append(node.spelling)

        if node.kind == cindex.CursorKind.CLASS_DECL and node.is_definition():
            class_name = node.spelling

        if node.kind in [cindex.CursorKind.CXX_METHOD, cindex.CursorKind.FUNCTION_DECL] and node.spelling == function_name:
            if node.is_definition():
                print(f"Definition of '{function_name}' found at {node.location.file}:{node.location.line}")
                function_range = (node.extent.start.line, node.extent.end.line)

                def collect_includes(n):
                    try:
                        if n.location.file and n.location.file.name.endswith(('.hpp', '.h')):
                            includes.add(n.location.file.name)
                        if n.type:
                            decl = n.type.get_declaration()
                            if decl and decl.location.file and decl.location.file.name.endswith(('.hpp', '.h')):
                                includes.add(decl.location.file.name)
                        if n.referenced and n.referenced.location.file and n.referenced.location.file.name.endswith(('.hpp', '.h')):
                            includes.add(n.referenced.location.file.name)
                    except:
                        pass
                    for child in n.get_children():
                        collect_includes(child)

                collect_includes(node)

        for child in node.get_children():
            visit(child)

        if node.kind == cindex.CursorKind.NAMESPACE:
            namespace_stack.pop()

    visit(tu.cursor)
    return function_range, includes, "::".join(namespace_stack), class_name


def extract_function_code(file_path, line_start, line_end):
    with open(file_path, "r") as f:
        lines = f.readlines()
    return "".join(lines[line_start - 1:line_end])


def generate_output(function_code, includes, namespace, class_name, function_name, output_path):
    with open(output_path, "w") as f:
        for inc in sorted(set(i for i in includes if i.endswith(('.h', '.hpp')))):
            f.write(f'#include "{os.path.basename(inc)}"\n')
        f.write("\n")

        if namespace:
            f.write(f"namespace {namespace} {{\n\n")

        if class_name:
            # Correction : transforme "Class::auto FunctionName" en "Class::ReturnType FunctionName"
            fixed_code = re.sub(
                rf"{re.escape(class_name)}::\s*auto\s+{re.escape(function_name)}",
                f"{class_name}::{function_name}",
                function_code
            )
            f.write(fixed_code.strip() + "\n")
        else:
            f.write(function_code.strip() + "\n")

        if namespace:
            f.write(f"\n}}  // namespace {namespace}\n")

    print(f"\nFunction extracted to {output_path}")


if __name__ == "__main__":
    if len(sys.argv) != 4:
        print("Usage: python extract_and_export.py <source.cpp> <compile_commands.json> <function_name>")
        sys.exit(1)

    source_path = sys.argv[1]
    compile_commands_path = sys.argv[2]
    target_function = sys.argv[3]

    if not os.path.exists(source_path):
        print(f"File not found: {source_path}")
        sys.exit(1)

    if not os.path.exists(compile_commands_path):
        print(f"compile_commands.json not found: {compile_commands_path}")
        sys.exit(1)

    function_range, includes, namespace, class_name = find_function_and_includes(
        source_path, compile_commands_path, target_function)

    if not function_range:
        print(f"Function '{target_function}' not found.")
        sys.exit(1)

    code = extract_function_code(source_path, *function_range)
    output_file = f"extracted_{target_function}.cpp"
    generate_output(code, includes, namespace, class_name, target_function, output_file)
