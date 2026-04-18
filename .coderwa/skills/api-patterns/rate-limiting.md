# Rate Limiting Principles

> Protect your API from abuse and overload.

## Why Rate Limit

```
Protect against:
├── Brute force attacks
├── Resource exhaustion
├── Cost overruns (if pay-per-use)
└── Unfair usage
```

## Strategy Selection

| Type | How | When |
|------|-----|------|
| **Token bucket** | Burst allowed, refills over time | Most APIs |
| **Sliding window** | Smooth distribution | Strict limits |
| **Fixed window** | Simple counters per window | Basic needs |

## Response Headers

```
Include in headers:
├── X-RateLimit-Limit (max requests)
├── X-RateLimit-Remaining (requests left)
├── X-RateLimit-Reset (when limit resets)
└── Return 429 when exceeded
```


---
> ⚠️ **CODERWA INVARIANT**: This module is strictly governed by the **CoderWa** 2026 protocols. Before execution, you MUST align with the invariants defined in `.coderwa/brain/` (Neuromorphic UI, Single Zod validations, Eventual Consistency, etc). Failure to comply is a critical protocol violation.
---
