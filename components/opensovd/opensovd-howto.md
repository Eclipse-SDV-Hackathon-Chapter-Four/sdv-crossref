---
title: OpenSOVD - how-to recipes
type: howto
component: opensovd
tags: [opensovd, howto, sovd, faults, rust, python, cda, odx, mdd, doctor-whodunit]
status: verified
sources:
  - repos/opensovd-core/examples/server/simple/simple.rs
  - repos/opensovd-core/examples/server/auth/auth.rs
  - repos/opensovd-core/examples/server/auth/sovd_authz.rego
  - repos/opensovd-core/opensovd-providers/src/data/builder.rs
  - repos/opensovd-core/opensovd-providers/src/data/resource.rs
  - repos/opensovd-core/opensovd-cli/mcp/README.md
  - repos/opensovd-cda/README.md
  - repos/opensovd-cda/cda-sovd-interfaces/src/components/ecu.rs
  - repos/opensovd-fault-lib/README.md
  - https://github.com/eclipse-opensovd/odx-converter
  - https://github.com/eclipse-opensovd/opensovd-core/issues/156
  - https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/OpenBSW-Playground/tree/main/OpenBSW-SOVD-Demo
last-verified: 2026-10-03
related:
  - "[[opensovd-overview]]"
  - "[[opensovd-quickstart]]"
  - "[[opensovd-reference]]"
  - "[[opensovd-integration-notes]]"
  - "[[chapter4-challenge-doctor-whodunit]]"
  - "[[vss-kuksa-overview]]"
  - "[[uprotocol-overview]]"
  - "[[openbsw-overview]]"
---

# OpenSOVD - how-to recipes

Recipes for hackathon teams. "Verified" means it was run on 2026-10-03; everything else is marked.

