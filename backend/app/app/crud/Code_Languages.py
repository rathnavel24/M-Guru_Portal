import subprocess
import tempfile
import uuid
import os

def normalize_io(input_data):
    if input_data is None:
        return ""
    return input_data.replace("\r\n", "\n").strip()

def run_python(code, input_data):
    with tempfile.NamedTemporaryFile(delete=False, suffix=".py") as f:
        f.write(code.encode())
        file_name = f.name

    input_data = normalize_io(input_data)

    result = subprocess.run(
        ["python", file_name],
        input=input_data + "\n",
        text=True,
        capture_output=True,
        timeout=3
    )

    return result
    
def run_javascript(code, input_data):
    wrapped_code = f"""
const fs = require('fs');
const input = fs.readFileSync(0, 'utf8').toString().trim();

{code}
"""

    with tempfile.NamedTemporaryFile(delete=False, suffix=".js") as f:
        f.write(wrapped_code.encode())
        file_name = f.name

    result = subprocess.run(
        ["node", file_name],
        input=input_data,
        text=True,
        capture_output=True,
        timeout=3
    )

    return result

def run_c(code, input_data):
    unique = uuid.uuid4().hex
    c_file = f"{unique}.c"
    exe_file = f"{unique}.exe"

    with open(c_file, "w") as f:
        f.write(code)

    try:
        # 🔹 Compile
        compile_process = subprocess.run(
            ["gcc", c_file, "-o", exe_file],
            capture_output=True,
            text=True
        )

        if compile_process.returncode != 0:
            return compile_process  # compilation error

        # 🔹 Run
        result = subprocess.run(
            [exe_file],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=3
        )

        return result

    finally:
        if os.path.exists(c_file):
            os.remove(c_file)
        if os.path.exists(exe_file):
            os.remove(exe_file)

#######3
def run_cpp(code, input_data):
    unique = uuid.uuid4().hex
    cpp_file = f"{unique}.cpp"
    exe_file = f"{unique}.exe"

    with open(cpp_file, "w") as f:
        f.write(code)

    try:
        # 🔹 Compile
        compile_process = subprocess.run(
            ["g++", cpp_file, "-o", exe_file],
            capture_output=True,
            text=True
        )

        if compile_process.returncode != 0:
            return compile_process

        # 🔹 Run
        result = subprocess.run(
            [exe_file],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=3
        )

        return result

    finally:
        if os.path.exists(cpp_file):
            os.remove(cpp_file)
        if os.path.exists(exe_file):
            os.remove(exe_file)

            ##########3

def run_java(code, input_data):
    classname = "Main"
    java_file = f"{classname}.java"

    with open(java_file, "w") as f:
        f.write(code)

    try:
        # 🔹 Compile
        compile_process = subprocess.run(
            ["javac", java_file],
            capture_output=True,
            text=True
        )

        if compile_process.returncode != 0:
            return compile_process

        # 🔹 Run
        result = subprocess.run(
            ["java", classname],
            input=input_data,
            text=True,
            capture_output=True,
            timeout=3
        )

        return result

    finally:
        if os.path.exists(java_file):
            os.remove(java_file)
        if os.path.exists(f"{classname}.class"):
            os.remove(f"{classname}.class")