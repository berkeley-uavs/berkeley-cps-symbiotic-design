from __future__ import annotations

import os
from collections.abc import Callable
from pathlib import Path
from sym_cps.shared.paths import output_folder

build_path: Path = Path(os.path.dirname(__file__)).parent.parent / "frontend" / "build"

storage_path: Path = output_folder

# Usage: session_path(_SESSION_ID_)
session_path: Callable[[str], Path] = lambda s: storage_path / f"s_{s}"

# Usage: design_path(_SESSION_ID_)
design_path: Callable[[str], Path] = lambda s: storage_path / f"s_{s}" / "designs"

# Usage: save_design_path(_SESSION_ID_, _MODE_)
save_design_path: Callable[[str, str], Path] = lambda s, m: storage_path / f"s_{s}" / "designs" / f"save_{m}"
