---
type: playbook
component: opendut
tags: [fix, opendut, edgar, docker]
status: draft
sources:
  - "[[opendut-quickstart]]"
last-verified: 2026-10-03
related:
  - "[[opendut-quickstart]]"
---
# openDuT localenv and EDGAR-in-Docker: settings that were needed (2026-10-03)
No override file was needed for the localenv stack itself (ports 80/443/8080/8081 free). For `repos/opendut/.ci/docker/edgar`:
- `export OPENDUT_EDGAR_IMAGE_VERSION=0.10.2` (default tag `0.10.0-alpha` does not match CARL 0.10.2; pull `ghcr.io/eclipse-opendut/opendut-edgar:0.10.2`).
- `export OPENDUT_BACKEND_IP=127.0.0.1` when CARL is on the same host, else extra_hosts maps the openDuT names to 0.0.0.0.
- Setup-String: `docker exec opendut-cleo opendut-cleo generate-setup-string <peer-id>` (positional).
- **Still failing:** with these, EDGAR setup succeeds but netbird-client uses ManagementURL api.netbird.io and the peer stays Disconnected. Unresolved; see the Observed section of [[opendut-quickstart]]. Fall back to native EDGAR or THEO (path B) if it matters.
