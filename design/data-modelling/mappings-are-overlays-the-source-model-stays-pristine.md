---
title: Mappings are overlays, the source model stays pristine
type: pattern
cluster: data-modelling
component: none
tags: [vss, dbc, arxml, mapping, overlay, kuksa-can-provider]
status: draft
sources:
  - repos/vehicle_signal_specification/docs-gen/content/extensions/network_serialization_profile.md
  - repos/vehicle_signal_specification/docs-gen/content/extensions/_index.md
  - repos/vss-tools/docs/export.md (-e, --extended-attributes, --strict)
  - https://github.com/eclipse-kuksa/kuksa-can-provider
last-verified: 2026-10-03
related:
  - "[[vss-kuksa-howto]]"
  - "[[openbsw-howto]]"
  - "[[pick-the-model-by-layer-not-by-fashion]]"
  - "[[the-conversion-rule-is-part-of-the-type]]"
applies-to: [vss-kuksa, openbsw]
gap-rows: [B6, B11, D4]
---

# Mappings are overlays, the source model stays pristine

**Problem.** The DBC says `VCLEFT_mirrorTiltYPosition`, the VSS says `Vehicle.Body.Mirrors.DriverSide.Tilt`. Whoever edits either file to fit the other makes both unreusable: the DBC drifts from the ECU, the VSS drifts from COVESA.

**Forces.**
- The same VSS signal has different sources per vehicle variant; the same DBC serves many VSS trees.
- Mapping includes rate, endianness, transform and defaults, none of which belongs in the catalog.
- Unknown keys are errors under `--strict`.

**The rule.** Source model, target model and mapping are three artefacts; the mapping is an overlay on the target, keyed by the target's name and pointing at the source's names. VSS already ships this: the *network serialization profile* puts `network_serialization: {signal, interval_ms, on_change, endianness, length_bits, default, transform}` on the VSS node in an overlay, with `transform.math` (`py-expression-eval`, `x` is the physical DBC value) and `transform.representation` (value/text list). The DBC keeps its own factor/offset; the mapping only bridges physical to physical. Whitelist the key with `vspec export ... -e network_serialization` and keep the overlay in its own file so a VSS upgrade is a replace, not a merge.

**Prior art.**
| Where | The idea | What it gives you |
|---|---|---|
| VSS network serialization profile | mapping keys in an overlay | a standardised, versionable mapping shape |
| kuksa-can-provider `dbc2val`/`val2dbc` | DBC plus mapping JSON/overlay feeds the broker | the runtime that consumes the mapping |
| vss-tools `-e` | whitelisted extended attributes | extension keys survive export and are checked under `--strict` |
| AUTOSAR ARXML system extract | signal-to-PDU mapping is its own element | mapping as a first-class artefact, not an edit of the signal |
| Vorto mapping models | platform mapping separate from the information model | the same separation in another ecosystem |

**On the Eclipse SDV stack.** [[vss-kuksa-howto]] section 6 and 7: overlay plus `-e`, then kuksa-can-provider in replay mode against a candump. OpenBSW emits the frames ([[openbsw-howto]]); gap B11 (DBC to overlay drafter) is exactly "emit a tentative `network_serialization` overlay from cantools, curator trims". Same VSS names with CSV or CAN provider is gap D4.

**The trap.** Editing `Vehicle.vspec` to add a `dbc:` key, then losing it on the next VSS release. Also: the mapping repeating factor/offset already in the DBC, which makes two sources of truth.

**For a hackathon team.** One DBC, one overlay, one provider run, one dashboard that works unchanged when the mapping file is swapped. Pitch: "the mapping is a file, not a fork".

**Evidence.** Profile syntax and the Tesla mirror example: network_serialization_profile.md. `-e`/`--strict`: export.md. kuksa-can-provider mapping format details (`dbc:` keys) are in the older provider README and may differ from the profile syntax; verify against the provider version in use (unverified).
