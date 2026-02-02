# VLAN Plan

## VLAN Definitions

| VLAN ID | Name       | Subnet (per site)       | Notes                          |
|---------|------------|-------------------------|--------------------------------|
| 10      | Management | 10.x.10.0/26            | Network devices only (OOB)     |
| 20      | Users      | 10.x.20.0/25            | Employee workstations          |
| 30      | Voice      | 10.x.30.0/26            | VoIP phones                    |
| 40      | Servers    | 10.0.40.0/26            | HQ only — DNS, NTP, DHCP       |
| 99      | Native     | —                       | Untagged trunk VLAN            |

---

## VLAN Presence Per Site

| VLAN | HQ | Branch A | Branch B |
|------|----|----------|----------|
| 10   | ✓  | ✓        | ✓        |
| 20   | ✓  | ✓        | ✓        |
| 30   | ✓  | ✓        | ✓        |
| 40   | ✓  | ✗        | ✗        |
| 99   | ✓  | ✓        | ✓        |

---

## Trunk Port Allowed VLANs

| Link                            | Allowed VLANs        | Native VLAN |
|---------------------------------|----------------------|-------------|
| HQ L3 Switch ↔ HQ Access Switch | 10,20,30,40          | 99          |
| Branch A Router ↔ BrA Switch    | 10,20,30             | 99          |
| Branch B Router ↔ BrB Switch    | 10,20,30             | 99          |
| EtherChannel uplinks (HQ)       | 10,20,30,40          | 99          |
| EtherChannel uplinks (Branches) | 10,20,30             | 99          |

---

## Access Port Assignments

| Port Type         | VLAN | PortFast | BPDU Guard |
|-------------------|------|----------|------------|
| Workstation ports | 20   | ✓        | ✓          |
| VoIP phone ports  | 30   | ✓        | ✓          |
| Server ports      | 40   | ✓        | ✓          |
| Mgmt device ports | 10   | ✓        | ✓          |

---

## Notes

- VLAN 99 is the native VLAN on all trunks — no user traffic should be untagged
- VLAN 40 (Servers) exists only at HQ; branches access servers via OSPF routing
- Management VLAN 10 is used exclusively for OOB device management (SSH, SNMP)
- Voice VLAN 30 is blocked from reaching Server VLAN 40 (enforced by ACL — see acl-policy.md)