import platform
import subprocess
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
      subprocess.Popen(
        ["xdg-open", str(path)],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        start_new_session=True,
      )
  except Exception as e:
    # Re-raise or handle specific execution errors
    raise RuntimeError(f"Failed to open {path}: {e}")
