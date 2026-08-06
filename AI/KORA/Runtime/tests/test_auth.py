from __future__ import annotations

import unittest

from app.auth import (
    AuthenticationError,
    AuthorizationError,
    BearerAuthorizer,
    MemoryScope,
)


class BearerAuthorizerTests(unittest.TestCase):
    def setUp(self) -> None:
        self.authorizer = BearerAuthorizer(
            {
                "reader": ("read-secret", frozenset({MemoryScope.READ})),
                "user": (
                    "approval-secret",
                    frozenset({MemoryScope.READ, MemoryScope.APPROVE}),
                ),
                "operator": (
                    "operator-secret",
                    frozenset({MemoryScope.READ, MemoryScope.OPERATE}),
                ),
            }
        )

    def test_authentication_and_read_scope(self) -> None:
        principal = self.authorizer.authorize("Bearer read-secret", MemoryScope.READ)
        self.assertEqual(principal.principal_id, "reader")

    def test_missing_and_invalid_tokens_are_rejected(self) -> None:
        with self.assertRaises(AuthenticationError):
            self.authorizer.authorize(None, MemoryScope.READ)
        with self.assertRaises(AuthenticationError):
            self.authorizer.authorize("Bearer wrong", MemoryScope.READ)

    def test_user_and_operator_authorization_are_distinct(self) -> None:
        self.authorizer.authorize("Bearer approval-secret", MemoryScope.APPROVE)
        self.authorizer.authorize("Bearer operator-secret", MemoryScope.OPERATE)

        with self.assertRaises(AuthorizationError):
            self.authorizer.authorize("Bearer operator-secret", MemoryScope.APPROVE)
        with self.assertRaises(AuthorizationError):
            self.authorizer.authorize("Bearer read-secret", MemoryScope.OPERATE)

    def test_duplicate_tokens_fail_closed(self) -> None:
        with self.assertRaises(ValueError):
            BearerAuthorizer(
                {
                    "reader": ("same", frozenset({MemoryScope.READ})),
                    "user": ("same", frozenset({MemoryScope.APPROVE})),
                }
            )


if __name__ == "__main__":
    unittest.main()
