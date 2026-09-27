from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

import httpx

from app.config import settings
from app.contracts import LabInterfaceResult


class EveNGError(RuntimeError):
    pass


@dataclass
class EveNGClient:
    base_url: str
    username: str
    password: str
    verify_ssl: bool = False
    timeout: float = 15.0

    def __post_init__(self) -> None:
        self._client = httpx.Client(
            base_url=self.base_url.rstrip("/"),
            verify=self.verify_ssl,
            timeout=self.timeout,
        )

    def close(self) -> None:
        self._client.close()

    def login(self) -> None:
        response = self._client.post(
            "/api/auth/login",
            json={
                "username": self.username,
                "password": self.password,
                "html5": "0",
            },
        )
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") != "success":
            raise EveNGError(payload.get("message", "EVE-NG authentication failed"))

    def _request(self, method: str, path: str, **kwargs) -> dict:
        response = self._client.request(method, path, **kwargs)
        if response.status_code in {400, 401}:
            self.login()
            response = self._client.request(method, path, **kwargs)
        response.raise_for_status()
        payload = response.json()
        if payload.get("status") != "success":
            raise EveNGError(payload.get("message", "EVE-NG API request failed"))
        return payload

    def get_folder(self, path: str) -> dict:
        return self._request(
            "GET",
            f"/api/folders/{quote(path.strip('/'), safe='/')}",
        )

    def create_folder(self, parent: str, name: str) -> dict:
        return self._request(
            "POST",
            "/api/folders",
            json={"path": parent, "name": name},
        )

    def ensure_folder(self, path: str) -> None:
        normalized = "/" + path.strip("/")
        if normalized == "/":
            return
        try:
            self.get_folder(normalized)
            return
        except (EveNGError, httpx.HTTPStatusError):
            parts = [part for part in normalized.strip("/").split("/") if part]
            current = ""
            for part in parts:
                parent = current or "/"
                current = f"{current}/{part}"
                try:
                    self.get_folder(current)
                except (EveNGError, httpx.HTTPStatusError):
                    self.create_folder(parent, part)

    def get_lab(self, path: str) -> dict:
        return self._request("GET", f"/api/labs/{quote(path.strip('/'), safe='/')}")

    def create_lab(self, folder: str, name: str, author: str = "Training Platform") -> dict:
        return self._request(
            "POST",
            "/api/labs",
            json={
                "path": folder,
                "name": name,
                "version": "1",
                "author": author,
                "description": "Training Platform lab",
            },
        )

    def delete_lab(self, path: str) -> dict:
        return self._request(
            "DELETE",
            f"/api/labs/{quote(path.strip('/'), safe='/')}",
        )

    def start_all(self, path: str) -> dict:
        encoded = quote(path.strip("/"), safe="/")
        return self._request("GET", f"/api/labs/{encoded}/nodes/start")

    def stop_all(self, path: str) -> dict:
        encoded = quote(path.strip("/"), safe="/")
        return self._request("GET", f"/api/labs/{encoded}/nodes/stop")

    def wipe_all(self, path: str) -> dict:
        encoded = quote(path.strip("/"), safe="/")
        return self._request("GET", f"/api/labs/{encoded}/nodes/wipe")


class EveNGAdapter:
    def __init__(self, client: EveNGClient | None = None) -> None:
        self.client = client or EveNGClient(
            base_url=settings.eve_ng_base_url,
            username=settings.eve_ng_username,
            password=settings.eve_ng_password,
            verify_ssl=settings.eve_ng_verify_ssl,
            timeout=settings.eve_ng_timeout_seconds,
        )

    def provision(self, template_key: str, lab_id: int, user_id: int) -> LabInterfaceResult:
        # Template cloning is intentionally a separate increment. For now the
        # adapter creates a uniquely named EVE-NG lab in the configured workspace.
        folder = settings.eve_ng_lab_folder
        name = f"lab-{lab_id}-user-{user_id}"
        self.client.login()
        self.client.ensure_folder(folder)
        payload = self.client.create_lab(folder=folder, name=name, author="Training Platform")
        path = payload.get("data", {}).get("path") or f"{folder.rstrip('/')}/{name}.unl"
        return LabInterfaceResult(
            external_reference=path,
            access_url=f"{settings.eve_ng_base_url.rstrip('/')}/index.html",
            state="provisioned",
        )

    def start(self, external_reference: str) -> LabInterfaceResult:
        self.client.login()
        self.client.start_all(external_reference)
        return LabInterfaceResult(external_reference=external_reference, state="running")

    def stop(self, external_reference: str) -> LabInterfaceResult:
        self.client.login()
        self.client.stop_all(external_reference)
        return LabInterfaceResult(external_reference=external_reference, state="stopped")

    def reset(self, external_reference: str) -> LabInterfaceResult:
        self.client.login()
        self.client.wipe_all(external_reference)
        return LabInterfaceResult(external_reference=external_reference, state="provisioned")

    def status(self, external_reference: str) -> LabInterfaceResult:
        self.client.login()
        self.client.get_lab(external_reference)
        return LabInterfaceResult(
            external_reference=external_reference,
            access_url=f"{settings.eve_ng_base_url.rstrip('/')}/index.html",
            state="unknown",
        )

    def release(self, external_reference: str) -> LabInterfaceResult:
        return LabInterfaceResult(external_reference=external_reference, state="released")

    def delete(self, external_reference: str) -> LabInterfaceResult:
        self.client.login()
        self.client.delete_lab(external_reference)
        return LabInterfaceResult(external_reference=external_reference, state="deleted")
