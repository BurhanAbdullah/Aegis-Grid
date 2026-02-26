# protocol/

Formal protocol definitions for Aegis-Grid communication.

## Purpose

Defines the message structure, acceptance rules, and invalidation semantics
that underpin the fail-secure communication model.

## Core Protocol Properties

1. **Timing validity** — message must arrive within declared deadline
2. **Structural correctness** — message must conform to schema
3. **Trust assumptions** — sender must hold valid credentials (PKI, v1.3+)
4. **Physical safety relevance** — message must not encode a physically unsafe command

A message failing **any** criterion is **rejected entirely** — no partial acceptance.

## Contents

- Message schema definitions
- Acceptance rule implementations
- Invalidation logic
- PKI identity handshake (introduced in v1.3 / `MASTER RELEASE v1.3`)

## Relationship to `aegis_grid/protocol/`

The `aegis_grid/protocol/` Python package is the executable implementation
of the specifications defined here.
