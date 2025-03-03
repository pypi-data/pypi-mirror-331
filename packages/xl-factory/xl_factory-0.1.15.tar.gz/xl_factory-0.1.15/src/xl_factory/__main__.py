import os
import sys
import importlib.util
from pathlib import Path


def find_file_upwards(start_path: Path, target_file: str) -> Path:
    current_path = start_path
    while current_path != current_path.parent:
        target_path = current_path / target_file
        if target_path.exists():
            return target_path
        current_path = current_path.parent
    return None


def import_module_from_path(module_name, file_path):
    spec = importlib.util.spec_from_file_location(module_name, file_path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


if len(sys.argv) < 1:
    print("Usage: python script.py <module_name>")
    sys.exit(1)


module_name = sys.argv[1]
start_directory = Path.cwd() # 从当前命令行执行路径开始
target_file = 'factory.py'
factory_path = find_file_upwards(start_directory, target_file)
if factory_path:
    # Add factory.py's directory to sys.path
    factory_dir = str(factory_path.parent)
    if factory_dir not in sys.path:
        sys.path.append(factory_dir)
    factory_module = import_module_from_path('factory', str(factory_path))
    factory = getattr(factory_module, 'factory')
    factory.make_module(module_name)
else:
    print(f"{target_file} not found.")