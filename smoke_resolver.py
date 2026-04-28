"""Verify _resolve_bin reads JAVA_BIN/NODE_BIN from the environment correctly.

Three scenarios:
1. JAVA_BIN unset      -> falls back to PATH (likely None on this box).
2. JAVA_BIN=<jdk_home> -> resolves to <jdk_home>/bin/java.exe.
3. JAVA_BIN=<exe path> -> resolves to that exact file.
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

# Ensure no PATH leak between scenarios. We deliberately strip the JDK from PATH.
PATH_NO_JDK = ";".join(
    p for p in os.environ.get("Path", "").split(";")
    if "Java" not in p and "jdk" not in p.lower()
)
os.environ["Path"] = PATH_NO_JDK
os.environ["PATH"] = PATH_NO_JDK

sys.path.insert(0, str(Path(__file__).parent))


def reload_app():
    """Force a fresh resolver lookup against the current env."""
    if "app" in sys.modules:
        del sys.modules["app"]
    import app  # noqa: F401
    return sys.modules["app"]


def case(label: str, env: dict[str, str | None]) -> None:
    print(f"\n--- {label} ---")
    for k, v in env.items():
        if v is None:
            os.environ.pop(k, None)
        else:
            os.environ[k] = v
    a = reload_app()
    java = a._resolve_bin(a.JAVA_BIN_ENV, "java")
    node = a._resolve_bin(a.NODE_BIN_ENV, "node")
    print(f"  JAVA_BIN env -> {os.environ.get('JAVA_BIN', '<unset>')}")
    print(f"  resolved java = {java}")
    print(f"  NODE_BIN env -> {os.environ.get('NODE_BIN', '<unset>')}")
    print(f"  resolved node = {node}")


JDK_HOME = r"C:\Program Files\Java\jdk-26.0.1"

case("1. neither var set, java/jdk stripped from PATH",
     {"JAVA_BIN": None, "NODE_BIN": None})

case("2. JAVA_BIN = JDK home directory",
     {"JAVA_BIN": JDK_HOME, "NODE_BIN": None})

case("3. JAVA_BIN = full path to java.exe",
     {"JAVA_BIN": JDK_HOME + r"\bin\java.exe", "NODE_BIN": None})

case("4. JAVA_BIN quoted with spaces (env-file style)",
     {"JAVA_BIN": f'"{JDK_HOME}"', "NODE_BIN": None})

case("5. JAVA_BIN points to garbage -> fall back to PATH",
     {"JAVA_BIN": r"C:\does\not\exist", "NODE_BIN": None})
