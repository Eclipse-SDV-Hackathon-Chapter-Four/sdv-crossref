#!/usr/bin/env bash
# Install or check the dependencies for the vault tooling, the verified
# quickstarts and the pre-flight pulls (playbook/env-setup-matrix.md).
# Usage: ./install_deps.sh [--check] [--vault] [--tools] [--system [--yes]] [--pull] [--clone] [--all]
# --clone recreates repos/ from repos/manifest.tsv (about 4.7 GB measured 2026-10-06); --all includes it (everything without sudo).
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
VENV="$ROOT/.venv"
MANIFEST="$ROOT/repos/manifest.tsv"
PY_PKGS=(duckdb pyyaml pytest 'vss-tools==6.1.*' 'kuksa-client==0.6.0' eclipse-zenoh 'iceoryx2==0.10.0')
PY_IMPORTS="duckdb, yaml, pytest, vss_tools, kuksa_client, zenoh, iceoryx2"
APT_PKGS=(build-essential cmake ninja-build pkg-config libssl-dev protobuf-compiler libclang-dev can-utils git-lfs podman)
# Pre-flight pull list, tags copied from playbook/env-setup-matrix.md section 3.
IMAGES=(
  ghcr.io/eclipse-kuksa/kuksa-databroker:0.7.1
  ghcr.io/eclipse-kuksa/kuksa-databroker-cli:0.7.1
  ghcr.io/eclipse-kuksa/kuksa-python-sdk/kuksa-client:0.6.0
  ghcr.io/eclipse-opensovd/opensovd-gateway:latest
  ghcr.io/eclipse-autowrx/sdv-runtime:latest
  quay.io/eclipse-kuksa/kuksa-databroker:0.6.0
  quay.io/eclipse-kuksa/csv-provider:0.4.5
  eclipse/zenoh:1.1.0
  docker.io/library/influxdb:2.7
  docker.io/grafana/grafana:9.5.14
)

usage() { sed -n '2,5p' "$0" | sed 's/^# \{0,1\}//'; }

DO_CHECK=0 DO_VAULT=0 DO_TOOLS=0 DO_SYSTEM=0 DO_PULL=0 DO_CLONE=0 YES=0
[[ $# -eq 0 ]] && DO_CHECK=1
for arg in "$@"; do
  case "$arg" in
    --check) DO_CHECK=1 ;;
    --vault) DO_VAULT=1 ;;
    --tools) DO_TOOLS=1 ;;
    --system) DO_SYSTEM=1 ;;
    --pull) DO_PULL=1 ;;
    --clone) DO_CLONE=1 ;;
    --all) DO_VAULT=1 DO_TOOLS=1 DO_PULL=1 DO_CLONE=1 ;;
    --yes) YES=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $arg" >&2; usage >&2; exit 2 ;;
  esac
done

have() { command -v "$1" >/dev/null 2>&1; }
first_line() { "$@" 2>&1 | head -n1 || true; }
docker_ok() { have docker && docker info >/dev/null 2>&1; }

# ---------- check ----------
MISSING=0
FIXES=()
row() { printf '%-14s %-9s %s\n' "$1" "$2" "$3"; }
req() {  # req NAME FOUND(0/1) VERSION FIX
  if [[ $2 -eq 1 ]]; then row "$1" ok "$3"
  else row "$1" MISSING "required"; MISSING=$((MISSING + 1)); FIXES+=("$1: $4"); fi
}
opt() {  # opt NAME FOUND(0/1) VERSION NOTE
  if [[ $2 -eq 1 ]]; then row "$1" ok "$3"; else row "$1" absent "optional: $4"; fi
}
ver_of() { have "$1" && first_line "$@" || echo ""; }

