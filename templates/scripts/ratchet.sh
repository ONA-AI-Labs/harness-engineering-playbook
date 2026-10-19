#!/usr/bin/env bash
# Ratchet: a gate for pre-existing debt. "No more than today" instead of "zero", so the gate survives.
#   scripts/ratchet.sh --name "lint errors" --max 12 [--match REGEX] [--ok-exit 0,1] -- <command...>
# Counts the command's output lines matching REGEX (default: error), fails above --max, tells you to
# lower --max when the count drops, and hard-fails when the command exits with a code not in --ok-exit:
# a checker that crashed must never read as clean. Commit the --max value where CI can see it.
set -uo pipefail

name="findings"; max=""; match="error"; ok_exit="0,1"
while [ $# -gt 0 ]; do
  case "$1" in
    --name) name="$2"; shift 2 ;;
    --max) max="$2"; shift 2 ;;
    --match) match="$2"; shift 2 ;;
    --ok-exit) ok_exit="$2"; shift 2 ;;
    --) shift; break ;;
    *) echo "ratchet: unknown option $1"; exit 2 ;;
  esac
done
[ -n "$max" ] && [ $# -gt 0 ] || { echo "usage: ratchet.sh --name NAME --max N [--match REGEX] [--ok-exit 0,1] -- <command>"; exit 2; }

output=$("$@" 2>&1); code=$?
case ",$ok_exit," in *",$code,"*) ;; *)
  printf '%s\n' "$output" | tail -20
  echo "ratchet: $name FAIL (the checker exited $code, which is not in --ok-exit $ok_exit; a crashed checker is not a clean one)"
  exit 2 ;;
esac
count=$(printf '%s\n' "$output" | grep -cE -- "$match" || true)
if [ "$count" -gt "$max" ]; then
  printf '%s\n' "$output" | grep -E -- "$match" | tail -20
  echo "ratchet: $name FAIL ($count over the baseline of $max; fix the new ones, the list above ends with the last findings in file order)"
  exit 1
fi
if [ "$count" -lt "$max" ]; then
  echo "ratchet: $name OK ($count of $max; lower --max to $count to lock the gain in)"
else
  echo "ratchet: $name OK ($count of $max)"
fi
