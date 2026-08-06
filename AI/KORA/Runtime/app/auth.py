"""Provider-agnostic KORA Bearer authentication and scope authorization."""

from __future__ import annotations

import hmac
import os
from dataclasses import dataclass
from enum import Enum


class MemoryScope(str, Enum):
    READ = "memory:read"
    APPROVE = "memory:approve"
    OPERATE = "memory:operate"


@dataclass(frozen=True, slots=True)
class Principal:
    principal_id: str
    scopes: frozenset[MemoryScope]


class AuthenticationError(PermissionError):
    pass


class AuthorizationError(PermissionError):
    pass


class BearerAuthorizer:
    def __init__(self, credentials: dict[str, tuple[str, frozenset[MemoryScope]]]) -> None:
        tokens = [token for token, _ in credentials.values() if token]
        if len(tokens) != len(set(tokens)):
            raise ValueError("KORA Memory API tokens must be distinct")
        self._credentials = credentials

    @classmethod
    def from_environment(cls) -> "BearerAuthorizer":
        return cls(
            {
                "memory-reader": (
                    os.environ.get("KORA_MEMORY_READ_TOKEN", ""),
                    frozenset({MemoryScope.READ}),
                ),
                "memory-user": (
                    os.environ.get("KORA_MEMORY_APPROVAL_TOKEN", ""),
                    frozenset({MemoryScope.READ, MemoryScope.APPROVE}),
                ),
                "memory-operator": (
                    os.environ.get("KORA_MEMORY_OPERATOR_TOKEN", ""),
                    frozenset({MemoryScope.READ, MemoryScope.OPERATE}),
                ),
            }
        )

    @property
    def configured(self) -> bool:
        return all(token for token, _ in self._credentials.values())

    def authorize(self, authorization: str | None, required: MemoryScope) -> Principal:
        if not self.configured:
            raise AuthenticationError("KORA Memory API authentication is not configured")
        if not authorization or not authorization.startswith("Bearer "):
            raise AuthenticationError("Bearer authentication required")
        candidate = authorization[7:]
        matched: Principal | None = None
        # Compare against every configured token to avoid early-exit timing signals.
        for principal_id, (token, scopes) in self._credentials.items():
            if hmac.compare_digest(candidate, token):
                matched = Principal(principal_id, scopes)
        if matched is None:
            raise AuthenticationError("invalid Bearer token")
        if required not in matched.scopes:
            raise AuthorizationError(f"missing required scope: {required.value}")
        return matched
