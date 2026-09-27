from app.contracts import LabInterfaceResult
from app.eve_ng import EveNGAdapter


class FakeClient:
    def __init__(self):
        self.calls = []

    def login(self):
        self.calls.append(("login",))

    def ensure_folder(self, path):
        self.calls.append(("ensure_folder", path))

    def create_lab(self, folder, name, author):
        self.calls.append(("create_lab", folder, name, author))
        return {"status": "success", "data": {"path": f"{folder}/{name}.unl"}}

    def get_lab(self, path):
        self.calls.append(("get_lab", path))
        return {"status": "success", "data": {"path": path}}

    def start_all(self, path):
        self.calls.append(("start_all", path))
        return {"status": "success"}

    def stop_all(self, path):
        self.calls.append(("stop_all", path))
        return {"status": "success"}

    def wipe_all(self, path):
        self.calls.append(("wipe_all", path))
        return {"status": "success"}

    def delete_lab(self, path):
        self.calls.append(("delete_lab", path))
        return {"status": "success"}


def test_eve_adapter_lifecycle_calls_platform_client(monkeypatch):
    adapter = EveNGAdapter(FakeClient())

    provisioned = adapter.provision("sdwan", 7, 42)
    assert isinstance(provisioned, LabInterfaceResult)
    assert provisioned.external_reference == "/Training-Platform/lab-7-user-42.unl"

    started = adapter.start(provisioned.external_reference)
    stopped = adapter.stop(provisioned.external_reference)
    reset = adapter.reset(provisioned.external_reference)
    status = adapter.status(provisioned.external_reference)
    released = adapter.release(provisioned.external_reference)
    deleted = adapter.delete(provisioned.external_reference)

    assert started.state == "running"
    assert stopped.state == "stopped"
    assert reset.state == "provisioned"
    assert status.external_reference == provisioned.external_reference
    assert released.state == "released"
    assert deleted.state == "deleted"

    assert ("ensure_folder", "/Training-Platform") in adapter.client.calls
    assert ("create_lab", "/Training-Platform", "lab-7-user-42", "Training Platform") in adapter.client.calls
    assert ("start_all", provisioned.external_reference) in adapter.client.calls
    assert ("stop_all", provisioned.external_reference) in adapter.client.calls
    assert ("wipe_all", provisioned.external_reference) in adapter.client.calls
    assert ("get_lab", provisioned.external_reference) in adapter.client.calls
    assert ("delete_lab", provisioned.external_reference) in adapter.client.calls
