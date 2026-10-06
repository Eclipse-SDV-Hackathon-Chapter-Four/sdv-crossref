---
title: VSS + KUKSA quickstart (databroker get/set in 5 minutes, custom overlay in 15)
type: quickstart
component: vss-kuksa
tags: [kuksa, databroker, quickstart, docker, vss-tools, overlay]
status: verified
sources:
  - repos/kuksa-databroker/README.md
  - repos/kuksa-databroker/doc/user_guide.md
  - repos/kuksa-python-sdk/kuksa-client/README.md
  - repos/vehicle_signal_specification/Makefile
  - https://github.com/eclipse-kuksa/kuksa-databroker/releases
last-verified: 2026-10-03
related:
  - "[[vss-kuksa-overview]]"
  - "[[vss-kuksa-howto]]"
  - "[[vss-kuksa-reference]]"
---

# VSS + KUKSA quickstart

**Prerequisites:** Docker (or Podman: replace `docker` with `podman`) and internet access to ghcr.io. For part B you also need Python ≥3.11 and git. No Rust toolchain is needed.
Versions used: `ghcr.io/eclipse-kuksa/kuksa-databroker:0.7.1` (== `latest` on 2026-10-03), `kuksa-databroker-cli:0.7.1`, `kuksa-client` 0.6.0, vss-tools 6.1.0, VSS v6.1.
Pin `:0.7.1` rather than `:latest` or `:main` so every team runs the same thing.

## A. Databroker + get/set (≈5 min)

```sh
docker network create kuksa
# terminal 1 (or add -d): databroker, no TLS, no auth, VSS 6.0 default tree
docker run -it --rm --name Server --network kuksa -p 55555:55555 \
  ghcr.io/eclipse-kuksa/kuksa-databroker:0.7.1 --insecure
```
Expected log lines (observed on 2026-10-03, timestamps trimmed):
```
INFO databroker: Starting Kuksa Databroker 0.7.1
INFO databroker: Populating metadata from file 'vss_release_6.0.json'
WARN databroker: Authorization is not enabled.
INFO databroker::grpc::server: Listening on 0.0.0.0:55555
INFO databroker::grpc::server: TLS is not enabled
```

In terminal 2, run the CLI one-shot. **`-it` is required**: without a TTY the CLI fails with `Error: terminfo entry not found` / `Not a tty (os error 25)` (observed).
```sh
CLI="docker run --rm -it --network kuksa ghcr.io/eclipse-kuksa/kuksa-databroker-cli:0.7.1 --server Server:55555"
$CLI get Vehicle.Speed
$CLI publish Vehicle.Speed 100.34
$CLI get Vehicle.Speed
```
Observed on 2026-10-03:
```
Using kuksa.val.v1
[get]  OK
Vehicle.Speed: NotAvailable
Using kuksa.val.v1
[publish]  OK
Using kuksa.val.v1
[get]  OK
Vehicle.Speed: 100.34 km/h
```
Run `$CLI` without a command to get the interactive prompt, which has TAB completion and `get`/`publish`/`actuate`/`subscribe`/`metadata`/`token` commands.

### Same thing from Python (talks v2 for publish, v1 for get)
```sh
python3 -m venv .venv && . .venv/bin/activate && pip install kuksa-client==0.6.0
python3 - <<'PY'
from kuksa_client.grpc import VSSClient, Datapoint
with VSSClient('127.0.0.1', 55555) as c:
    print(c.get_server_info())
    c.set_current_values({'Vehicle.Powertrain.TractionBattery.Temperature.Average': Datapoint(42.0)})
    print(c.get_current_values(['Vehicle.Powertrain.TractionBattery.Temperature.Average'])
          ['Vehicle.Powertrain.TractionBattery.Temperature.Average'].value)
PY
```
Observed (against a broker on 55556, same image): `ServerInfo(name='databroker', version='0.7.1')` then `42.0`.

