---
title: Eclipse SommR (SOME/IP in Rust) - overview
type: overview
component: sommr
tags: [sommr, someip, rust, archived, in-vehicle-comms, adjacent]
status: draft
sources:
  - https://projects.eclipse.org/projects/automotive.sommr
  - https://projects.eclipse.org/projects/automotive.sommr
  - https://projects.eclipse.org/proposals/eclipse-sommr
last-verified: 2026-10-03
related:
  - "[[sommr-integration-notes]]"
  - "[[uprotocol-overview]]"
  - "[[openbsw-overview]]"
  - "[[sdv-landscape-overview]]"
---

# Eclipse SommR

## Short answer
**Archived, and the GitHub repo is empty. Do not plan a hackathon around it.** Use it only as a design reference or as a gap to fill.

## What it was meant to be
"Automotive grade implementation of the SomeIP specification for embedded Linux" plus developer tools; a SOME/IP daemon written in Rust, language-agnostic client side (Rust and Java first), motivated by C++-only (vsomeip) or vendor-locked stacks. Apache-2.0. Proposed by Cariad (SDV Contribution Day June 2022 slides). Sources: https://projects.eclipse.org/proposals/eclipse-sommr, https://projects.eclipse.org/projects/automotive.sommr.

## State (verified 2026-10-03)
- Eclipse project page: lifecycle **archived**; not in the current SDV WG project list (https://projects.eclipse.org/api/projects?working_group=sdv).
- GitHub `eclipse-sommr/sommr`: archived by owner (12 Jun, 2025); page shows "This repository is empty"; API last push 2022-07-08; 6 stars; website repo archived too; org `.github`/`.eclipsefdn` archived. No releases, no version.
- Maturity: **none** (no usable code in public). Any claims about performance, SOME/IP-SD coverage, or TP support are unverified and unverifiable.
- Residual mentions: the BCX2022 hack challenge listed "if applicable SommR" (https://github.com/Eclipse-SDV-Hackathon-BCX/hackchallenge-passenger-welcome); Leda docs navigation does not list it.

## Relevance for in-vehicle communication with classic ECUs
SOME/IP over Ethernet is how many classic AUTOSAR ECUs expose services (the dreamKIT docs also cite SOME/IP via the S32G, https://github.com/eclipse-autowrx/dreamKIT). A SOME/IP bridge is therefore a real gap in the open SDV stack: no Eclipse SDV project currently ships one.
Candidates a team could use instead (not Eclipse SDV, not evaluated here): COVESA vsomeip (C++, the de-facto open stack, unverified in this vault), `rsomeip` (Rust, community, https://github.com/brunoldsilva/rsomeip, search hit only), commercial AUTOSAR stacks. Check licence and maturity before use.
The Eclipse-native alternative path for classic ECUs is not SOME/IP but CAN/UDS via OpenSOVD adapters ([[opensovd-overview]]), CANought for Kanto, or the OpenBSW stack on the MCU side ([[openbsw-overview]]), bridged by [[uprotocol-overview]] / [[zenoh-overview]].

## Quickstart
None possible: there is no code. If you need a hands-on SOME/IP demo, use vsomeip's own examples instead (not verified here).

## Pros / cons / when not to use
Pros: a (former) Rust SOME/IP daemon concept fits the Rust-leaning SDV ecosystem (Ankaios, uProtocol, OpenSOVD, iceoryx2 bindings).
Cons: dead; empty repo; no maintainers.
Do not use: ever as a dependency.

## Hackathon ideas
1. SOME/IP-SD listener in Rust that publishes discovered services as uProtocol/Zenoh topics (read-only gateway, 2 days is realistic).
2. SOME/IP field/event to KUKSA datapoint provider (VSS signal from a SOME/IP service).
3. Compare vsomeip vs rsomeip interop as a reference note.
4. Ask the Eclipse SDV WG whether a successor project is planned (gap register item).
