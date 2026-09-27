from pathlib import Path
from app.native import NativeEveBackend, NativeEveSettings

def test_filesystem_clone(tmp_path: Path):
    root = tmp_path / "labs"; root.mkdir()
    template = root / "templates" / "base.unl"; template.parent.mkdir(); template.write_text("<lab/>")
    backend = NativeEveBackend(NativeEveSettings(labs_root=root, wrapper_path=root / "wrapper"))
    assert backend.provision("/templates/base.unl", "/Training-Platform/student-001.unl") == "/Training-Platform/student-001.unl"
    assert (root / "Training-Platform/student-001.unl").read_text() == "<lab/>"

def test_status(tmp_path: Path):
    root = tmp_path / "labs"; root.mkdir(); (root / "student.unl").write_text("<lab/>")
    backend = NativeEveBackend(NativeEveSettings(labs_root=root, wrapper_path=root / "wrapper"))
    result = backend.status("/student.unl")
    assert result["exists"] is True
