"""
secure_authorization_pattern.py
================================================================================
Defensive Architecture Reference Implementation:
Demonstrating Broken Object Level Authorization (BOLA/IDOR - OWASP API1:2023)
vs. Scoped Multi-Tenant Ownership Authorization.

Run directly in terminal:
    python3 src/secure_authorization_pattern.py
================================================================================
"""

from dataclasses import dataclass
from typing import Optional, Dict


class SecurityException(Exception):
    """Base exception for authorization and access failures."""
    pass


class AuthenticationError(SecurityException):
    """Raised when an unauthenticated request attempts access (HTTP 401)."""
    pass


class AuthorizationError(SecurityException):
    """Raised when an authenticated principal attempts unauthorized access (HTTP 403)."""
    pass


class ResourceNotFoundError(SecurityException):
    """Raised when a resource does not exist (HTTP 404)."""
    pass


@dataclass(frozen=True)
class SecurityPrincipal:
    """Immutable user security context extracted from a verified JWT/session."""
    user_id: str
    tenant_id: str
    role: str = "member"


@dataclass
class DomainResource:
    """Domain entity containing multi-tenant boundary identifiers."""
    resource_id: str
    tenant_id: str
    owner_id: str
    data_payload: str


class MockRepository:
    """Simulates a persistence layer with multi-tenant data."""
    def __init__(self):
        self._store: Dict[str, DomainResource] = {
            "res_alpha_01": DomainResource("res_alpha_01", "tenant_alpha", "user_a", "Alpha Confidential Records"),
            "res_beta_01": DomainResource("res_beta_01", "tenant_beta", "user_b", "Beta Enterprise Orders"),
        }

    def fetch_by_id(self, resource_id: str) -> Optional[DomainResource]:
        return self._store.get(resource_id)


class AccessControlService:
    def __init__(self, repo: MockRepository):
        self.repo = repo

    def get_vulnerable_object(self, caller: SecurityPrincipal, resource_id: str) -> DomainResource:
        """
        VULNERABLE IMPLEMENTATION (BOLA / IDOR):
        Validates caller authentication, but directly returns object without tenant scoping.
        """
        if not caller:
            raise AuthenticationError("Caller must be authenticated.")

        resource = self.repo.fetch_by_id(resource_id)
        if not resource:
            raise ResourceNotFoundError(f"Resource {resource_id} not found.")

        # DEFECT: Missing tenant/owner validation check!
        return resource

    def get_secure_object(self, caller: SecurityPrincipal, resource_id: str) -> DomainResource:
        """
        DEFENSIVE REMEDIATED IMPLEMENTATION:
        Enforces tenant boundary validation at the trust boundary.
        """
        if not caller:
            raise AuthenticationError("Caller must be authenticated.")

        resource = self.repo.fetch_by_id(resource_id)
        if not resource:
            raise ResourceNotFoundError(f"Resource {resource_id} not found.")

        # CONTROL 1: Multi-tenant boundary check
        if resource.tenant_id != caller.tenant_id:
            raise AuthorizationError(
                f"Access Denied: Principal {caller.user_id} (Tenant: {caller.tenant_id}) "
                f"attempted unauthorized access to Resource {resource_id} (Tenant: {resource.tenant_id})"
            )

        # CONTROL 2: Object-level owner check (for private items)
        if caller.role != "admin" and resource.owner_id != caller.user_id:
            raise AuthorizationError(f"Access Denied: Principal does not own resource {resource_id}")

        return resource


def run_verification_suite():
    """Assertion-based self-verification suite (Runs in any standard Python 3.8+ environment)."""
    repo = MockRepository()
    service = AccessControlService(repo)

    user_alpha = SecurityPrincipal(user_id="user_a", tenant_id="tenant_alpha")
    user_beta = SecurityPrincipal(user_id="user_b", tenant_id="tenant_beta")

    print("[*] Running Access Control Verification Suite...")

    # 1. Legitimate Self Access
    res = service.get_secure_object(user_alpha, "res_alpha_01")
    assert res.data_payload == "Alpha Confidential Records", "Failed legitimate access."
    print("  [PASS] Test 1: Principal can access own tenant resource.")

    # 2. Defect Demonstration (Vulnerable Path)
    leaked = service.get_vulnerable_object(user_alpha, "res_beta_01")
    assert leaked.data_payload == "Beta Enterprise Orders", "Vulnerable path failed to demonstrate leak."
    print("  [WARN] Test 2: Vulnerable path reproduced cross-tenant data leak.")

    # 3. Defensive Enforcement (Remediated Path)
    blocked = False
    try:
        service.get_secure_object(user_alpha, "res_beta_01")
    except AuthorizationError:
        blocked = True
    assert blocked, "Security Failure: Cross-tenant access was not blocked!"
    print("  [PASS] Test 3: Remediated path successfully blocked cross-tenant access (403 Forbidden).")

    # 4. Unauthenticated Access Blocked
    unauth_blocked = False
    try:
        service.get_secure_object(None, "res_alpha_01")
    except AuthenticationError:
        unauth_blocked = True
    assert unauth_blocked, "Security Failure: Unauthenticated request was not blocked!"
    print("  [PASS] Test 4: Unauthenticated request blocked (401 Unauthorized).")

    # 5. Non-Existent Resource Returns 404
    missing_blocked = False
    try:
        service.get_secure_object(user_alpha, "non_existent_id")
    except ResourceNotFoundError:
        missing_blocked = True
    assert missing_blocked, "Security Failure: Missing resource did not raise 404!"
    print("  [PASS] Test 5: Missing resource correctly returned 404 Not Found.")

    print("\n[SUCCESS] 5/5 access control assertions passed! Defense verified.\n")


if __name__ == "__main__":
    run_verification_suite()
