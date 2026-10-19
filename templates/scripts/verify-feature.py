#!/usr/bin/env python3
"""Verify one feature from feature_list.json and record the evidence.

  python3 scripts/verify-feature.py <feature-id>

Runs the feature's "verify" command; on success sets "passes": true and writes
"evidence": {"date", "command", "exit"}; on failure sets passes false with the
same evidence. The list is the scope boundary: an agent may mark a feature done
only through this script, never by editing the JSON by hand.
"""
import json
import subprocess
import sys
import time

LIST = "feature_list.json"


def main(feature_id):
    with open(LIST) as handle:
        data = json.load(handle)
    feature = next((f for f in data.get("features", []) if f.get("id") == feature_id), None)
    if feature is None:
        print("verify-feature: FAIL (no feature with id %r in %s)" % (feature_id, LIST))
        return 2
    command = feature.get("verify")
    if not command:
        print("verify-feature: FAIL (%s has no verify command)" % feature_id)
        return 2
    proc = subprocess.run(["bash", "-lc", command], capture_output=True, text=True)
    tail = "\n".join((proc.stdout + proc.stderr).splitlines()[-10:])
    feature["passes"] = proc.returncode == 0
    feature["evidence"] = {"date": time.strftime("%Y-%m-%d"), "command": command, "exit": proc.returncode}
    with open(LIST, "w") as handle:
        json.dump(data, handle, indent=2)
        handle.write("\n")
    if proc.returncode == 0:
        print("verify-feature: OK (%s passes; evidence recorded)" % feature_id)
        return 0
    print(tail)
    print("verify-feature: FAIL (%s exit %d; passes stays false)" % (feature_id, proc.returncode))
    return 1


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print(__doc__)
        sys.exit(2)
    sys.exit(main(sys.argv[1]))