### Python interactive CLI in a container
```sh
docker run -it --rm --net=host ghcr.io/eclipse-kuksa/kuksa-python-sdk/kuksa-client:0.6.0 grpc://127.0.0.1:55555
# at the prompt: getValue Vehicle.Speed / setValue Vehicle.Speed 88 / quit
```
Observed: banner `kuksa-client CLI 0.6.0`, then `getValue` returns JSON `{"path": "Vehicle.Speed", "value": {"value": 88.0, "timestamp": "..."}}`.

## B. Load a custom VSS overlay (child presence + battery thermal) (≈10 min)

```sh
python3 -m venv .venv && . .venv/bin/activate && pip install vss-tools==6.1
git clone --depth 1 --branch v6.1 https://github.com/COVESA/vehicle_signal_specification vss61
mkdir -p vss && cat > vss/hackathon_overlay.vspec <<'EOF2'
Vehicle.Cabin.ChildPresence:
  type: branch
  description: Child presence detection (CPD) results, hackathon extension.
Vehicle.Cabin.ChildPresence.IsDetected:
  type: sensor
  datatype: boolean
  description: True if any CPD sensor reports a child or pet in the cabin.
Vehicle.Cabin.ChildPresence.Confidence:
  type: sensor
  datatype: uint8
  unit: percent
  min: 0
  max: 100
  description: Confidence of the child presence detection.
Vehicle.Cabin.ChildPresence.AlertLevel:
  type: actuator
  datatype: string
  allowed: ['NONE', 'HMI', 'HORN_LIGHTS', 'REMOTE', 'EMERGENCY_CALL']
  description: Escalation level requested by the CPD application.
Vehicle.Powertrain.TractionBattery.Temperature.IsThermalRunawayWarning:
  type: sensor
  datatype: boolean
  description: Thermal event / thermal runaway warning raised by the BMS.
EOF2
vspec export json -u vss61/spec/units.yaml -q vss61/spec/quantities.yaml \
  -s vss61/spec/VehicleSignalSpecification.vspec -l vss/hackathon_overlay.vspec -o vss/vss_hackathon.json
# expected tail: "VSpecs loaded, amount=94" ... "Generating JSON output..."; file is about 370 KB

docker run -d --rm --name Custom --network kuksa -v $PWD/vss:/vss:ro \
  ghcr.io/eclipse-kuksa/kuksa-databroker:0.7.1 --insecure --vss /vss/vss_hackathon.json
docker logs Custom | grep Populating   # -> Populating metadata from file '/vss/vss_hackathon.json'

CLI="docker run --rm -it --network kuksa ghcr.io/eclipse-kuksa/kuksa-databroker-cli:0.7.1 --server Custom:55555"
$CLI publish Vehicle.Cabin.ChildPresence.IsDetected true
$CLI get Vehicle.Cabin.ChildPresence.IsDetected
$CLI publish Vehicle.Cabin.Seat.Row2.PassengerSide.OccupancyStatus OCCUPIED
$CLI publish Vehicle.Cabin.ChildPresence.Confidence 150
```
Observed on 2026-10-03:
```
[publish]  OK
[get]  OK
Vehicle.Cabin.ChildPresence.IsDetected: true
[publish]  OK
[publish]  OK  Error [Error { code: 400, reason: "value out of min/max bounds", message: "given value exceeds type's boundaries" }]
```
Note that the CLI prints `[publish] OK` **even when the value was rejected**. Read the rest of the line.
`--vss` accepts a comma-separated list of JSON files. Mounting a single file also works.

## C. Clean up
```sh
docker rm -f Server Custom; docker network rm kuksa
```

## Observed on 2026-10-03
Run on Linux (x86_64, Docker, no podman) by the research agent. All of A and B above were executed. The outputs shown are copied from the run, with ANSI escapes stripped. Additional checks that were run are written up in [[vss-kuksa-howto]] (JWT auth, v2 actuation provider, v1 target vs v2 actuation, enum handling).
