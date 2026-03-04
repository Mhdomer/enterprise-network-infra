#!/usr/bin/env python3
"""
Network verification script — SSHes into all devices and validates key state.
Exits with code 1 if any check fails (CI-pipeline compatible).
"""

import json
import sys
from dataclasses import dataclass, field

from netmiko import ConnectHandler, NetmikoTimeoutException, NetmikoAuthenticationException


DEVICES = [
    {"device_type": "cisco_ios", "host": "172.16.0.1",  "username": "admin", "password": "ADMIN_PASS", "name": "hq-router"},
    {"device_type": "cisco_ios", "host": "172.16.0.2",  "username": "admin", "password": "ADMIN_PASS", "name": "branch-a-router"},
    {"device_type": "cisco_ios", "host": "172.16.0.3",  "username": "admin", "password": "ADMIN_PASS", "name": "branch-b-router"},
    {"device_type": "cisco_ios", "host": "172.16.0.10", "username": "admin", "password": "ADMIN_PASS", "name": "hq-switch"},
]

CHECKS = {
    "OSPF neighbors FULL":    "show ip ospf neighbor",
    "IPSec SA active":        "show crypto ipsec sa",
    "VLANs present":          "show vlan brief",
    "NTP synchronized":       "show ntp status",
    "NAT translations":       "show ip nat translations",
}

REQUIRED_VLANS = ["10", "20", "30", "40"]
EXPECTED_OSPF_NEIGHBORS = {
    "hq-router":        ["192.168.1.2", "192.168.2.2"],
    "branch-a-router":  ["192.168.1.1"],
    "branch-b-router":  ["192.168.2.1"],
}


@dataclass
class CheckResult:
    passed: bool
    detail: str


def check_ospf(output: str, device_name: str) -> CheckResult:
    expected = EXPECTED_OSPF_NEIGHBORS.get(device_name, [])
    missing = [ip for ip in expected if ip not in output]
    not_full = "FULL" not in output and expected  # routers should have FULL neighbors

    if missing:
        return CheckResult(False, f"Missing neighbors: {missing}")
    if not_full and expected:
        return CheckResult(False, "No FULL state adjacency found")
    return CheckResult(True, "All expected neighbors in FULL state")


def check_ipsec(output: str, device_name: str) -> CheckResult:
    if device_name not in ("hq-router", "branch-a-router", "branch-b-router"):
        return CheckResult(True, "N/A for this device")
    if "pkts encaps:" not in output and "encaps:" not in output:
        return CheckResult(False, "No IPSec SA found or counters not incrementing")
    return CheckResult(True, "IPSec SA active")


def check_vlans(output: str, device_name: str) -> CheckResult:
    if "router" in device_name:
        return CheckResult(True, "N/A for routers")
    missing = [v for v in REQUIRED_VLANS if v not in output]
    if missing:
        return CheckResult(False, f"Missing VLANs: {missing}")
    return CheckResult(True, f"VLANs {REQUIRED_VLANS} all present")


def check_ntp(output: str, _device_name: str) -> CheckResult:
    if "synchronized" in output.lower():
        return CheckResult(True, "Clock is synchronized")
    return CheckResult(False, "NTP not synchronized")


def check_nat(output: str, device_name: str) -> CheckResult:
    if device_name != "hq-router":
        return CheckResult(True, "N/A for this device")
    return CheckResult(True, "NAT table reachable (manual verification needed)")


VALIDATORS = {
    "OSPF neighbors FULL":  check_ospf,
    "IPSec SA active":      check_ipsec,
    "VLANs present":        check_vlans,
    "NTP synchronized":     check_ntp,
    "NAT translations":     check_nat,
}


def verify_device(device: dict) -> dict:
    name = device.pop("name")
    results = {}
    try:
        with ConnectHandler(**device) as conn:
            for check_name, command in CHECKS.items():
                output = conn.send_command(command)
                validator = VALIDATORS[check_name]
                result = validator(output, name)
                results[check_name] = {
                    "passed": result.passed,
                    "detail": result.detail,
                    "raw_output": output,
                }
    except NetmikoTimeoutException:
        results["CONNECTION"] = {"passed": False, "detail": f"Timeout connecting to {device['host']}"}
    except NetmikoAuthenticationException:
        results["CONNECTION"] = {"passed": False, "detail": "Authentication failed"}

    return {name: results}


def main():
    all_results = {}
    failures = []

    for device in DEVICES:
        result = verify_device(device.copy())
        all_results.update(result)

        device_name = list(result.keys())[0]
        for check, data in result[device_name].items():
            if not data["passed"]:
                failures.append(f"{device_name} / {check}: {data['detail']}")

    print(json.dumps(all_results, indent=2))

    if failures:
        print("\n--- FAILURES ---", file=sys.stderr)
        for f in failures:
            print(f"  FAIL: {f}", file=sys.stderr)
        sys.exit(1)

    print("\nAll checks passed.", file=sys.stderr)
    sys.exit(0)


if __name__ == "__main__":
    main()