do_check() {
  row TOOL STATUS VERSION
  row ---- ------ -------
  req git "$(have git && echo 1 || echo 0)" "$(ver_of git --version)" "run ./install_deps.sh --system"
  local py_ok=0
  if have python3 && python3 -c 'import sys; sys.exit(sys.version_info < (3, 10))'; then py_ok=1; fi
  req python3 "$py_ok" "$(ver_of python3 --version) (need >= 3.10)" "sudo apt-get install -y python3 python3-venv"
  req docker "$(have docker && echo 1 || echo 0)" "$(ver_of docker --version)" "run ./install_deps.sh --system"
  if have docker; then
    req docker-daemon "$(docker_ok && echo 1 || echo 0)" "reachable" \
      "start the daemon (sudo systemctl start docker) and join the docker group (sudo usermod -aG docker \$USER)"
  fi
  req cargo "$(have cargo && echo 1 || echo 0)" "$(ver_of cargo --version)" "run ./install_deps.sh --tools"
  req rustc "$(have rustc && echo 1 || echo 0)" "$(ver_of rustc --version)" "run ./install_deps.sh --tools"
  req cmake "$(have cmake && echo 1 || echo 0)" "$(ver_of cmake --version)" "run ./install_deps.sh --system"
  req gcc "$(have gcc && echo 1 || echo 0)" "$(ver_of gcc --version)" "run ./install_deps.sh --system"
  req g++ "$(have g++ && echo 1 || echo 0)" "$(ver_of g++ --version)" "run ./install_deps.sh --system"
  local venv_ok=0 duck=""
  if [[ -x $VENV/bin/python ]] && duck=$("$VENV/bin/python" -c 'import duckdb; print(duckdb.__version__)' 2>/dev/null); then venv_ok=1; fi
  req .venv-duckdb "$venv_ok" "duckdb $duck" "run ./install_deps.sh --vault"
  opt podman "$(have podman && echo 1 || echo 0)" "$(ver_of podman --version)" "Ankaios/AutoSD only; sudo apt-get install -y podman"
  local bz=0 bzv=""
  if have bazelisk; then bz=1; bzv="bazelisk $(first_line bazelisk version | sed 's/^Bazelisk version: //')"
  elif have bazel; then bz=1; bzv="$(first_line bazel --version)"; fi
  opt bazelisk "$bz" "$bzv" "S-CORE Bazel only; run ./install_deps.sh --tools"
  opt protoc "$(have protoc && echo 1 || echo 0)" "$(ver_of protoc --version)" "S-CORE Bazel only; run ./install_deps.sh --system"
  opt can-utils "$(have cansend && echo 1 || echo 0)" "cansend" "OpenBSW vcan only; sudo apt-get install -y can-utils"
  opt kvm "$([[ -e /dev/kvm ]] && echo 1 || echo 0)" "/dev/kvm" "S-CORE Path C / AutoSD VMs only (info)"
  local free_gb
  free_gb=$(df -Pk "$ROOT" | awk 'NR==2 {print int($4 / 1048576)}')
  local total=0 present=0 name _
  if [[ -f $MANIFEST ]]; then
    while IFS=$'\t' read -r name _; do
      [[ -z $name || $name == \#* || $name == name ]] && continue
      total=$((total + 1)); [[ -e $ROOT/repos/$name/.git ]] && present=$((present + 1))
    done < "$MANIFEST"
    opt repos "$([[ $present -eq $total ]] && echo 1 || echo 0)" "$present/$total present" \
      "$present/$total present; run ./install_deps.sh --clone"
  else
    opt repos 0 "" "no repos/manifest.tsv; run python3 scripts/build_repo_manifest.py"
  fi
  opt disk-free "$([[ $free_gb -ge 20 ]] && echo 1 || echo 0)" "${free_gb} GB" "${free_gb} GB free, 20 GB recommended (info)"
  echo
  echo "required missing: $MISSING"
  local f
  for f in "${FIXES[@]+"${FIXES[@]}"}"; do echo "  fix $f"; done
}

# ---------- vault ----------
do_vault() {
  have python3 || { echo "python3 not found; run ./install_deps.sh --system" >&2; exit 1; }
  if "$VENV/bin/python" -c "import $PY_IMPORTS" 2>/dev/null; then
    echo "vault: $VENV already satisfied"; return
  fi
  [[ -x $VENV/bin/python ]] || python3 -m venv "$VENV"
  "$VENV/bin/python" -m pip install --quiet --upgrade pip
  "$VENV/bin/python" -m pip install --quiet "${PY_PKGS[@]}"
  "$VENV/bin/python" -c "import $PY_IMPORTS; print('vault: imports ok:', '$PY_IMPORTS')"
}

# ---------- tools (user space, no sudo) ----------
do_tools() {
  if ! have rustup && [[ -x $HOME/.cargo/bin/rustup ]]; then export PATH="$HOME/.cargo/bin:$PATH"; fi
  if ! have rustup; then
    echo "tools: installing rustup + stable into ~/.cargo (no sudo)"
    curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y --default-toolchain stable
    export PATH="$HOME/.cargo/bin:$PATH"
  elif ! rustup toolchain list | grep -q '^stable'; then
    rustup toolchain install stable
  else
    echo "tools: rustup stable present ($(first_line rustc +stable --version))"
  fi
  if have bazelisk; then
    echo "tools: bazelisk present ($(command -v bazelisk))"
  else
    local arch
    case "$(uname -m)" in x86_64) arch=amd64 ;; aarch64|arm64) arch=arm64 ;; *) echo "tools: no bazelisk build for $(uname -m)" >&2; return 1 ;; esac
    mkdir -p "$HOME/.local/bin"
    echo "tools: downloading bazelisk to ~/.local/bin/bazelisk"
    curl -fsSL -o "$HOME/.local/bin/bazelisk" \
      "https://github.com/bazelbuild/bazelisk/releases/latest/download/bazelisk-linux-$arch"
    chmod +x "$HOME/.local/bin/bazelisk"
    [[ :$PATH: == *":$HOME/.local/bin:"* ]] || echo "tools: add ~/.local/bin to PATH"
  fi
}

