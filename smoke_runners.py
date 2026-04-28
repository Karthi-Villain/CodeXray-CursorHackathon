"""Smoke-test the new JS + Java auto-test runners without calling Cursor.

Builds a fake `test_cases` payload that mimics what the Cursor agent would
return, then exercises:
- build_pytest_file + run_pytest        (existing path, regression check)
- build_node_test_file + run_node_test  (new)
- build_java_test_file + run_java_test  (new — gracefully falls back if the
  JDK isn't installed)
"""

from __future__ import annotations

import json
import os
import shutil
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from app import (  # noqa: E402
    TEST_FOLDER,
    build_java_test_file,
    build_node_test_file,
    build_pytest_file,
    run_java_test,
    run_node_test,
    run_pytest,
)


def hr(title: str) -> None:
    print()
    print("=" * 60)
    print(title)
    print("=" * 60)


def smoke_python() -> None:
    hr("PYTHON / pytest")

    sample_module = "smoke_py"
    upload_path = Path("uploads") / f"{sample_module}.py"
    upload_path.parent.mkdir(exist_ok=True)
    upload_path.write_text(
        'def add(a, b):\n    return a + b\n\n'
        'def is_even(n):\n    return n % 2 == 0\n',
        encoding="utf-8",
    )

    test_cases = {
        "functional": [
            {
                "name": "add positive",
                "test_code": (
                    "def test_add_positive():\n"
                    "    from smoke_py import add\n"
                    "    assert add(2, 3) == 5\n"
                ),
            }
        ],
        "edge": [
            {
                "name": "is_even zero",
                "test_code": (
                    "def test_is_even_zero():\n"
                    "    from smoke_py import is_even\n"
                    "    assert is_even(0) is True\n"
                ),
            }
        ],
        "negative": [
            {
                "name": "add fails on str",
                "test_code": (
                    "def test_add_fails_on_str():\n"
                    "    import pytest\n"
                    "    from smoke_py import add\n"
                    "    with pytest.raises(TypeError):\n"
                    "        add('a', 1)\n"
                ),
            }
        ],
    }

    test_path = Path(TEST_FOLDER) / f"test_{sample_module}.py"
    test_path.parent.mkdir(exist_ok=True)
    test_path.write_text(
        build_pytest_file(sample_module, test_cases, upload_path.read_text()),
        encoding="utf-8",
    )

    result = run_pytest(str(test_path))
    print(json.dumps({k: v for k, v in result.items() if k != "stdout"}, indent=2))


def smoke_node() -> None:
    hr("JAVASCRIPT / node --test")

    sample_module = "smoke_js"
    test_path = Path(TEST_FOLDER) / f"test_{sample_module}.mjs"
    module_path = Path(TEST_FOLDER) / f"{sample_module}.mjs"

    module_path.write_text(
        "export function add(a, b) { return a + b; }\n"
        "export const greet = (name) => `Hello, ${name}!`;\n",
        encoding="utf-8",
    )

    test_cases = {
        "functional": [
            {
                "name": "add positive",
                "test_code": (
                    "test('test_add_positive', () => {\n"
                    "  assert.equal(target.add(2, 3), 5);\n"
                    "});"
                ),
            },
            {
                "name": "greet returns string",
                "test_code": (
                    "test('test_greet_returns_string', () => {\n"
                    "  assert.equal(target.greet('World'), 'Hello, World!');\n"
                    "});"
                ),
            },
        ],
        "edge": [
            {
                "name": "add zero",
                "test_code": (
                    "test('test_add_zero', () => {\n"
                    "  assert.equal(target.add(0, 0), 0);\n"
                    "});"
                ),
            }
        ],
        "negative": [
            {
                "name": "intentional failure",
                "test_code": (
                    "test('test_intentional_failure', () => {\n"
                    "  assert.equal(target.add(2, 2), 5);  // expected to FAIL\n"
                    "});"
                ),
            }
        ],
    }

    test_path.write_text(
        build_node_test_file(sample_module, test_cases, "javascript"),
        encoding="utf-8",
    )
    print(f"[generated] {test_path}")

    result = run_node_test(str(test_path))
    summary = {k: v for k, v in result.items() if k not in ("stdout",)}
    print(json.dumps(summary, indent=2))
    if not result.get("ran"):
        print("---- node not available, skipped execution ----")


def smoke_java() -> None:
    hr("JAVA / single-file launcher (JEP 330)")

    test_cases = {
        "functional": [
            {
                "name": "add positive",
                "test_code": (
                    "public static void test_add_positive() throws Exception {\n"
                    "    int got = SmokeJava.add(2, 3);\n"
                    "    if (got != 5) throw new AssertionError(\"add(2,3) = \" + got);\n"
                    "}"
                ),
            }
        ],
        "edge": [
            {
                "name": "add zero",
                "test_code": (
                    "public static void test_add_zero() throws Exception {\n"
                    "    if (SmokeJava.add(0, 0) != 0) throw new AssertionError();\n"
                    "}"
                ),
            }
        ],
        "negative": [
            {
                "name": "intentional failure",
                "test_code": (
                    "public static void test_intentional_failure() throws Exception {\n"
                    "    if (SmokeJava.add(2, 2) == 4) throw new AssertionError(\"forced fail\");\n"
                    "}"
                ),
            }
        ],
    }

    runner_class = "SmokeJavaRunner"
    test_path = Path(TEST_FOLDER) / f"{runner_class}.java"

    java_source = (
        "public class SmokeJava {\n"
        "    public static int add(int a, int b) { return a + b; }\n"
        "}\n"
    )

    test_path.write_text(
        build_java_test_file(runner_class, test_cases, java_source),
        encoding="utf-8",
    )
    print(f"[generated] {test_path}")

    result = run_java_test(str(test_path))
    summary = {k: v for k, v in result.items() if k not in ("stdout",)}
    print(json.dumps(summary, indent=2))
    if not result.get("ran"):
        print("---- java not available, skipped execution ----")


if __name__ == "__main__":
    Path(TEST_FOLDER).mkdir(exist_ok=True)
    smoke_python()
    smoke_node()
    smoke_java()
