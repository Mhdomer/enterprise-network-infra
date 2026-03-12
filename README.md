# Enterprise Network Infrastructure

A production-grade multi-site network built, automated, and documented across 8 phases using Cisco IOS, Packet Tracer, GNS3, Ansible, and Python.

---

## Technologies

![Cisco IOS](https://img.shields.io/badge/Cisco_IOS-1BA0D7?style=flat&logo=cisco&logoColor=white)
![Ansible](https://img.shields.io/badge/Ansible-EE0000?style=flat&logo=ansible&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![GNS3](https://img.shields.io/badge/GNS3-FF6600?style=flat)

---

## Features

| Feature | Details |
|---------|---------|
| OSPF Multi-Area | Areas 0/1/2 · ABR at HQ · MD5 authentication · manual summarization |
| VLANs | 4 VLANs (Mgmt / Users / Voice / Servers) across 3 sites |
| STP | Rapid-PVST · root bridge at HQ · PortFast + BPDU Guard on access ports |
| EtherChannel | LACP mode active on all switch uplinks |
| ACLs | Named extended ACLs enforcing inter-VLAN security policy |
| NAT / PAT | Overload NAT on HQ router · simulated internet access from branches |
| IPSec IKEv2 | Site-to-site VPN HQ↔BranchA and HQ↔BranchB · AES-256 / SHA-256 |
| Ansible | 5 playbooks: DHCP · NTP · NAT · OSPF auth · config backup |
| Python | Netmiko-based state verification + NAPALM structured audit |

---

## Topology

```
        Internet (203.0.113.0/30)
                   |
           [ HQ Router 1.1.1.1 ]  ← Area 0 Backbone
         /                       \
192.168.1.0/30             192.168.2.0/30
       /                             \
[ Branch A Router 2.2.2.2 ]   [ Branch B Router 3.3.3.3 ]
     Area 1                              Area 2
  10.1.0.0/24                         10.2.0.0/24
```

Detailed topology diagram: [`docs/topology.png`](docs/topology.png) *(added after Packet Tracer build)*

---

## IP Plan

| Site | Network | OSPF Area |
|------|---------|-----------|
| HQ | 10.0.0.0/24 | Area 0 |
| Branch A | 10.1.0.0/24 | Area 1 |
| Branch B | 10.2.0.0/24 | Area 2 |
| HQ–BrA WAN | 192.168.1.0/30 | Area 0 |
| HQ–BrB WAN | 192.168.2.0/30 | Area 0 |
| Management OOB | 172.16.0.0/24 | — |

Full interface-level addressing → [docs/ip-plan.md](docs/ip-plan.md)

---

## Phase Summary

| Phase | Scope | Tool | Status |
|-------|-------|------|--------|
| 1 | Design & Documentation | Docs | ✅ |
| 2 | VLANs, STP, EtherChannel | Packet Tracer | ✅ |
| 3 | OSPF Multi-Area + MD5 Auth | Packet Tracer | ✅ |
| 4 | ACLs + NAT/PAT | Packet Tracer | ✅ |
| 5 | IPSec IKEv2 VPN | Packet Tracer | ✅ |
| 6 | GNS3 migration + Ansible | GNS3 + Ansible | ✅ |
| 7 | Python network validation | Python | ✅ |
| 8 | Documentation & GitHub polish | GitHub | ✅ |

---

## Running Ansible Playbooks

**Prerequisites**
```bash
pip install ansible
ansible-galaxy collection install cisco.ios
```

**Create vault file with secrets**
```bash
cp ansible/vault.yml.example ansible/vault.yml
ansible-vault encrypt ansible/vault.yml
# populate: vault_device_password, vault_enable_password, vault_ospf_md5_key
```

**Run individual playbooks**
```bash
cd ansible
ansible-playbook -i inventory/hosts.yml playbooks/01_dhcp.yml --ask-vault-pass
ansible-playbook -i inventory/hosts.yml playbooks/02_ntp.yml --ask-vault-pass
ansible-playbook -i inventory/hosts.yml playbooks/03_nat.yml --ask-vault-pass
ansible-playbook -i inventory/hosts.yml playbooks/04_ospf_auth.yml --ask-vault-pass
ansible-playbook -i inventory/hosts.yml playbooks/05_backup_configs.yml --ask-vault-pass
```

**Run with dynamic GNS3 inventory** *(requires GNS3 running with project open)*
```bash
# Edit PROJECT_ID in ansible/inventory/dynamic_inventory.py first
ansible-playbook -i inventory/dynamic_inventory.py playbooks/01_dhcp.yml --ask-vault-pass
```

---

## Running Python Scripts

**Prerequisites**
```bash
pip install netmiko napalm
```

**Verify network state** *(exits 1 if any check fails — CI compatible)*
```bash
python scripts/verify_network.py
```

Checks performed on every device:
- OSPF neighbor adjacency in FULL state
- IPSec SA counters incrementing (routers only)
- VLANs 10/20/30/40 active (switches only)
- NTP clock synchronized
- NAT translation table reachable (HQ only)

**Run structured NAPALM audit**
```bash
python scripts/audit_configs.py
# Saves JSON to configs/<hostname>/audit-<timestamp>.json
```

---

## Repository Structure

```
enterprise-network-infra/
├── docs/
│   ├── ip-plan.md          # Full interface-level addressing
│   ├── vlan-plan.md        # VLAN IDs, subnets, trunk allowed lists
│   ├── ospf-design.md      # Area map, ABR roles, summarization
│   ├── ipsec-design.md     # IKEv2 parameters, crypto ACLs
│   └── acl-policy.md       # Inter-VLAN security policy
├── packet-tracer/          # .pkt simulation files
├── gns3/                   # .gns3 project files
├── ansible/
│   ├── inventory/          # hosts.yml + dynamic GNS3 inventory
│   ├── group_vars/         # Variable files per device group
│   ├── playbooks/          # 5 automation playbooks
│   └── roles/              # base / ospf / security roles
├── scripts/
│   ├── verify_network.py   # Netmiko state verification
│   └── audit_configs.py    # NAPALM structured data pull
└── configs/                # Backed-up running configs + audit JSON
```

---

## Troubleshooting Notes

**OSPF neighbors stuck in EXSTART/EXCHANGE**
Root cause: MTU mismatch between peers.
Fix: `ip ospf mtu-ignore` on the affected interface while investigating the actual MTU.

**EtherChannel stays in `(I)` — individual state**
Root cause: LACP mode is passive/passive on both ends — no peer initiates negotiation.
Fix: at least one side must use `channel-group 1 mode active`.

**IPSec Phase 2 — encrypt/decrypt counters stuck at 0**
Root cause: crypto ACL asymmetry — source and destination must be exact mirrors on each peer.
Fix: run `show crypto map` and `show ip access-lists` on both sides to compare.

**Ansible fails with SSH timeout on GNS3 devices**
Root cause: router boot time — device SSH stack not ready.
Fix: add `ansible_command_timeout: 60` to `ansible/group_vars/all.yml`.

---

## Lessons Learned

- Completing the full design phase before opening Packet Tracer saved hours of rework — the IP plan caught several subnet overlap issues before any config was touched
- OSPF MD5 keys are case-sensitive on Cisco IOS — a mismatch is silent until you run `debug ip ospf adj`
- Ansible `ios_config` is idempotent; `ios_command` is not — mixing them without understanding this causes false "changed" task results
- NAPALM `get_facts()` returns serial number, OS version, and uptime in one call — useful as a quick health check after automation runs
- Dynamic inventory makes the Ansible workflow feel real: no manual host file updates when the GNS3 topology changes
