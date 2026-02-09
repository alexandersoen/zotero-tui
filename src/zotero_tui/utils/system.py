import subprocess
import platform
from pathlib import Path


def open_file(path: Path) -> None:
  """
  Opens a file using the default system application.
  This is a side-effect-only function.
  """
  if not path.exists():
    raise FileNotFoundError(f"No file found at {path}")

  system = platform.system()
  try:
    if system == "Darwin":  # macOS
      subprocess.run(["open", str(path)], check=True)
    elif system == "Windows":  # Windows
      raise NotImplementedError()
    else:  # Linux (standard)
      subprocess.run(["xdg-open", str(path)], check=True)
  except Exception as e:
    # Re-raise or handle specific execution errors
    raise RuntimeError(f"Failed to open {path}: {e}")
