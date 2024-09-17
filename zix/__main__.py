#!/usr/bin/env python3
import os

from .cli import entry_point

if __name__ == "__main__":
    code_dir, _ = os.path.split(__file__)
    working_dir = os.path.join(code_dir, "default_project") 
    entry_point(working_dir=working_dir)