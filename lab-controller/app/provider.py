from dataclasses import dataclass
from typing import Protocol

@dataclass(frozen=True)
class ProviderResult:
    external_reference: str | None = None
    access_url: str | None = None

class LabProvider(Protocol):
    def provision(self, template_key: str, lab_id: int, user_id: int) -> ProviderResult: ...
    def start(self, external_reference: str) -> ProviderResult: ...
    def stop(self, external_reference: str) -> ProviderResult: ...
    def reset(self, external_reference: str) -> ProviderResult: ...
    def status(self, external_reference: str) -> ProviderResult: ...
    def release(self, external_reference: str) -> ProviderResult: ...
    def delete(self, external_reference: str) -> ProviderResult: ...

class MockLabProvider:
    def provision(self, template_key: str, lab_id: int, user_id: int) -> ProviderResult:
        return ProviderResult(external_reference=f"mock-{template_key}-{lab_id}")
    def start(self, external_reference: str) -> ProviderResult:
        return ProviderResult(external_reference=external_reference)
    def stop(self, external_reference: str) -> ProviderResult:
        return ProviderResult(external_reference=external_reference)
    def reset(self, external_reference: str) -> ProviderResult:
        return ProviderResult(external_reference=external_reference)
    def status(self, external_reference: str) -> ProviderResult:
        return ProviderResult(external_reference=external_reference)
    def release(self, external_reference: str) -> ProviderResult:
        return ProviderResult(external_reference=external_reference)
    def delete(self, external_reference: str) -> ProviderResult:
        return ProviderResult(external_reference=external_reference)
