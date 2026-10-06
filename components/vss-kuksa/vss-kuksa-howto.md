---
title: VSS + KUKSA how-to recipes
type: howto
component: vss-kuksa
tags: [kuksa, databroker, jwt, tls, provider, actuation, overlay, ankaios]
status: verified
sources:
  - repos/kuksa-databroker/doc/user_guide.md
  - repos/kuksa-databroker/doc/authorization.md
  - repos/kuksa-databroker/doc/protocol.md
  - repos/kuksa-databroker/jwt/README.md
  - repos/kuksa-proto/kuksa/val/v2/val.proto
  - repos/kuksa-python-sdk/kuksa-client/kuksa_client/grpc/__init__.py
  - repos/vehicle_signal_specification/docs-gen/content/extensions/overlay.md
  - repos/ankaios/doc/docs/usage/tutorial-vehicle-signals.md
  - repos/hc3-ArBytesMoral/compute/ankaios.yaml
  - https://github.com/eclipse-kuksa/kuksa-csv-provider
last-verified: 2026-10-03
related:
  - "[[vss-kuksa-quickstart]]"
  - "[[vss-kuksa-reference]]"
  - "[[ankaios-overview]]"
  - "[[uprotocol-overview]]"
---

# VSS + KUKSA how-to

All recipes assume the `kuksa` docker network from [[vss-kuksa-quickstart]]. Recipes marked **(ran)** were executed on 2026-10-03 against databroker 0.7.1.

## 1. Enable JWT authorization (ran)
Authorization is **off unless `--jwt-public-key` is given**. The broker logs `WARN Authorization is not enabled.` Example keys and tokens are in the databroker repo (the tokens expire in 2029: `"exp": 1861919999`).
```sh
git clone --depth 1 https://github.com/eclipse-kuksa/kuksa-databroker && cd kuksa-databroker
docker run -d --rm --name Auth --network kuksa -v $PWD/certificates:/opt/kuksa:ro \
  ghcr.io/eclipse-kuksa/kuksa-databroker:0.7.1 --insecure --jwt-public-key /opt/kuksa/jwt/jwt.key.pub
CLI="docker run --rm -it --network kuksa -v $PWD/jwt:/t:ro ghcr.io/eclipse-kuksa/kuksa-databroker-cli:0.7.1 --server Auth:55555"
$CLI get Vehicle.Speed                                                  # [get]  Unauthenticated  No auth token provided
$CLI --token-file /t/read-vehicle-speed.token get Vehicle.Speed         # [get]  OK  Vehicle.Speed: NotAvailable
$CLI --token-file /t/read-vehicle-speed.token get Vehicle.Cabin.Light.IsDomeOn   # code 403 "Permission denied for some entries"
$CLI --token-file /t/read-vehicle-speed.token publish Vehicle.Speed 10  # code 403 "Access was denied for Vehicle.Speed"
$CLI --token-file /t/provide-all.token publish Vehicle.Speed 10         # [publish]  OK
```
Scope grammar (doc/authorization.md): the space-separated `scope` claim holds `read`, `actuate`, `provide`, `provide:data`, `provide:actuation` and `create`, optionally followed by `:<VSS path or branch>`. Examples: `read:Vehicle.Speed`, `actuate:Vehicle.ADAS`, `provide:Vehicle.Cabin.ChildPresence`. `actuate` and `provide` include `read`. The audience must be `kuksa.val`. RS256 is supported, and ES256/EdDSA since 0.7.0. New tokens are created with the helper scripts in eclipse-kuksa/kuksa-common/jwt (repos/kuksa-databroker/jwt/README.md). In Python: `VSSClient(host, port, token=...)`, or call `client.authorize(token)`.

## 2. Enable TLS
```sh
docker run --rm -it --name Server --network kuksa -v $PWD/certificates:/opt/kuksa \
  ghcr.io/eclipse-kuksa/kuksa-databroker:0.7.1 --tls-cert /opt/kuksa/Server.pem --tls-private-key /opt/kuksa/Server.key
docker run --rm -it --network kuksa -v $PWD/certificates:/opt/kuksa ghcr.io/eclipse-kuksa/kuksa-databroker-cli:0.7.1 \
  --server https://Server:55555 --ca-cert /opt/kuksa/CA.pem
```
Use `https://` in the client URL. With `http://` you get `h2 protocol error: ... frame with invalid size` (doc/user_guide.md, Troubleshooting). The example cert is issued for the host name `Server`, so name the container `Server` or set the TLS server name in the client. Not run by us.

