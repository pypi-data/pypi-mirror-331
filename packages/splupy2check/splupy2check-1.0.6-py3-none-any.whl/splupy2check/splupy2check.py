import os
import sys
import subprocess
import argparse


def get_arguments():
    parser = argparse.ArgumentParser(
        prog="splupy2check",
        description="""Checks for occurances of Python2 files in a given folder structure.
                        The program recursively traverses the folder structure, and if a .py file is encountered,
                        it is compiled with Python 3.9.

                        Please make sure to have Python 3.9 installed, since this program specifically uses Python 3.9 to compile the files.
                        """,
    )

    parser.add_argument(
        "input", help="File or folder to be scanned for containing Python 2 code."
    )
    parser.add_argument("-o", "--output", help="Stores program output in a file.")
    parser.add_argument(
        "-v", "--version", action="version", version="1.0.6", help="Prints the version."
    )
    return parser.parse_args()


def compile(file):
    if not (file.endswith(".py")):
        return
    print(f"Compiling file {os.path.abspath(file)}")
    try:
        subprocess.run(
            ["python3.9", "-m", "py_compile", f"{os.path.abspath(file)}"],
            check=True,
            capture_output=True,
        )
    except subprocess.CalledProcessError as e:
        print(f"{str(e.stderr.decode('utf8'))}")


def get_directory_of_file(filepath):
    abs_path = os.path.abspath(filepath)
    path_segments = os.path.split(abs_path)
    return path_segments[0]


def cleanup(current_directory):
    pycache_dir = f"{current_directory}/__pycache__"
    if not (os.path.exists(pycache_dir)):
        return
    for file in os.listdir(pycache_dir):
        os.remove(os.path.join(pycache_dir, file))
    os.rmdir(pycache_dir)


def scan_for_py():
    args = get_arguments()
    input = args.input

    if args.output:
        sys.stdout = open(args.output, "w")

    if not (os.path.isdir(input)):
        compile(input)
        cleanup(get_directory_of_file(input))
        return

    for root, _, files in os.walk(input):
        for file in files:
            compile(os.path.join(root, file))
        cleanup(root)

    if args.output:
        sys.stdout.close()
