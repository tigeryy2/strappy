---
name: deslop
description: Simplify code and plans by removing non-essential logic, shrinking abstractions, and matching implementation complexity to real project needs. Use when code feels over-engineered, padded, generic, hard to consume, or "AI slop"; when reviewing/refactoring for clarity; or when implementing a feature or bug fix where the smallest correct solution and focused TDD matter.
---

# Deslop

## Overview

Treat accidental complexity as a bug. Optimize for the smallest implementation that is obviously correct, easy to read, easy to test, and easy to change later.

## Core Questions

- Ask: what code is actually necessary?
- Ask: what is the cleanest possible implementation?
- Ask: what level of complexity is appropriate for this project and the actual usage?
- Ask: can this be solved by deleting code, inlining code, narrowing scope, or removing a layer?
- Ask: is this complexity justified by a concrete requirement, observed failure, security boundary, or realistic edge case—or only by speculation?

## Workflow

1. Re-state the required behavior in a few concrete sentences.
2. List hard constraints and non-goals.
3. Reject speculative flexibility, future-proofing, and generic abstractions unless current requirements force them.
4. Start with TDD.
5. Add or tighten the smallest test that proves the required behavior.
6. Prefer characterization or regression tests when simplifying existing code with uncertain behavior.
7. Delete or narrow code before adding code.
8. Remove dead branches, unused options, single-use helpers, optional layers, and abstractions without present value.
9. Implement the smallest code that meets the requirements.
10. Re-run tests after each simplification step.
11. Stop once the code is clear and complete. Do not add knobs, hooks, extension points, or config without an active requirement.

## TDD Simplification Loop

1. Write the smallest failing test that captures the real need.
2. Write the simplest implementation that passes.
3. Refactor by deletion, inlining, and de-duplication.
4. Re-run tests.
5. Repeat until every remaining line earns its keep.

If tests already cover the behavior well, use those tests as the guardrail and simplify under them instead of adding broad new scaffolding.

## Simplification Heuristics

- Prefer deletion over refactor.
- Prefer local code over shared abstractions until multiple real call sites demand sharing.
- Prefer concrete names, shapes, and control flow over generic helpers.
- Prefer one obvious path over flexible branching.
- Prefer plain data structures over wrappers, factories, or builders around trivial values.
- Prefer fewer moving parts over architectural symmetry.
- Split files only when size or mixed responsibilities are hurting comprehension.
- Keep interfaces as narrow as the current callers allow.

## Red Flags

- Helper used once.
- Config added for a hypothetical future.
- Generic utility created before a second real use case exists.
- Interface broader than the current product surface.
- Branches for modes nobody asked for.
- Wrapper component or service that only forwards arguments.
- Type model that represents possibilities the product does not expose.
- Test setup larger than the behavior under test.

## Response Pattern

1. State the required behavior.
2. State what can be deleted, inlined, or narrowed.
3. State the smallest implementation that satisfies the tests.
4. Justify any remaining complexity with a concrete constraint.

## Guardrails

- Do not preserve complexity just because it already exists.
- Do not introduce abstractions to signal sophistication.
- Do not widen APIs "just in case."
- Do not turn simple logic into patterns with more indirection than value.
- Do not add broad test scaffolding when one focused regression test is enough.

## Example Requests

- `Use $deslop to simplify this hook and keep only the behavior the UI actually uses.`
- `Use $deslop to refactor this service with TDD and delete unnecessary abstractions.`
- `Use $deslop to review this PR for accidental complexity and propose the smallest correct rewrite.`
