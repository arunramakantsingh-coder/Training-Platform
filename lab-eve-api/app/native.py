from __future__ import annotations

import os
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


class NativeEveError(RuntimeError):
    pass


@dataclass(frozen=True)
class NativeEveSettings:
    labs_root: Path = Path(os.getenv("LAB_EVE_LABS_ROOT", "/opt/unetlab/labs"))
    wrapper_path: Path = Path(os.getenv("LAB_EVE_WRAPPER_PATH", "/opt/unetlab/wrappers/unl_wrapper"))


class NativeEveBackend:
    def __init__(self, settings: NativeEveSettings | None = None) -> None:
        self.settings = settings or NativeEveSettings()

    def _resolve_lab_path(self, lab_path: str) -> Path:
        relative = lab_path.strip("/")
        if not relative or ".." in Path(relative).parts:
            raise NativeEveError("Invalid lab path")
        path = (self.settings.labs_root / relative).resolve()
        root = self.settings.labs_root.resolve()
        if path != root and root not in path.parents:
            raise NativeEveError("Lab path escapes EVE labs root")
        return path

    def provision(self, template_path: str, lab_path: str) -> str:
        source = self._resolve_lab_path(template_path)
        destination = self._resolve_lab_path(lab_path)
        if source.suffix != ".unl" or destination.suffix != ".unl":
            raise NativeEveError("Template and lab paths must be .unl files")
        if not source.is_file():
            raise NativeEveError(f"Template not found: {template_path}")
        if destination.exists():
            raise NativeEveError(f"Lab already exists: {lab_path}")
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)
        return "/" + str(destination.relative_to(self.settings.labs_root))

    def status(self, lab_path: str) -> dict:
        path = self._resolve_lab_path(lab_path)
        if not path.is_file():
            raise NativeEveError(f"Lab not found: {lab_path}")
        return {"lab_path": "/" + str(path.relative_to(self.settings.labs_root)), "exists": True, "size_bytes": path.stat().st_size}

    def _run_wrapper(self, *args: str) -> None:
        if not self.settings.wrapper_path.is_file():
            raise NativeEveError(f"EVE wrapper not found: {self.settings.wrapper_path}")
        try:
            result = subprocess.run([str(self.settings.wrapper_path), *args], check=False, capture_output=True, text=True, timeout=60)
        except OSError as exc:
            raise NativeEveError(str(exc)) from exc
        if result.returncode != 0:
            raise NativeEveError(result.stderr.strip() or result.stdout.strip() or "EVE wrapper failed")

    def start(self, lab_path: str) -> None:
        raise NativeEveError("Start mapping pending verification of unl_wrapper syntax on the installed EVE-NG version.")

    def stop(self, lab_path: str) -> None:
        raise NativeEveError("Stop mapping pending verification of unl_wrapper syntax on the installed EVE-NG version.")

    def reset(self, lab_path: str) -> None:
        raise NativeEveError("Reset/wipe mapping pending verification of unl_wrapper syntax on the installed EVE-NG version.")

    def delete(self, lab_path: str) -> None:
        path = self._resolve_lab_path(lab_path)
        if path.exists():
            path.unlink()
