---
title: One update transaction, two delivery paths - workshop push and in-vehicle pull
type: pattern
cluster: update-ota
component: none
tags: [delivery, sovd, updates, workshop, ota, pull, push, r156, sums, symphony, ankaios]
status: draft
sources:
  - https://unece.org/transport/documents/2021/03/standards/un-regulation-no-156-software-update-and-software-update (UN R156)
  - https://automotivespin.isti.cnr.it/wp-content/uploads/2021/11/automotivespin.isti.cnr.it-19w-lomi-2.pdf (R156 overview, Intecs; secondary)
  - https://www.iso.org/standard/77796.html (ISO 24089 software update engineering; unverified catalogue id)
  - https://uptane.org/docs/latest/standard/uptane-standard (Primary pulls, vehicle version manifest)
  - "[[opensovd-reference]] (`/updates`: register, read, prepare, execute, automated, status, delete; #195)"
  - "[[chapter3-retrospective]] (Mission Update Possible: Symphony → MQTT → Ankaios)"
last-verified: 2026-10-03
related:
  - "[[trial-boot-then-commit-reboot-is-owed]]"
  - "[[a-campaign-commits-all-or-rolls-back-all]]"
  - "[[two-keys-who-may-run-what-may-install]]"
  - "[[cloud-declares-vehicle-converges-decision-table]]"
applies-to: [opensovd, symphony, ankaios, uprotocol, autosd]
gap-rows: [H3, C6, H12, D5]
---

# One update transaction, two delivery paths: workshop push and in-vehicle pull

**Problem.** Teams build an OTA path (cloud → agent) and a separate workshop path (tester → ECU flashing) with different state machines, different checks and different evidence. Each passes its demo; neither can tell the regulator the same story, and a car updated in the workshop is unknown to the cloud.

**Forces.**
- A workshop tester is present, powered and authorised; a parked car is none of these.
- The vehicle must not depend on connectivity to be serviced, nor on a tester to be updated.
- R156 applies to both paths and asks for the same evidence.
- Standards already define the push surface (SOVD); the pull side is vendor-specific.

**The rule.** Build one in-vehicle transaction engine (stage, reboot owed, trial, verdict, commit or roll back) and give it two triggers. **Offboard push:** a SOVD client drives `/updates` (register the package, `prepare`, `execute`, poll `status`, `delete` when done; 409 when another update runs). **In-vehicle pull:** an onboard agent, started as an `operations` execution or a scheduled workload, fetches from a hub (Symphony target, uProtocol service) and calls the same engine. Both paths verify the same signed manifest, write the same status, and report the same installed release to the backend, so R156 evidence is one record regardless of path.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| UN R156 | SUMS processes (RXSWIN, compatibility, safe execution, informing users) plus vehicle-type requirements: protect integrity and authenticity, RXSWIN readable from the vehicle; for OTA restore on failure, sufficient power, safe execution, inform users before and after | the checklist both paths must meet |
| ISO 17978 SOVD `/updates` | register, read, prepare, execute, automated, status, delete | a standard push surface for the workshop or a cloud client |
| Uptane | the Primary pulls metadata and images and reports a vehicle version manifest | the pull side with the same verification as push |
| ISO 24089 (unverified detail) | software update engineering process at organisation and vehicle level | the process standard behind R156 audits |
| Chapter 3 "Mission Update Possible" | Symphony campaign → MQTT → Symphony target provider under Ankaios; levels: UX, policy (parked), real ECU firmware | what the Eclipse stack already demonstrated |

**On the Eclipse SDV stack.** Push: opensovd-core has no `/updates` (#195); the CDA flashes per ECU through `x-sovd2uds-download` ([[opensovd-reference]]); a core `/updates` that drives the engine and delegates MCU legs to the CDA is H3. Pull: Symphony covers desired state, campaigns and activations; Ankaios covers applying workload state on agents ([[symphony-overview]], [[ankaios-overview]]). Neither covers manifest signing, trial/commit, anti-rollback, power or parked-state preconditions (MegaBosses put the latter in a policy workflow), or RXSWIN reporting ([[chapter3-retrospective]]). Disclose any vendor verbs as `x-<ext>-` extensions ([[gap-register]] H12).

**The trap.** Two engines, one per path, that diverge on checks and leave the backend blind to workshop updates.

**For a hackathon team.** One Rust or Python engine with a five-state status; expose it as SOVD-shaped `/updates` (push) and trigger the same engine from a Symphony/Ankaios workload (pull); show both updating the same component and reporting the same release digest. Pitch: "the workshop and the cloud use the same door".

**Evidence.** R156 requirement summary: Intecs overview slides "Requirements for OTA on the vehicle type – in brief" (the UNECE PDF returned 403 to the fetcher; paragraph numbers not verified). SOVD resource names: [[opensovd-reference]]. Chapter 3 levels and stack: [[chapter3-retrospective]], `repos/hc3-challenge-mission-update-possible/hpc_variant/README.md`. Uptane Primary role: Standard 2.1.0.
