#!/usr/bin/env bash
# Check or apply host prerequisites for the verification recipes (tier 2):
# a vcan0 interface for OpenBSW CAN/DoIP, CDA-over-UDS and the CAN-to-KUKSA feeder,
# tap0 (192.168.0.10/24) plus VLAN tap0a0 (id 160, 192.168.2.10/24) for OpenBSW POSIX DoIP,
# and /etc/hosts names for the openDuT self-hosted stack. Agents must not run --apply or --remove.
# Usage: ./test_setup.sh [--check] [--apply [--yes]] [--remove [--yes]]
set -euo pipefail

ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
HOSTS_FILE=/etc/hosts
MARK_BEGIN='# hackaton test_setup.sh begin'
MARK_END='# hackaton test_setup.sh end'
HOST_NAMES=(
  opendut.local
  auth.opendut.local
  netbird-api.opendut.local
  netbird-relay.opendut.local
  signal.opendut.local
  nginx-webdav.opendut.local
  opentelemetry.opendut.local
  monitoring.opendut.local
)

usage() { sed -n '2,6p' "$0" | sed 's/^# \{0,1\}//'; }

DO_CHECK=0 DO_APPLY=0 DO_REMOVE=0 YES=0
[[ $# -eq 0 ]] && DO_CHECK=1
for arg in "$@"; do
  case "$arg" in
    --check) DO_CHECK=1 ;;
    --apply) DO_APPLY=1 ;;
    --remove) DO_REMOVE=1 ;;
    --yes) YES=1 ;;
    -h|--help) usage; exit 0 ;;
    *) echo "unknown option: $arg" >&2; usage >&2; exit 2 ;;
  esac
done

have() { command -v "$1" >/dev/null 2>&1; }
net_ok() { [[ $(uname -s) == Linux ]] && have ip; }
hosts_line() { printf '127.0.0.1 %s' "$1"; }
has_marker() { grep -qxF "$1" "$HOSTS_FILE" 2>/dev/null; }

# ---------- state ----------
TAP_ADDR=192.168.0.10/24 VLAN_ADDR=192.168.2.10/24
MOD_VCAN=0 MOD_CANGW=0 LINK=0 LINK_READY=0 LINK_DETAIL=""
TAP=0 TAP_UP=0 TAP_HAS_ADDR=0 TAP_READY=0 VLAN=0 VLAN_UP=0 VLAN_HAS_ADDR=0 VLAN_READY=0
HOSTS_MISSING=()
probe_if() {  # probe_if DEV ADDR -> sets P_EXISTS P_UP P_ADDR
  P_EXISTS=0 P_UP=0 P_ADDR=0
  local info
  info=$(ip -o link show "$1" 2>/dev/null) || return 0
  P_EXISTS=1
  [[ $info =~ [\<,]UP[,\>] ]] && P_UP=1
  [[ $(ip -o -4 addr show dev "$1" 2>/dev/null) == *" $2 "* ]] && P_ADDR=1
  return 0
}
probe() {
  MOD_VCAN=0 MOD_CANGW=0 LINK=0 LINK_READY=0 LINK_DETAIL="" HOSTS_MISSING=()
  TAP=0 TAP_UP=0 TAP_HAS_ADDR=0 TAP_READY=0 VLAN=0 VLAN_UP=0 VLAN_HAS_ADDR=0 VLAN_READY=0
  if net_ok; then
    [[ -d /sys/module/vcan ]] && MOD_VCAN=1
    [[ -d /sys/module/can_gw ]] && MOD_CANGW=1
    local info
    if info=$(ip -o link show vcan0 2>/dev/null); then
      LINK=1
      LINK_DETAIL="$(grep -o 'mtu [0-9]*' <<<"$info" || true)"
      if [[ $info =~ [\<,]UP[,\>] ]]; then LINK_DETAIL="UP, $LINK_DETAIL"; else LINK_DETAIL="DOWN, $LINK_DETAIL"; fi
      [[ $info =~ [\<,]UP[,\>] && $info == *" mtu 16 "* ]] && LINK_READY=1
    fi
    probe_if tap0 "$TAP_ADDR"; TAP=$P_EXISTS TAP_UP=$P_UP TAP_HAS_ADDR=$P_ADDR
    [[ $TAP_UP -eq 1 && $TAP_HAS_ADDR -eq 1 ]] && TAP_READY=1
    probe_if tap0a0 "$VLAN_ADDR"; VLAN=$P_EXISTS VLAN_UP=$P_UP VLAN_HAS_ADDR=$P_ADDR
    [[ $VLAN_UP -eq 1 && $VLAN_HAS_ADDR -eq 1 ]] && VLAN_READY=1
  fi
  local h
  for h in "${HOST_NAMES[@]}"; do
    grep -qxF "$(hosts_line "$h")" "$HOSTS_FILE" 2>/dev/null || HOSTS_MISSING+=("$h")
  done
}

