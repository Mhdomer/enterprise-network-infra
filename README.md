# Enterprise Network Infrastructure

A production-grade multi-site network built, automated, and documented across 8 phases using Cisco IOS, Packet Tracer, GNS3, Ansible, and Python.

---

## Technologies

![Cisco IOS](https://img.shields.io/badge/Cisco_IOS-1BA0D7?style=flat&logo=cisco&logoColor=white)
![Ansible](https://img.shields.io/badge/Ansible-EE0000?style=flat&logo=ansible&logoColor=white)
![Python](https://img.shields.io/badge/Python-3776AB?style=flat&logo=python&logoColor=white)
![GNS3](https://img.shields.io/badge/GNS3-FF6600?style=flat)

---

## IP Plan (Quick Reference)

| Site | Network | OSPF Area |
|------|---------|-----------|
| HQ | 10.0.0.0/24 | Area 0 |
| Branch A | 10.1.0.0/24 | Area 1 |
| Branch B | 10.2.0.0/24 | Area 2 |
| HQ–BrA WAN | 192.168.1.0/30 | Area 0 |
| HQ–BrB WAN | 192.168.2.0/30 | Area 0 |

Full interface-level addressing: [docs/ip-plan.md](docs/ip-plan.md)

---

## Build Phases

| Phase | Scope | Tool | Status |
|-------|-------|------|--------|
| 1 | Design & Documentation | Docs | ✅ |
| 2 | VLANs, STP, EtherChannel | Packet Tracer | 🔄 |
| 3 | OSPF Multi-Area + MD5 Auth | Packet Tracer | ⬜ |
| 4 | ACLs + NAT/PAT | Packet Tracer | ⬜ |
| 5 | IPSec IKEv2 VPN | Packet Tracer | ⬜ |
| 6 | GNS3 migration + Ansible | GNS3 + Ansible | ⬜ |
| 7 | Python network validation | Python | ⬜ |
| 8 | Documentation & GitHub polish | GitHub | ⬜ |

---

## Repository Structure

```
enterprise-network-infra/
├── docs/               # Design documents
├── packet-tracer/      # .pkt simulation files
├── gns3/               # .gns3 project files
├── ansible/            # Automation playbooks and inventory
├── scripts/            # Python verification and audit scripts
└── configs/            # Backed-up device configs
```
