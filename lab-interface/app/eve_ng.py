from __future__ import annotations

from dataclasses import dataclass
from urllib.parse import quote

import httpx

from app.config import settings
from app.contracts import LabInterfaceResult


class LabEveAPIError(RuntimeError):
    pass


@dataclass
class LabEveAPIClient:
    base_url: str
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

    def _request(self, method: str, path: str, **kwargs) -> dict:
        response = self._client.request(method, path, **kwargs)
        response.raise_for_status()
        payload = response.json()
        if payload.get("detail"):
            raise LabEveAPIError(str(payload["detail"]))
        return payload

    def provision(self, template_path: str, lab_path: str) -> dict:
        return self._request(
            "POST",
            "/v1/labs/provision",
            json={"template_path": template_path, "lab_path": lab_path},
        )

    def start(self, lab_path: str) -> dict:
        return self._request("POST", "/v1/labs/start", json={"lab_path": lab_path})

    def stop(self, lab_path: str) -> dict:
        return self._request("POST", "/v1/labs/stop", json={"lab_path": lab_path})

    def reset(self, lab_path: str) -> dict:
        return self._request("POST", "/v1/labs/reset", json={"lab_path": lab_path})

    def status(self, lab_path: str) -> dict:
        return self._request(
            "GET",
            f"/v1/labs?lab_path={quote(lab_path, safe='')}",
        )

    def delete(self, lab_path: str) -> dict:
        return self._request(
            "DELETE",
            "/v1/labs",
            json={"lab_path": lab_path},
        )


class LabConnector:
    """EVE implementation of the generic Lab Interface."""

    def __init__(self, client: LabEveAPIClient | None = None) -> None:
        self.client = client or LabEveAPIClient(
            base_url=settings.lab_eve_api_url,
            verify_ssl=settings.lab_eve_api_verify_ssl,
            timeout=settings.lab_eve_api_timeout_seconds,
        )

    def provision(self, template_key: str, lab_id: int, user_id: int) -> LabInterfaceResult:
        template_path = (
            f"{settings.lab_eve_template_root.rstrip('/')}/{template_key}.unl"
        )
        lab_path = f"{settings.lab_eve_lab_root.rstrip('/')}/lab-{lab_id}-user-{user_id}.unl"
        payload = self.client.provision(template_path, lab_path)
        return LabInterfaceResult(
            external_reference=payload["lab_path"],
            state=payload.get("state", "provisioned"),
        )

    def start(self, external_reference: str) -> LabInterfaceResult:
        payload = self.client.start(external_reference)
        return LabInterfaceResult(external_reference, state=payload.get("state", "running"))

    def stop(self, external_reference: str) -> LabInterfaceResult:
        payload = self.client.stop(external_reference)
        return LabInterfaceResult(external_reference, state=payload.get("state", "stopped"))

    def reset(self, external_reference: str) -> LabInterfaceResult:
        payload = self.client.reset(external_reference)
        return LabInterfaceResult(external_reference, state=payload.get("state", "provisioned"))

    def status(self, external_reference: str) -> LabInterfaceResult:
        self.client.status(external_reference)
        return LabInterfaceResult(external_reference, state="unknown")

    def release(self, external_reference: str) -> LabInterfaceResult:
        return LabInterfaceResult(external_reference, state="released")

    def delete(self, external_reference: str) -> LabInterfaceResult:
        payload = self.client.delete(external_reference)
        return LabInterfaceResult(external_reference, state=payload.get("state", "deleted"))


# Temporary compatibility name for the existing Phase 6 tests/imports.
EveNGAdapter = LabConnector
EveNGError = LabEveAPIError
