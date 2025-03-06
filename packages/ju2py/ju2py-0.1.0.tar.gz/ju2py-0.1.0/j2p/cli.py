#!/usr/bin/env python
# coding: utf-8


import re
import sys
import argparse
import nbformat
from nbconvert import PythonExporter


def convert_notebook_to_script(notebook_path, module_path=None):
    """
    Convert a Jupyter notebook to a clean Python script.

    Usage:
    >>> j2p("example.ipynb")  # Converts to example.py
    >>> j2p("example.ipynb", "output.py")  # Converts to output.py
    """
    with open(notebook_path, "r", encoding="utf-8") as fh:
        nb = nbformat.reads(fh.read(), as_version=4)

    exporter = PythonExporter()
    source, _ = exporter.from_notebook_node(nb)

    # Remove lines starting with `# In[` (cell markers)
    source = re.sub(r"^# In\[[0-9 ]*\]:\n", "", source, flags=re.MULTILINE)

    # Replace multiple blank lines with a single blank line
    source = re.sub(r"\n{2,}", "\n\n", source)

    if module_path is None:
        module_path = notebook_path.replace(".ipynb", ".py")

    with open(module_path, "w", encoding="utf-8") as fh:
        fh.write(source)

    print(f"Converted: {notebook_path} → {module_path}")


def main():
    
    if len(sys.argv) == 1:
        print("Usage: j2p.py <notebook.ipynb> <optional output.py>")
        sys.exit(1)
    else:
        if len(sys.argv) == 2:
            convert_notebook_to_script(sys.argv[1])
        else:
            convert_notebook_to_script(sys.argv[1], sys.argv[2])
            
    
if __name__ == "__main__":
    main()