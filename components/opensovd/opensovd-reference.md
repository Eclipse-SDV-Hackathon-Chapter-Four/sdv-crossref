---
title: OpenSOVD - reference (repos, versions, endpoints, config)
type: reference
component: opensovd
tags: [opensovd, reference, sovd, api, endpoints, cda, rust]
status: draft
sources:
  - https://github.com/eclipse-opensovd
  - https://github.com/eclipse-opensovd/opensovd-core/issues
  - https://www.iso.org/standard/86587.html
  - repos/opensovd-core/opensovd-server/src/routes/
  - repos/opensovd-core/opensovd-cli/gateway/README.md
  - repos/opensovd-core/docs/architecture.md
  - repos/opensovd-cda/README.md
  - repos/opensovd-cda/cda-sovd/src/sovd.rs
  - repos/opensovd-cda/docs/03_architecture/02_sovd-api/02_sovd-api.rst
  - repos/opensovd-cda/opensovd-cda.toml
last-verified: 2026-10-03
related:
  - "[[opensovd-overview]]"
  - "[[opensovd-quickstart]]"
  - "[[opensovd-howto]]"
  - "[[opensovd-integration-notes]]"
---

# OpenSOVD - reference

## Repos looked at (shallow clones in `repos/`)
| Local path | Upstream | Commit (date) | Notes |
|---|---|---|---|
| repos/opensovd-main | eclipse-opensovd/opensovd | e769a39 (2026-06-29) | design.md, mvp.md, ADR-001 (fault-lib = S-CORE interface), weekly forum .ics |
| repos/opensovd-core | eclipse-opensovd/opensovd-core | e25fa30 (2026-10-02) | workspace v0.1.1, edition 2024, toolchain `nightly-2026-05-07` |
| repos/opensovd-cda | eclipse-opensovd/classic-diagnostic-adapter | e6f4b8f (2026-10-02) | CDA 0.1.0, MSRV 1.88 (CI clippy nightly-2025-07-14) |
| repos/opensovd-fault-lib | eclipse-opensovd/fault-lib | 12dac50 (2026-10-01) | Cargo + Bazel, iceoryx2 git rev eba5da4, S-CORE `rust_kvs` |
| repos/opensovd-demo | eclipse-opensovd/demo | bd0f79e (2026-04-28) | cda-oauth demo (OCA 2026), submodule diag-converter (not fetched) |
Not cloned: odx-converter (Kotlin), uds2sovd-proxy (README only), mdd-ui (~1.4 GB), cpp-bindings (empty), dlt-tracing-lib, mbedtls-rs, website, cicd-workflows. See [https://github.com/eclipse-opensovd](../../https://github.com/eclipse-opensovd).

Container images: `ghcr.io/eclipse-opensovd/opensovd-gateway` (latest/nightly/vX.Y.Z), `ghcr.io/eclipse-opensovd/opensovd-mcp`. **No CDA image.**

## opensovd-core crates
`opensovd-core` (Topology, entities Component/App/Area, `DataProvider`, `BulkDataProvider` traits), `opensovd-models` (SOVD JSON models; `DataCategory` = identData/currentData/storedData/sysInfo/`x-…` custom), `opensovd-providers` (`DataProviderBuilder`, `Constant`, `ReadableDataResource`/`WriteableDataResource`, `Value<T>` envelope), `opensovd-server` (axum `Server::builder()`, `Authenticator`/`Authorizer`, TCP/Unix/abstract-socket listeners, optional TLS), `opensovd-client` (Rust client), `opensovd-extra` (JWT, Rego via regorus, TLS helpers), `opensovd-mocks`, `opensovd-cli/{gateway,mcp}`, `examples/{server/{simple,auth,bulkdata,mtls,systemd},client}`. Tests: Rust plus pytest/Bruno under `tests/` ([architecture.md](../../repos/opensovd-core/docs/architecture.md)).

## opensovd-core HTTP API (base `http://<host>:7690/sovd`; routes from `opensovd-server/src/routes/`)
| Method | Path | Notes |
|---|---|---|
| GET | `/version-info` | `sovd_info[{version:"1.1.0", base_uri, vendor_info}]` |
| GET | `/v1/` | root capabilities (links to areas/components/apps) |
| GET | `/v1/{areas,components,apps}` | `{"items":[{id,name,href,tags,translation_id}]}` |
| GET | `/v1/areas/{id}`, `/v1/areas/{id}/contains` | |
| GET | `/v1/components/{id}`, `/v1/components/{id}/hosts` | capabilities include `variant`, `belongs-to` |
| GET | `/v1/apps/{id}` | includes `is-located-on` |
| GET | `/v1/{components,apps}/{id}/data` | list; filters by categories/groups/tags (`?categories=storedData` worked) |
| GET | `/v1/{components,apps}/{id}/data-categories`, `/data-groups` | |
| GET / PUT | `/v1/{components,apps}/{id}/data/{data_id}` | `?include-schema=true`; PUT body `{"data": <value>}` -> 204; read-only -> 400 |
| GET / POST / DELETE | `/v1/{entity-collection}/{entity-id}/bulk-data[/{category}[/{id}]]` | upload/download files, max body 1 GiB |
| - | faults, operations, configurations, modes, locks, logs, updates | **not implemented** (404). Issues: faults #156, update #195, data/docs #92, mDNS #31, diagnostic-lib #58 |
Errors: `{"error_code": "...", "vendor_code"?: "...", "message": "..."}`. 401 has an empty body. 403 returns `insufficient-access-rights`.

Gateway flags: `--url` (default `http://localhost:7690/sovd`), `--unix-socket` (`@name` = abstract), `--mock`, `--serve-dir PATH:DIR`, CORS (`--cors-origin` etc.), TLS (`--tls-cert`, `--tls-key`, `--tls-client-ca`, `--tls-client-auth required|optional`). TLS is a separate cargo feature, so the gateway accepts a JWT (`--auth-jwt-key`) over plain `http://`; core's `JwtAuthenticator` takes HS512/RS512 only and sets `validate_aud = false` ([[verify-offline-against-a-pinned-root]]). Env `SOVD_URL` in the image ([gateway README](../../repos/opensovd-core/opensovd-cli/gateway/README.md)).

## CDA HTTP API (base `http://<host>:20002/vehicle/v15`; from `/openapi.json` observed on 2026-10-03)
| Path | Methods (observed or from source) | UDS mapping |
|---|---|---|
| `/health`, `/health/ready` | GET (ready -> 204) | - |
| `/swagger-ui`, `/openapi.json` | GET | - |
| `/vehicle/v15/authorize` | POST `{client_id, client_secret}` -> `{access_token}` | - (default plugin accepts anything; without the `auth` feature JWTs are read with `jsonwebtoken::dangerous::insecure_decode`, no signature check, see [[verify-offline-against-a-pinned-root]]) |
| `/vehicle/v15/components` | GET (extra keys `x-sovd2uds-can-ecus`, `x-sovd2uds-lin-ecus`) | - |
| `/components/{ecu}` | GET (variant: name, state Online/Offline/NotTested/Duplicate/Disconnected/NoVariantDetected, logical_address, `last_seen`); PUT = force variant detection | variant detection |
| `/components/{ecu}/data`, `/data/{id}`, `/data/{id}/docs`, `/data-categories` | GET, PUT | 0x22 / 0x2E |
| `/components/{ecu}/configurations[/{id}]` | GET, PUT | 0x22/0x2E (varcoding class) |
| `/components/{ecu}/operations/{op}/executions[/{id}]` | POST, GET, DELETE | 0x31 start/stop/results |
| `/components/{ecu}/faults`, `/faults/{code}` | GET (status/severity/scope filters), DELETE (needs lock) | 0x19 / 0x14 |
| `/components/{ecu}/modes/{session,security,commctrl,dtcsetting}` | GET, PUT | 0x10, 0x27/0x29 (both map to `modes/security`, cda-interfaces/src/lib.rs), 0x28, 0x85 |
| `/components/{ecu}/locks[/{id}]`, `/vehicle/v15/locks` (vehicle lock), `/functions/functionalgroups/{g}/locks` | POST, GET, DELETE | - |
| `/components/{ecu}/genericservice` | raw UDS passthrough | any |
| `/components/{ecu}/x-single-ecu-jobs[/{job}]` | ODX single-ECU jobs | - |
| `/components/{ecu}/x-sovd2uds-download/{requestdownload,flashtransfer,transferexit}` | flashing | 0x34/0x36/0x37 |
| `/components/{ecu}/x-sovd2uds-bulk-data/mdd-embedded-files` | files embedded in MDD | - |
| `/components/{ecu}/operations/comparam/executions` | change communication parameters | - |
| `/vehicle/v15/functions/functionalgroups/{g}[/operations/{op}...]` | functional (broadcast) communication | functional addressing |
| `/vehicle/v15/apps/sovd2uds/{bulk-data/flashfiles, bulk-data/runtimefiles-*, data/networkstructure, data/version, operations/runtimefilesupdate/executions}` | CDA self-management, runtime MDD update | - |
CLI: `-c/--config` (env `CDA_CONFIG_FILE`), `-d/--databases-dir`, `-t/--tester-address`, `--tester-subnet`, `--gateway-port` (13400), `--protocol-name` (`UDS_Ethernet_DoIP_DOBT` default, or `UDS_Ethernet_DoIP` off-board), `--listen-address`, `--listen-port` (20002), `--unix-socket`, `-f/--flash-files-path`, `--file-logging`, `--exit-no-database-loaded`, `--fallback-to-base-variant`, `--mdd-decompress`. `opensovd-cda generate-config -o -` prints a fully commented TOML. Transports: DoIP (TLS through patched mbedtls), CAN via `socketcand:` interface (feature `can-socketcand`). Plugins: security (default/JWT), lock-priority, runtime-update, communication-management. Health crate. DLT tracing.

## Data model snippets (observed)
CDA fault:
```json
{"code":"01E240","scope":"FaultMem","fault_name":"DTC Code 1","severity":0,
 "status":{"test_failed":true,"test_failed_this_operation_cycle":false,"pending_dtc":false,"confirmed_dtc":true,
           "test_not_completed_since_last_clear":false,"test_failed_since_last_clear":false,
           "test_not_completed_this_operation_cycle":false,"warning_indicator_requested":false,"mask":"09"}}
```
Detail adds `"environment_data":{"extended_data_records":{...},"snapshots":{...}}`.
DFM `SovdFault` (fault-lib) has the same status flags (keys `confirmedDTC`, `pendingDTC`, `mask:"0x00"` as strings), plus `occurrence_counter`, `aging_counter`, `healing_counter`, `first_occurrence`, `last_occurrence`, `symptom` (`src/dfm_lib/src/sovd_fault_manager.rs`). **The casing and mask formats differ between the CDA and the DFM**, so a shared model is still to be defined (#553). The confirmed flag is spelled three ways (CDA JSON `confirmed_dtc`, CDA filter key `confirmedDtc`, DFM `confirmedDTC`); the hex `mask` is the only safe join key ([[a-fault-is-a-state-machine-with-evidence-attached]]).

## Standard
- ISO 17978-1:2026 (general), ISO 17978-3:2026 (API). Derived from ASAM SOVD 1.0/1.1. opensovd-core reports `version: "1.1.0"` ([https://www.iso.org/standard/86587.html](../../https://www.iso.org/standard/86587.html)).
- Related: ISO 14229 (UDS), ISO 13400 (DoIP), ISO 22901 (ODX; the converter README says ISO-22091; the ODX standard number is ISO 22901, so treat the README number as a typo, unverified).

## Community
- Weekly Forum Mondays 11:30-12:30 CET (.ics in repos/opensovd-main). Slack `#eclipse-opensovd` on the SDV WG workspace. Minutes in GitHub Discussions.
- S-CORE x OpenSOVD workshop 2026-05-04 (discussion #103): fault-lib and diag-lib on the SOVD server, "http-ipc" planned, S-CORE integrates via `inc_diagnostics` (still a template README on 2026-10-03), first use case version readout ([https://github.com/eclipse-opensovd/opensovd-core/issues](../../https://github.com/eclipse-opensovd/opensovd-core/issues)).
- Kickoff video: https://www.youtube.com/watch?v=VnMauUXT2cI. Project page: https://projects.eclipse.org/projects/automotive.opensovd. CDA docs: https://eclipse-opensovd.github.io/classic-diagnostic-adapter/.

## ISO 17978-3 resource catalogue vs OpenSOVD (names only; added 2026-10-03)

The standard text is paywalled, but its resource catalogue is public knowledge through ASAM SOVD and the open implementations. Use this to answer "what does a complete SOVD server need?" and to size freestyle items ([[gap-register]] section H). "core" = opensovd-core v0.1.1 gateway; "CDA" = classic-diagnostic-adapter.

| Resource collection (per entity unless noted) | Purpose | core | CDA | Notes |
|---|---|---|---|---|
| `/version-info` (root, version-independent) | list supported API versions | yes | yes | |
| `{path}/docs` capability description (OpenAPI 3.1 scoped to path) | self-description | no (#92) | Swagger UI | mandatory in the standard |
| entity discovery: `components`, `areas`, `apps`, `functions` + relations (`subcomponents`, `subareas`, `contains`, `hosts`, `depends-on`) | topology | yes (partial relations) | components, functional groups | `related-apps`/`related-components` are deprecated names |
| tags (`?tags=` filters, `x-sovd-tags`) | filtering | no | no | |
| `data`, `data-categories`, `data-groups`, `data-lists` | read/write values; data-lists read several at once | data + categories + groups | data (0x22/0x2E) | writes are whole-resource only |
| `faults` (list, read with environment data, delete one/all) | DTC-like records | **no (#156)** | yes (0x19/0x14) | status filters such as `status[confirmedDTC]` |
| `cyclic-subscriptions` (SSE) | periodic push of a resource | no | no | 201 + Location; `Accept: text/event-stream` on the subscription itself |
| `triggers` (SSE / log / command on EnterRange, LeaveRange, OnChange, OnChangeTo) | event hooks | no | no | the standard's evidence mechanism |
| `configurations` (read, write, reset one/all) | coding / parameters | no | yes (varcoding) | |
| `clear-data` (cached, learned, client-defined) | resets | no | no | |
| `operations` + `executions` (start, status, terminate, control) | routines, I/O control, async jobs | no | yes (0x31; single-ECU jobs) | 202 + Location for long-running |
| `scripts` + executions | uploadable scripts | no | no | |
| `modes` (`session`, `security`, `comm-ctrl`, `dtcsetting`) | UDS-mapped state | no | yes | hint-based control via `x-sovd-mode` header |
| `locks` (acquire with expiry, modify, release, breakable) | concurrency | no | yes | lock-broken → 409; contention → 423 when a priority plugin is registered, else 409: treat both as stop ([[lock-before-clear-and-expect-it-to-break]]) |
| `/updates` (root: register, read, prepare, execute, automated, status, delete) | software update | no (#195) | flashing via `x-sovd2uds-download` extension | phase + status body; 409 when another update runs |
| `status` (read, start, restart, force-restart, shutdown, force-shutdown) | entity lifecycle | no | restart via ECU reset mapping | `operations/ecureset` mapping is deprecated |
| `bulk-data` (categories, download/upload, delete, optional signature) | files, logs, flash files | yes | yes | |
| `logs` (entries, config read/write/reset) | HPC logging (RFC 5424 / DLT) | no | no | entries retrieved via bulk-data |
| `communication-logs` | dev/QA tracing | no | no | |
| `/authorize`, `/token` (informative) | auth bootstrap | JWT + Rego hooks | demo-only auth | OAuth2/OIDC recommended |
| discovery: mDNS (RFC 6762) + DNS-SD (RFC 6763), service `_sovd._tcp`, port 7690, `<id>.local`, TXT `accessurl` (https) | co-located discovery | no (#31) | no | mandatory use case; TLS and discovery are one gap |
| extension rule: custom names use `x-<ext>-…`; `x-sovd-` is reserved | conformance | n/a | `x-sovd2uds-*` | disclose extensions where a scanner can list them |

Deprecated and best avoided in new code: `related-apps`, `related-components`, `Fault.schema`, `x-sovd-lock-required`, `x-sovd-required-modes`, `x-sovd-capabilities`, the `operations/ecureset` mapping. Status codes are the plain RFC 9110 set (200/201/202/204/400/401/404/405/406/409/415/500/501/503/504); 403 and 502 are reasonable additions for security-denied and ECU-failure negative responses.


## Observed on 2026-10-03 (verifier): CAN transport
Documented and works on vcan0 rootless. Crate `repos/opensovd-cda/cda-comm-can` (`src/config.rs`, `src/gateway/*`) uses ISO-TP via `tokio-socketcan-isotp`; interface schemes are a plain name (kernel `can_isotp` module, which is NOT loaded on this host), `rawcan:<ifname>` (userspace ISO-TP over raw CAN, vcan suffices; cargo feature `can-isotp-userspace`) and `socketcand:<host>:<port>:<bus>` (feature `can-socketcand`). The release binary built earlier had no CAN support. Example config: `repos/opensovd-cda/opensovd-cda-can.toml`.
Recipe (rebuild 1 min incremental): `cd repos/opensovd-cda && CARGO_BUILD_JOBS=8 cargo build --release -p opensovd-cda --features can-isotp-userspace`. Config used: `components/opensovd/examples-can-vcan0/cda-can-vcan0.toml`: `[doip] enabled=false`, `[can] interface="rawcan:vcan0"`, `[[can.ecu_mappings]] ecu_name="OpenBSW" request_id=0x7E0 response_id=0x7E8`, `[[can.transport_overrides]] transport="can"`, `[ecu.OpenBSW] protocol="UDS_Ethernet_DoIP"` (the Playground MDD only has that protocol; the CAN alias list does not match it). Run from a scratch dir with `mdds/OpenBSW.mdd` (from `repos/hackfest-OpenBSW-Playground/.../odx-gen/`): `CDA_CONFIG_FILE=cda-can.toml opensovd-cda`.
Observed: component `openbsw` Online (logical_address 0x2a), `POST /vehicle/v15/authorize` returns a JWT with any client_id/secret; `GET .../data/StaticData` -> 16 bytes via ISO-TP multi-frame (FF `7E8#101B62CF01..`, CDA sends flow control `7E0#30000000`, CFs 21-23); `data/ADC_Value` -> 0; `data/Identification` and `VehicleSpeed` -> NRC 0x31 (DIDs F100/CF12 not implemented by this ECU); `GET .../faults` -> `7E0#190 2FF` answered `7E8#0759 02FF 123456 09` (DTC 0x123456 status 0x09), but CDA returns 400 "No DTC with code 123456 found in DTC references" (the demo MDD has no such DTC). CDA also sends functional `7DF#023E80` TesterPresent every 2 s (keepalive) and probes `7E0#023E00` and `#22F100` at startup (variant detection fails: no SESSION state chart in the MDD, harmless). Evidence: `components/opensovd/examples-can-vcan0/candump-cda-over-vcan0.log`. Not run: DoIP over tap0 (needs root).
