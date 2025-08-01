import json
import os
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.extract_and_export import (
    extract_compile_args,
    extract_function_code,
    find_function_and_includes,
    generate_output,
)


def test_extract_compile_args(tmp_path):
    source = tmp_path / "main.cpp"
    source.touch()
    compile_commands = [
        {
            "directory": str(tmp_path),
            "command": f"clang++ -I{tmp_path}/include -DDEBUG -std=c++20 {source}",
            "file": str(source),
        }
    ]
    path = tmp_path / "compile_commands.json"
    path.write_text(json.dumps(compile_commands))

    args = extract_compile_args(str(source), str(path))
    assert f"-I{tmp_path}/include" in args
    assert "-DDEBUG" in args
    assert "-std=c++20" in args


def test_extract_function_code(tmp_path):
    code = """\nint func() {\n    return 42;\n}\n"""
    file = tmp_path / "sample.cpp"
    file.write_text(code)

    result = extract_function_code(str(file), 2, 4)
    assert result.strip().startswith("int func()")
    assert "return 42" in result


def test_generate_output(tmp_path):
    function_code = "auto Bar::add(int a, int b) -> int {\n return a + b;\n}\n"
    output = tmp_path / "out.cpp"
    generate_output(
        function_code, {"/path/to/foo.h"}, "ns", "Bar", "add", str(output)
    )

    content = output.read_text()
    assert '#include "foo.h"' in content
    assert "namespace ns" in content
    assert "auto Bar::add" in content
    assert "}  // namespace ns" in content


def test_find_function_and_includes(tmp_path):
    header = tmp_path / "foo.h"
    header.write_text("int foo();\n")

    source_lines = [
        '#include "foo.h"',
        "namespace ns {",
        "class Bar {",
        "public:",
        "    int add(int a, int b) {",
        "        return foo() + a + b;",
        "    }",
        "};",
        "}",
    ]
    source = tmp_path / "sample.cpp"
    source.write_text("\n".join(source_lines))

    compile_commands = [
        {
            "directory": str(tmp_path),
            "command": f"clang++ -std=c++17 -I{tmp_path} {source}",
            "file": str(source),
        }
    ]
    cc_path = tmp_path / "compile_commands.json"
    cc_path.write_text(json.dumps(compile_commands))

    function_range, includes, namespace, class_name = (
        find_function_and_includes(str(source), str(cc_path), "add")
    )

    assert function_range == (5, 7)
    assert any(os.path.basename(inc) == "foo.h" for inc in includes)
    assert class_name == "Bar"
    assert namespace == ""