## 3. Write an actuation provider with kuksa.val.v2 (ran)
In v2 an application calls `Actuate`. The broker forwards the request to the **one** provider that registered for that signal over `OpenProviderStream`. If no provider is registered, `Actuate` fails with `UNAVAILABLE` (observed: `Provider for vss_id 184 does not exist`).

Provider (Python SDK 0.6.0). Note that the requested value arrives in `entry.actuator_target`, **not** `entry.value`:
```python
from kuksa_client.grpc import VSSClient, Datapoint
P = 'Vehicle.Cabin.ChildPresence.AlertLevel'   # from the overlay in the quickstart
with VSSClient('127.0.0.1', 55556) as c:
    for updates in c.v2_subscribe_actuation_requests([P]):
        for u in updates:
            print('PROVIDER got actuation request:', u.entry.path, u.entry.actuator_target.value)
            c.set_current_values({P: Datapoint(u.entry.actuator_target.value)})  # report the new actual value
```
Consumer: the Python SDK 0.6.0 has **no v2 `Actuate` wrapper**, so use the raw stubs that ship inside the `kuksa-client` wheel:
```python
import grpc
from kuksa.val.v2 import val_pb2, val_pb2_grpc, types_pb2
stub = val_pb2_grpc.VALStub(grpc.insecure_channel('127.0.0.1:55556'))
stub.Actuate(val_pb2.ActuateRequest(signal_id=types_pb2.SignalID(path='Vehicle.Cabin.ChildPresence.AlertLevel'),
                                    value=types_pb2.Value(string='REMOTE')))
```
Observed: `Actuate OK`. The provider printed `PROVIDER got actuation request: Vehicle.Cabin.ChildPresence.AlertLevel REMOTE`. A `GetValue` issued immediately afterwards was still empty, because the provider publishes asynchronously. **Subscribe instead of reading back right away.**

## 4. Do not mix v1 "target value" with v2 actuation (ran)
Using the same broker and provider as in recipe 3, `client.set_target_values({...AlertLevel: 'EMERGENCY_CALL'})` (v1) **returned OK but the v2 provider never received it**. Afterwards `get_current_values` returned `REMOTE` and `get_target_values` returned `EMERGENCY_CALL`. Likewise `databroker-cli actuate ...` (v1) returns `[actuate] OK` even when no provider exists. This matches doc/protocol.md: "Target Value and Actuation Value … are handled as separate channels" and "Do not mix different versions of APIs for providers and clients".
Rule for teams: **pick v2 end-to-end for anything with actuators.**

## 5. Subscribe to changes
- v2: `Subscribe(signal_paths=[...])` streams `entries` maps. Python: `for upd in c.subscribe_current_values([...])` or `c.v2_subscribe(...)` (repos/kuksa-python-sdk/kuksa-client/kuksa_client/grpc/__init__.py).
- Change types: since 0.4.2, sensors and actuators default to `continuous` (every publish notifies) and attributes to `static`. Add `x-kuksa-changetype: onchange` to a node in your overlay to suppress duplicate notifications (doc/user_guide.md). A *stuck-value* detector should therefore watch timestamps, because with `onchange` a frozen sensor is silent.

## 6. Overlays: add, change, delete, instantiate
Overlay rules are in repos/vehicle_signal_specification/docs-gen/content/extensions/overlay.md:
- Pass any number of `-l file.vspec`. **Order matters**: later overlays win.
- New branches must hook onto an existing branch. Implicit branches are not allowed.
- When changing an existing node, you may omit `type`/`datatype`. Glob `*` keys are allowed.
- `delete: true` on a node removes it, for example to trim the tree to your vehicle.
- Custom keys (such as `x-kuksa-changetype` or CAN mapping `dbc:` blocks) must be whitelisted with `-e <key>` / `--extended-attributes` on `vspec export`, otherwise they are flagged (an error with `--strict`, which the VSS Makefile uses). The flag names were confirmed in `vspec export json --help` on vss-tools 6.1.0.
- Profiles: repos/vehicle_signal_specification/overlays/profiles/motorbike.vspec shows how to reshape the car tree into a different vehicle type. repos/vehicle_signal_specification/overlays/extensions/ holds the OBD and dual-wiper extensions.