# ---------- check ----------
MISSING=0
row() { printf '%-28s %-8s %s\n' "$1" "$2" "$3"; }
req() {  # req NAME FOUND(0/1) DETAIL
  if [[ $2 -eq 1 ]]; then row "$1" ok "$3"
  elif net_ok || [[ $1 == *.local ]]; then row "$1" MISSING "$3"; MISSING=$((MISSING + 1))
  else row "$1" absent "not Linux or iproute2 missing"; MISSING=$((MISSING + 1)); fi
}

if_detail() {  # if_detail EXISTS UP HAS_ADDR ADDR
  [[ $1 -eq 1 ]] || { echo "need UP, $4"; return; }
  local d=DOWN
  [[ $2 -eq 1 ]] && d=UP
  if [[ $3 -eq 1 ]]; then echo "$d, $4"; else echo "$d, no $4"; fi
}

do_check() {
  probe
  MISSING=0
  row ITEM STATUS DETAIL
  row ---- ------ ------
  req module-vcan "$MOD_VCAN" "kernel module vcan"
  req module-can_gw "$MOD_CANGW" "kernel module can_gw (openDuT)"
  req vcan0 "$LINK" "ip link show vcan0"
  req vcan0-up-mtu16 "$LINK_READY" "${LINK_DETAIL:-need UP, mtu 16}"
  req tap0 "$TAP" "ip link show tap0 (OpenBSW POSIX DoIP, ECU 192.168.0.201)"
  req tap0-up-192.168.0.10 "$TAP_READY" "$(if_detail "$TAP" "$TAP_UP" "$TAP_HAS_ADDR" "$TAP_ADDR")"
  req tap0a0-vlan160 "$VLAN" "ip link show tap0a0 (VLAN 160 on tap0)"
  req tap0a0-up-192.168.2.10 "$VLAN_READY" "$(if_detail "$VLAN" "$VLAN_UP" "$VLAN_HAS_ADDR" "$VLAN_ADDR")"
  local h
  for h in "${HOST_NAMES[@]}"; do
    if [[ " ${HOSTS_MISSING[*]+"${HOSTS_MISSING[*]}"} " == *" $h "* ]]; then req "$h" 0 "$(hosts_line "$h") in $HOSTS_FILE"
    else req "$h" 1 "$(hosts_line "$h") in $HOSTS_FILE"; fi
  done
  # informational rows, never counted
  if [[ -c /dev/net/tun ]]; then row tun-device ok /dev/net/tun
  else row tun-device absent "/dev/net/tun missing: tap0 cannot be created (container/WSL?)"; fi
  if [[ -e /dev/kvm ]]; then row kvm ok /dev/kvm; else row kvm absent "/dev/kvm (S-CORE Path C / AutoSD VMs only)"; fi
  local fs
  fs=$(findmnt -n -o FSTYPE /tmp 2>/dev/null || true)
  if [[ $fs == tmpfs ]]; then row tmp-fs WARN "RAM-backed: keep images and build dirs out of /tmp"
  else row tmp-fs ok "${fs:-unknown}"; fi
  local ram
  ram=$(free -g 2>/dev/null | awk '/^Mem:/ {print $7}' || true)
  if [[ -z $ram ]]; then row ram-available absent "free not available"
  elif [[ $ram -lt 8 ]]; then row ram-available WARN "${ram} GB available, 8 GB recommended"
  else row ram-available ok "${ram} GB available"; fi
  local ovmf=""
  ovmf=$(compgen -G '/usr/share/OVMF/OVMF_CODE*.fd' | head -n1 || true)
  [[ -z $ovmf && -f $ROOT/.local-autosd/ovmf/OVMF_CODE.fd ]] && ovmf="$ROOT/.local-autosd/ovmf/OVMF_CODE.fd"
  if [[ -n $ovmf ]]; then row ovmf ok "$ovmf"; else row ovmf absent "AutoSD QEMU boot needs --ovmf-dir"; fi
  echo
  echo "missing: $MISSING"
  if [[ $MISSING -gt 0 ]]; then echo "  fix: run ./test_setup.sh --apply"; return 1; fi
}