# ---------- system (apt, sudo, confirmed) ----------
do_system() {
  local pkgs=("${APT_PKGS[@]}")
  have docker || pkgs+=(docker.io)
  if ! have apt-get || ! have dpkg; then
    echo "system: not a Debian/Ubuntu host; install these with your package manager:"
    echo "  ${pkgs[*]}"
    exit 2
  fi
  local todo=() p
  for p in "${pkgs[@]}"; do dpkg -s "$p" >/dev/null 2>&1 || todo+=("$p"); done
  if [[ ${#todo[@]} -eq 0 ]]; then echo "system: all apt packages installed"; return; fi
  echo "system: will run:"
  echo "  sudo apt-get update && sudo apt-get install -y ${todo[*]}"
  if [[ $YES -ne 1 ]]; then
    local ans
    read -r -p "Proceed with sudo? [y/N] " ans
    [[ $ans == [yY]* ]] || { echo "system: aborted"; return 1; }
  fi
  sudo apt-get update
  sudo apt-get install -y "${todo[@]}"
}

# ---------- pull ----------
do_pull() {
  if ! docker_ok; then echo "pull: docker unavailable or daemon unreachable; skipping"; return; fi
  local img
  for img in "${IMAGES[@]}"; do
    if docker image inspect "$img" >/dev/null 2>&1; then echo "pull: have $img"
    else echo "pull: $img"; docker pull --quiet "$img" || echo "pull: FAILED $img" >&2; fi
  done
  echo "pull: build-only images (opensovd ecu-sim, openbsw toolchain) and fleet-management :main images: see playbook/env-setup-matrix.md section 3"
}

# ---------- clone ----------
do_clone() {
  export GIT_TERMINAL_PROMPT=0   # a repo that went private fails instead of prompting and hanging
  [[ -f $MANIFEST ]] || { echo "clone: $MANIFEST not found" >&2; exit 1; }
  local cloned=0 skipped=0 mismatch=0 failed=0
  local name url commit branch _date notes dir head
  while IFS=$'\t' read -r name url commit branch _date notes; do
    [[ -z $name || $name == \#* || $name == name ]] && continue
    dir="$ROOT/repos/$name"
    if [[ -e $dir ]]; then echo "clone: have $name"; skipped=$((skipped + 1)); continue; fi
    echo "clone: $name"
    local args=(--depth 1)
    [[ $branch != detached ]] && args+=(--branch "$branch")
    if ! git clone --quiet "${args[@]}" "$url" "$dir"; then
      echo "clone: FAILED $name" >&2; failed=$((failed + 1)); continue
    fi
    head=$(git -C "$dir" rev-parse HEAD)
    if [[ $head != "$commit" ]]; then
      # keep the branch name at the pinned commit so build_repo_manifest.py records it instead of "detached"
      local co=(--detach "$commit")
      [[ $branch != detached ]] && co=(-B "$branch" "$commit")
      if git -C "$dir" fetch --quiet --depth 1 origin "$commit" && git -C "$dir" checkout --quiet "${co[@]}"; then
        head=$commit
      else
        echo "clone: $name: at ${head:0:7} instead of pinned ${commit:0:7} (upstream moved)"
        mismatch=$((mismatch + 1))
      fi
    fi
    if [[ $notes == *submodules* ]]; then
      git -C "$dir" submodule update --quiet --init --depth 1 --recursive \
        || echo "clone: $name: submodule update failed; continuing" >&2
    fi
    cloned=$((cloned + 1))
  done < "$MANIFEST"
  echo "clone: cloned $cloned, skipped $skipped, pin-mismatch $mismatch, failed $failed"
  [[ $failed -eq 0 ]] || exit 1
}

[[ $DO_SYSTEM -eq 1 ]] && do_system
[[ $DO_TOOLS -eq 1 ]] && do_tools
[[ $DO_VAULT -eq 1 ]] && do_vault
[[ $DO_PULL -eq 1 ]] && do_pull
[[ $DO_CLONE -eq 1 ]] && do_clone
if [[ $DO_CHECK -eq 1 ]]; then
  do_check
  [[ $MISSING -eq 0 ]] || exit 1
fi
exit 0