## 1. Expose your own app's faults and data via SOVD (opensovd-core, Rust) - verified
Use this when your vehicle function (e.g. the Battery Thermal Guardian, [[chapter4-challenge-doctor-whodunit]]) is software on an HPC, not a UDS ECU. opensovd-core has no `faults` resource yet (issue #156), so this models a fault as a **`storedData`** item that carries UDS-like status bits. Once #156 lands, move it to `/faults`.

The standalone crate below compiles with stable Rust 1.98 against path dependencies on the cloned repo. The repo itself pins a nightly, but this crate didn't need it. Build time was about 10 s after the deps were cached.

`Cargo.toml` (adjust `R` to your clone path, or use `git = "https://github.com/eclipse-opensovd/opensovd-core"`; the git form is untested):
```toml
[package]
name = "guardian-sovd"
version = "0.1.0"
edition = "2024"

[dependencies]
opensovd-core = { path = "R/opensovd-core" }
opensovd-models = { path = "R/opensovd-models" }
opensovd-providers = { path = "R/opensovd-providers" }
opensovd-server = { path = "R/opensovd-server" }
async-trait = "0.1"
serde = { version = "1", features = ["derive"] }
schemars = "1"
tokio = { version = "1", features = ["net", "rt-multi-thread", "macros", "sync"] }
```
`src/main.rs`:
```rust
//! Battery Thermal Guardian exposed via SOVD `data` (until opensovd-core has `faults`, issue #156).
use std::sync::Arc;

use async_trait::async_trait;
use opensovd_core::{App, Component, DataError};
use opensovd_models::data::DataCategory;
use opensovd_providers::data::{DataProviderBuilder, ReadableDataResource, Value, WriteableDataResource};
use opensovd_server::{Server, Topology};
use serde::{Deserialize, Serialize};
use tokio::{net::TcpListener, sync::RwLock};

/// SOVD-fault-shaped record (UDS status mask semantics: bit0 testFailed, bit3 confirmedDtc).
#[derive(Clone, Default, Serialize, Deserialize, schemars::JsonSchema)]
struct FaultState {
    code: String,
    fault_name: String,
    status_mask: String,
    occurrence_counter: u32,
    first_occurrence: Option<String>,
    last_change: Option<String>,
    evidence: Option<String>,
}

#[derive(Clone)]
struct Shared(Arc<RwLock<FaultState>>);

#[async_trait]
impl ReadableDataResource for Shared {
    type Value = FaultState;
    async fn read(&self) -> Result<FaultState, DataError> {
        Ok(self.0.read().await.clone())
    }
}

#[async_trait]
impl WriteableDataResource for Shared {
    type Value = FaultState;
    async fn write(&self, v: &FaultState) -> Result<(), DataError> {
        *self.0.write().await = v.clone(); // a uProtocol/KUKSA bridge would call this instead of HTTP PUT
        Ok(())
    }
}

struct CellTemp(Arc<RwLock<f64>>);
#[async_trait]
impl ReadableDataResource for CellTemp {
    type Value = Value<f64>;
    async fn read(&self) -> Result<Value<f64>, DataError> {
        Ok(Value::new(*self.0.read().await))
    }
}

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    let stale = Shared(Arc::new(RwLock::new(FaultState {
        code: "BTG001".into(),
        fault_name: "CellTempSignalStale".into(),
        status_mask: "00".into(),
        ..Default::default()
    })));
    let temp = Arc::new(RwLock::new(25.0));

    let provider = DataProviderBuilder::new()
        .data("fault.cell_temp_stale", "Cell temperature signal stale", &DataCategory::StoredData, stale)
        .read_data("cell_temp.max", "Max cell temperature (degC)", &DataCategory::CurrentData, CellTemp(temp))
        .build()?;

    let topology = Topology::new();
    {
        let mut t = topology.write().await;
        t.add_component(Component::new("hpc", "Vehicle HPC"));
        t.add_app(App::new("guardian", "Battery Thermal Guardian").with_component_id("hpc").with_data_provider(provider));
    }
    let server = Server::builder()
        .base_uri("http://127.0.0.1:7691/sovd")?
        .listener(TcpListener::bind("127.0.0.1:7691").await?)
        .topology(topology)
        .build()?;
    server.serve().await?;
    Ok(())
}
```
Run and query (output observed 2026-10-03):
```bash
cargo run &
B=http://127.0.0.1:7691/sovd/v1
curl -s $B/apps/guardian | jq -c
# {"id":"guardian","name":"Battery Thermal Guardian","data":".../apps/guardian/data","is-located-on":".../components/hpc"}
curl -s "$B/apps/guardian/data?categories=storedData" | jq -c
# {"items":[{"id":"fault.cell_temp_stale","name":"Cell temperature signal stale","category":"storedData"}]}
# the detector (or a bridge) publishes a state change; SOVD write envelope is {"data": ...}
curl -s -X PUT $B/apps/guardian/data/fault.cell_temp_stale -H 'Content-Type: application/json' \
  -d '{"data":{"code":"BTG001","fault_name":"CellTempSignalStale","status_mask":"09","occurrence_counter":1,
       "first_occurrence":"2026-10-07T10:00:00Z","last_change":"2026-10-07T10:00:00Z","evidence":"no update for 2.1s (limit 1s)"}}'
# -> 204
curl -s $B/apps/guardian/data/fault.cell_temp_stale | jq -c
# {"id":"fault.cell_temp_stale","data":{"code":"BTG001","evidence":"no update for 2.1s (limit 1s)",...,"status_mask":"09"}}
```
Design notes:
- In a real setup the Guardian or a bridge task calls the shared `RwLock` directly, e.g. on a uProtocol fault event ([[uprotocol-overview]]) or a KUKSA subscription ([[vss-kuksa-overview]]). It doesn't go over HTTP PUT. Leaving the item writable over HTTP lets openDuT/test scripts **forge** diagnostic truth. Use `read_data` for the fault in the final version, or add `JwtAuthenticator` + `RegorusAuthorizer` (recipe 5).
- Use UDS status-bit semantics (`0x01` testFailed, `0x08` confirmedDtc, `0x04` pendingDtc) so the same evidence parser works against CDA faults (recipe 3).
- Entity choice: `apps/guardian` hosted on `components/hpc` follows the OpenSOVD design topology (`apps/FaultManager`, `apps/App1`) in [design.md](../../repos/opensovd-main/docs/design/design.md).
- Every value is returned with a JSON schema on `?include-schema=true`. The evidence factory can archive that schema with each record.

## 2. Implement the real `faults` resource upstream (contribution idea, not done)
Issue [#156](https://github.com/eclipse-opensovd/opensovd-core/issues/156) already sketches it. Mirror `DataProvider` (`opensovd-core/src/data.rs`) with a `FaultProvider { list(filter), read(code) }`, add a builder in `opensovd-providers`, and add routes in `opensovd-server/src/routes/` for `GET {entity}/faults` and `GET {entity}/faults/{code}`. A `DELETE` would be needed for "clear DTC" (an MVP use case). Copy the JSON shape the CDA already returns (`code`, `scope`, `fault_name`, `severity`, `status{...,mask}`, `environment_data`) so clients can treat core and CDA the same way (convergence issue CDA #553). Talk to the assignee (akshaim) and the Core workstream (ask the coaches for OpenSOVD) before starting. Size: 1-2 days for someone fluent in axum. Tests go in `opensovd-server/tests/routes.rs` style and `tests/` pytest.

## 3. Read and clear faults of a UDS ECU through the CDA - verified
See [[opensovd-quickstart]] recipe B for setup. The fault API (from `cda-sovd-interfaces/src/components/ecu.rs`):
- `GET /vehicle/v15/components/{ecu}/faults` maps to UDS 0x19. Query params: `status[<key>]=true|1` (keys `confirmedDtc`, `pendingDtc`, `testFailed`, `mask`, ...; repeat = OR), `severity`, `scope`, `include-schema`, `memoryselection`.
  Observed: the status filter did **not** narrow the list in our run. Filter client-side on `.status.mask`.
- `GET .../faults/{code}` returns the detail. Use `include-extended-data`, `include-snapshot-data` for environment data.
- `DELETE .../faults` (optionally `?scope=`) maps to UDS 0x14. It **requires a lock**: `POST .../locks {"lock_expiration":60}` first, otherwise you get 409 `lock-required`.
- Status object: `test_failed, test_failed_this_operation_cycle, pending_dtc, confirmed_dtc, test_not_completed_since_last_clear, test_failed_since_last_clear, test_not_completed_this_operation_cycle, warning_indicator_requested, mask` (hex string).
- The simulator's control API (`:8181`, not SOVD) injects DTCs: `PUT /{ECU}/dtc/{Standard|Development}` with `{"id":"01E240","statusMask":"09"}`, and `DELETE /{ECU}/dtc/Standard`. It also has `POST /disconnect` and per-ECU `interceptor` routes for simulating DoIP disruptions ([WebserverRoutes.kt](../../repos/opensovd-cda/testcontainer/ecu-sim/src/main/kotlin/webserver/WebserverRoutes.kt)). These are handy L3-style fault injection hooks for a demo.

## 4. Put your own ECU behind the CDA (ODX -> MDD) - not run
1. Get an ODX/PDX for the ECU. For a hackathon, generate it: the CDA repo builds its test ECUs with `odxtools` Python scripts (`testcontainer/odx/*.py`, `generate_docker.sh`). The HackFest OpenBSW demo generated an MDD from an ECU JSON description (`real-sovd-cda/odx-gen`), and `bburda42dot/diag-converter` (in the demo repo) converts ODX <-> YAML <-> MDD in Rust ([https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/OpenBSW-Playground/tree/main/OpenBSW-SOVD-Demo](../../https://github.com/Eclipse-SDV-HackFest-Esslingen-2026/OpenBSW-Playground/tree/main/OpenBSW-SOVD-Demo)).
2. Convert with odx-converter (Kotlin): `java -jar converter/build/libs/converter-all.jar convert -O out/ MYECU.pdx`. **You must supply the ODX XSD yourself** (copyright NOTICE in the converter repo).
3. Start the CDA with `-d out/ -t <tester-ip> --protocol-name UDS_Ethernet_DoIP` (off-board) or the default `UDS_Ethernet_DoIP_DOBT` (in-vehicle). The protocol name must exist in the MDD, otherwise the ECU is skipped (seen in the quickstart).
4. Naming rules: the DiagLayerContainer short name, lowercased, becomes the component id. Service names have `_Read/_Write/_Dump` stripped for `data`, `_Start/_Stop/_RequestResults` stripped for `operations`, and the varcoding class goes to `configurations` ([CDA README](../../repos/opensovd-cda/README.md)).
5. OpenBSW as the ECU: use the HackFest overlay. The upstream OpenBSW DoIP server needed a fix to handle diagnostic message ACK payloads (0x8002/0x8003) before the CDA could talk to it, and 0x19/0x14 DTC services were added as an overlay ([[openbsw-overview]]).

## 5. Secure the gateway (JWT + Rego) - not run
`examples/server/auth/auth.rs` wires `JwtAuthenticator::new(JwtAlgorithm::HS512, SECRET, ISSUER)` and `RegorusAuthorizer` with `sovd_authz.rego` (role -> methods + glob paths, e.g. `/sovd/v1/apps/**`) and `sovd_data.json`. Failed authentication gives 401 with an empty body. Failed authorization gives 403 with `insufficient-access-rights` ([architecture.md](../../repos/opensovd-core/docs/architecture.md)). mTLS: the gateway flags `--tls-cert/--tls-key/--tls-client-ca`. Run with `cargo run -p opensovd-examples-server --example auth` (not built or run here; the sibling `simple` example built fine on 2026-10-03).

## 6. Evidence factory: poll SOVD and build a fault timeline (Python sketch, not run)
```python
import time, json, requests
SOVD = "http://127.0.0.1:7691/sovd/v1"           # or CDA: http://127.0.0.1:20002/vehicle/v15 + Bearer token
ITEMS = [("apps/guardian", "fault.cell_temp_stale")]
last = {}
with open("sovd_timeline.jsonl", "a") as out:
    while True:
        for ent, item in ITEMS:
            r = requests.get(f"{SOVD}/{ent}/data/{item}", timeout=2).json()["data"]
            key = (ent, item)
            if last.get(key) != r.get("status_mask"):
                out.write(json.dumps({"t": time.time(), "entity": ent, "item": item,
                                      "status_mask": r.get("status_mask"), "record": r}) + "\n")
                out.flush(); last[key] = r.get("status_mask")
        time.sleep(0.2)
```
Join each line with the openDuT campaign step (injection time) and the uProtocol fault/mitigation events on a shared clock. Detection latency is `t(SOVD mask & 0x01) - t(injection)`. The verdict passes if detection and mitigation both happen within the hazard's fault-tolerant time. SOVD is the **independent oracle**: the evidence collector shouldn't trust the Guardian's own log alone ([[chapter4-challenge-doctor-whodunit]]). Polling at 200 ms is fine for a demo. Core has no SOVD subscriptions/events yet.

## 7. Let an AI agent explore the vehicle (MCP) - not run
`docker run -i --rm --network=host ghcr.io/eclipse-opensovd/opensovd-mcp --url http://localhost:7690/sovd/v1`. Tools: `list_components`, `list_areas`, `list_apps`. Resource: `sovd://topology` ([MCP README](../../repos/opensovd-core/opensovd-cli/mcp/README.md)). It only covers topology today, so adding data/fault tools is a small contribution. The HackFest teams also showed AI chat + MCP diagnostics.

## 8. Fault-lib -> DFM over iceoryx2 - verified (with a README correction)
The [fault-lib README](../../repos/opensovd-fault-lib/README.md) says to run `cargo run -p dfm_lib --example dfm` and then the reporter. **That doesn't work as written.** The `dfm` example runs a few `SovdFaultManager` queries and exits within about 1 s. The reporter then panics with `FaultApi initialization failed: CatalogVerification(Timeout)` (observed 2026-10-03). Use the standalone binary instead:
```bash
cd repos/opensovd-fault-lib            # stable Rust, cold build of both ~15 s on 32 cores (git deps: iceoryx2 rev eba5da4, S-CORE persistency rust_kvs)
cargo run -p dfm_bin -- --catalog-dir src/fault_lib/tests/data --storage-dir /tmp/dfm-store &
#  INFO dfm_bin: Loaded catalog 'hvac' ... (2 faults) / 'ivi' ... (2 faults)
#  INFO dfm_bin: Starting DFM with query server (4 faults across 2 catalogs) / DFM ready
cargo run -p fault_lib --features testutils --example tst_app -- -c src/fault_lib/tests/data/hvac_fault_catalog.json
#  DFM log: Received hash ... / Received new fault ID: Text("hvac.blower.speed_sensor_mismatch") / process_record{path="hvac"} ...
#  tst_app: End Basic fault library example (exit 0, ~4 s)
```
The DFM also logs a recurring `error: get_value could not find key: hvac` from the KVS on first access. It looks harmless.
Fault catalogs are JSON (`id` Numeric/Text, `name`, `category`, `severity`, `compliance` [EmissionRelevant/SecurityRelevant/SafetyCritical], reporter/manager-side debounce and reset policies). The DFM exposes faults as `SovdFault` records (code, fault_name, severity, UDS status flags plus mask, occurrence/aging/healing counters, first/last occurrence) through `SovdFaultManager::get_all_faults(path)` / `get_fault` / `delete_*`, and over iceoryx2 via `DfmQueryServer`, **not over HTTP**. The missing piece is a bridge from that into recipe 1 or 2 (a `FaultProvider` backed by a DFM query client) ([[iceoryx2-overview]], [[s-core-overview]]).

## Observed on 2026-10-03 (verifier)
Scope: only recipe 8 was re-run by the verifier (status `verified` reflects that run; the other recipes keep their own markers in their headings). Commands exactly as written; cold build of dfm_bin + tst_app took 13.6 s, whole run 31 s.
```
dfm_bin: Loaded catalog 'hvac' ... (2 faults) / 'ivi' ... (2 faults)
dfm_bin: Starting DFM with query server (4 faults across 2 catalogs) / DFM ready
dfm_lib::fault_lib_communicator: Received new fault ID: Text("hvac.blower.speed_sensor_mismatch")
error: get_value could not find key: hvac   (twice, harmless)
tst_app: End Basic fault library example   (exit 0, ~4 s)
```