confirm() {  # confirm LABEL
  [[ $YES -eq 1 ]] && return 0
  local ans
  read -r -p "Proceed with sudo? [y/N] " ans
  [[ $ans == [yY]* ]] || { echo "$1: aborted"; exit 1; }
}

need_net() { net_ok || { echo "$1: needs Linux with iproute2 (ip); nothing done" >&2; exit 1; }; }

# ---------- apply (sudo, confirmed) ----------
do_apply() {
  need_net apply
  probe
  local plan=() h
  [[ $MOD_VCAN -eq 1 ]] || plan+=("sudo modprobe vcan")
  [[ $MOD_CANGW -eq 1 ]] || plan+=("sudo modprobe can_gw max_hops=2")
  if [[ $LINK -eq 0 ]]; then
    plan+=("sudo ip link add dev vcan0 type vcan" "sudo ip link set vcan0 mtu 16" "sudo ip link set up vcan0")
  elif [[ $LINK_READY -eq 0 ]]; then
    plan+=("sudo ip link set down vcan0" "sudo ip link set vcan0 mtu 16" "sudo ip link set up vcan0")
  fi
  [[ $TAP -eq 1 ]] || plan+=("sudo ip tuntap add dev tap0 mode tap")
  [[ $TAP_UP -eq 1 ]] || plan+=("sudo ip link set tap0 up")
  [[ $TAP_HAS_ADDR -eq 1 ]] || plan+=("sudo ip address add $TAP_ADDR dev tap0")
  [[ $VLAN -eq 1 ]] || plan+=("sudo ip link add tap0a0 link tap0 type vlan id 160")
  [[ $VLAN_UP -eq 1 ]] || plan+=("sudo ip link set tap0a0 up")
  [[ $VLAN_HAS_ADDR -eq 1 ]] || plan+=("sudo ip address add $VLAN_ADDR dev tap0a0")
  local lines=()
  for h in "${HOSTS_MISSING[@]+"${HOSTS_MISSING[@]}"}"; do lines+=("$(hosts_line "$h")"); done
  local markers=0
  has_marker "$MARK_BEGIN" && has_marker "$MARK_END" && markers=1
  if [[ ${#lines[@]} -gt 0 ]]; then
    if [[ $markers -eq 1 ]]; then
      local l
      for l in "${lines[@]}"; do plan+=("sudo sed -i '/^$MARK_END\$/i $l' $HOSTS_FILE"); done
    else
      local quoted="'$MARK_BEGIN'" l
      for l in "${lines[@]}"; do quoted+=" '$l'"; done
      plan+=("printf '%s\\n' $quoted '$MARK_END' | sudo tee -a $HOSTS_FILE >/dev/null")
    fi
  fi
  if [[ ${#plan[@]} -eq 0 ]]; then
    echo "apply: nothing to do; all prerequisites already present"
  else
    echo "apply: will run:"
    local p
    for p in "${plan[@]}"; do echo "  $p"; done
    confirm apply
    [[ $MOD_VCAN -eq 1 ]] || sudo modprobe vcan
    [[ $MOD_CANGW -eq 1 ]] || sudo modprobe can_gw max_hops=2
    if [[ $LINK -eq 0 ]]; then
      sudo ip link add dev vcan0 type vcan
    elif [[ $LINK_READY -eq 0 ]]; then
      sudo ip link set down vcan0
    fi
    if [[ $LINK_READY -eq 0 ]]; then
      sudo ip link set vcan0 mtu 16
      sudo ip link set up vcan0
    fi
    [[ $TAP -eq 1 ]] || sudo ip tuntap add dev tap0 mode tap
    [[ $TAP_UP -eq 1 ]] || sudo ip link set tap0 up
    [[ $TAP_HAS_ADDR -eq 1 ]] || sudo ip address add "$TAP_ADDR" dev tap0
    [[ $VLAN -eq 1 ]] || sudo ip link add tap0a0 link tap0 type vlan id 160
    [[ $VLAN_UP -eq 1 ]] || sudo ip link set tap0a0 up
    [[ $VLAN_HAS_ADDR -eq 1 ]] || sudo ip address add "$VLAN_ADDR" dev tap0a0
    if [[ ${#lines[@]} -gt 0 ]]; then
      if [[ $markers -eq 1 ]]; then
        local l
        for l in "${lines[@]}"; do sudo sed -i "/^$MARK_END\$/i $l" "$HOSTS_FILE"; done
      else
        printf '%s\n' "$MARK_BEGIN" "${lines[@]}" "$MARK_END" | sudo tee -a "$HOSTS_FILE" >/dev/null
      fi
    fi
  fi
  echo "apply: note: vcan0, tap0/tap0a0 and the loaded modules do not survive a reboot (re-run --apply); the $HOSTS_FILE lines do"
  echo "apply: note: remove tap0 (./test_setup.sh --remove) before testing a real S32K148 on this host"
  echo
}

# ---------- remove (sudo, confirmed) ----------
do_remove() {
  need_net remove
  probe
  local plan=() markers=0
  [[ $LINK -eq 1 ]] && plan+=("sudo ip link del vcan0")
  [[ $VLAN -eq 1 ]] && plan+=("sudo ip link del tap0a0")
  [[ $TAP -eq 1 ]] && plan+=("sudo ip tuntap del dev tap0 mode tap")
  has_marker "$MARK_BEGIN" && markers=1
  [[ $markers -eq 1 ]] && plan+=("sudo sed -i '/^$MARK_BEGIN\$/,/^$MARK_END\$/d' $HOSTS_FILE")
  if [[ ${#plan[@]} -eq 0 ]]; then
    echo "remove: nothing to do; no vcan0, no tap0/tap0a0 and no marker block in $HOSTS_FILE"
  else
    echo "remove: will run (kernel modules stay loaded):"
    local p
    for p in "${plan[@]}"; do echo "  $p"; done
    confirm remove
    [[ $LINK -eq 1 ]] && sudo ip link del vcan0
    [[ $VLAN -eq 1 ]] && sudo ip link del tap0a0
    [[ $TAP -eq 1 ]] && sudo ip tuntap del dev tap0 mode tap
    [[ $markers -eq 1 ]] && sudo sed -i "/^$MARK_BEGIN\$/,/^$MARK_END\$/d" "$HOSTS_FILE"
  fi
  echo
}

if [[ $DO_REMOVE -eq 1 ]]; then
  do_remove
  do_check || true
  exit 0
fi
if [[ $DO_APPLY -eq 1 ]]; then
  do_apply
  do_check && exit 0 || exit 1
fi
if [[ $DO_CHECK -eq 1 ]]; then
  do_check && exit 0 || exit 1
fi
exit 0
