# Access Control & Authorization Test Matrix Template

> **Standard:** OWASP ASVS v4.0 Chapter 4 (Access Control Verification) & CWE-639  
> **Evaluation Phase:** Stage 7 (Cross-Context Testing & BOLA Boundary Analysis)

---

## 1. Project & Scope Metadata

- **Target Program:** `[PROGRAM_NAME]`
- **Lead Researcher:** `[RESEARCHER_USERNAME]`
- **Evaluation Date:** `[YYYY-MM-DD]`
- **Safe Harbor Header:** `X-Bug-Bounty: [PLATFORM]-[USERNAME]`
- **Testing Contexts:**
  - **Context A (Attacker):** `User A (account_a@example.com)`
  - **Context B (Victim):** `User B (account_b@example.com)`

---

## 2. Test Execution Matrix

| Test ID | Endpoint / Route | Method | Access Scenario | Expected Response | Observed Response | Verdict | Notes |
| :---: | :--- | :---: | :--- | :---: | :---: | :---: | :--- |
| **AC-01** | `/api/v1/user/profile` | `GET` | Unauthenticated | `401 / 302` | `302 Found` | **PASS** | Session-bound redirect |
| **AC-02** | `/api/v1/user/profile` | `GET` | User A Self Context | `200 OK` | `200 OK` | **PASS** | Access to own data |
| **AC-03** | `/api/v1/orders/{order_id}` | `GET` | User A requests User B ID | `403 / 404` | `404 Not Found` | **PASS** | Tenant boundary enforced |
| **AC-04** | `/api/v1/workspaces/{ws_id}` | `PUT` | Cross-tenant mutation | `403 Forbidden` | `403 Forbidden` | **PASS** | Modification denied |

---

## 3. Verdict Legend

* **PASS (Secure):** Endpoint enforces session binding, returns `401/403/404`, or restricts data to the active security principal.
* **FAIL (Vulnerable):** Endpoint returns `200 OK` with another tenant's data or permits unauthorized state changes (Proceed to Stage 8 PoC).
* **INFO (Public):** Endpoint intentionally serves non-sensitive, publicly accessible assets.