## 7. Feed data without hardware
- **CSV provider** (replay): `docker run -it --rm --net=host ghcr.io/eclipse-kuksa/kuksa-csv-provider/csv-provider:main`, or natively `python3 provider.py -f signals.csv -i`. CSV columns: `field,signal,value,delay`. It **does not support auth** (https://github.com/eclipse-kuksa/kuksa-csv-provider). Good for scripted CPD or thermal scenarios.
- **CAN provider**: DBC + VSS mapping JSON. It can replay a candump log without real CAN and has dbc2val and val2dbc modes.
- Your own provider: about 10 lines of Python with `set_current_values` in a loop. Use v2 `OpenProviderStream` (`ProvideSignalRequest`) if you want to claim ownership of signals (repos/kuksa-proto/kuksa/val/v2/val.proto:173-223).

## 8. Run the databroker as an Ankaios workload
Pattern used by Chapter 3 winner ArBytesMoral (repos/hc3-ArBytesMoral/compute/ankaios.yaml):
```yaml
apiVersion: v0.1
workloads:
  databroker:
    runtime: podman
    agent: agent_A
    runtimeConfig: |
      image: ghcr.io/eclipse-kuksa/kuksa-databroker:0.7.1
      commandArgs: ["--insecure"]
      commandOptions: ["--net=host"]
  my-provider:
    runtime: podman
    agent: agent_A
    dependencies:
      databroker: ADD_COND_RUNNING
    runtimeConfig: |
      image: localhost/my-provider:latest
      commandOptions: ["--net=host"]
```
`ank apply databroker.yaml`. The official Ankaios tutorial (repos/ankaios/doc/docs/usage/tutorial-vehicle-signals.md) still uses the **2023 image `ghcr.io/eclipse/kuksa.val/databroker:0.4.1`**, which still pulls (verified with `docker manifest inspect`) but predates v2. Swap in the eclipse-kuksa image. Check the `apiVersion` against your Ankaios version (see [[ankaios-overview]]). Not run by us.

## 9. Generate other artifacts from the same tree
`vspec export csv|yaml|protobuf|ddsidl|jsonschema|go|ros2interface|vhal|s2dm ...` with the same `-u/-q/-s/-l` flags as the JSON command in the quickstart. Examples: protobuf messages for a uProtocol payload, DDS IDL, ROS 2 msgs, or the Android VHAL mapping. The standalone `graphql` exporter no longer exists (removed in vss-tools 6.0).

## 10. Extend the unit catalogue (not run)
VSS validates every `unit:` against `spec/units.yaml` (and `quantities.yaml`). A signal in `Wh`, `rpm/s` or `kJ/K` fails the export until the unit exists. Keep your own `units.yaml` in VSS's own format **beside** COVESA's and pass both; do not edit the vendored release. `--units` is repeatable in vss-tools 6 (`cli_options.py`), so:

```
vspec export json -u vss61/spec/units.yaml -u my-units.yaml -q vss61/spec/quantities.yaml \
  -s vss61/spec/VehicleSignalSpecification.vspec -l my-overlay.vspec -o vss.json
```

Rules that keep two parties honest: declare each unit once, spell it exactly (`Celsius`, not `celsius`, since 6.0), and never add conversion factors to the catalogue, because a factor invites a consumer to believe ids normalise across units. Treat a unit as part of a signal's identity: a consumer reading km/h from a producer sending m/s is the fault a vocabulary exists to prevent. Continuous ranges (`min`/`max`) are tuning and may change without breaking readers; enum values (`allowed`) are a type and a rebound value changes what a byte means, so change them as you would change a type. `vspec export id` does the reverse: it hashes `min`/`max` (a range change re-mints the id) but not the 6.1 `enum` mapping (a rebinding keeps it), so do not rely on it as a layout id (corrected 2026-10-03, see [[derive-ids-from-layout-not-from-prose]], [[enum-discriminants-are-the-type]]). Related: `vspec export id` emits static ids, but the databroker still assigns its own numeric ids per loaded tree ([[vss-kuksa-reference]]); the path is the identity, the broker id is a session fact.
