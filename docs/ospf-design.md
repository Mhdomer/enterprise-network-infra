# OSPF Design

## Overview

Multi-area OSPF (OSPFv2) is used to provide scalable, loop-free routing between all three sites.
HQ acts as the backbone (Area 0) hub; branches are non-backbone areas connected through the HQ ABR.

---

## Area Map

```
          [ Area 1 — Branch A ]
          10.1.0.0/24
               |
               | (WAN 192.168.1.0/30)
               |
[ Area 0 — Backbone — HQ ]
10.0.0.0/24 + 192.168.1.0/30 + 192.168.2.0/30
               |
               | (WAN 192.168.2.0/30)
               |
          [ Area 2 — Branch B ]
          10.2.0.0/24
```

---

## Router Roles

| Device          | Router ID  | OSPF Role          | Areas       |
|-----------------|------------|--------------------|-------------|
| HQ Router       | 1.1.1.1    | ABR (backbone hub) | Area 0      |
| Branch A Router | 2.2.2.2    | Internal router    | Area 1      |
| Branch B Router | 3.3.3.3    | Internal router    | Area 2      |
| HQ L3 Switch    | 4.4.4.4    | Internal router    | Area 0      |

---

## ABR Summarization Plan

| ABR (HQ Router) | Summarizes     | Into    | Summary Route      |
|-----------------|----------------|---------|--------------------|
| HQ Router       | Area 1 routes  | Area 0  | 10.1.0.0/16        |
| HQ Router       | Area 2 routes  | Area 0  | 10.2.0.0/16        |

IOS config on HQ Router:
```
router ospf 1
  area 1 range 10.1.0.0 255.255.0.0
  area 2 range 10.2.0.0 255.255.0.0
```

---

## OSPF Interface Configuration

### All WAN interfaces (Area 0)

```
interface GigabitEthernet0/0
  ip ospf 1 area 0
  ip ospf authentication message-digest
  ip ospf message-digest-key 1 md5 SECURE_KEY_2026
  ip ospf network point-to-point
```

### HQ LAN interfaces (Area 0)

```
interface GigabitEthernet0/2
  ip ospf 1 area 0
```

### Branch A LAN interfaces (Area 1)

```
interface GigabitEthernet0/1
  ip ospf 1 area 1
```

### Branch B LAN interfaces (Area 2)

```
interface GigabitEthernet0/1
  ip ospf 1 area 2
```

---

## MD5 Authentication

MD5 authentication is configured on all OSPF-speaking interfaces to prevent rogue router injection.

- Key ID: `1`
- Key string: `SECURE_KEY_2026` (stored in Ansible vault — never in plaintext)
- Verification: `show ip ospf interface` — confirm `Message digest authentication`

---

## Expected LSA Types Per Area

| LSA Type | Name              | Present In                |
|----------|-------------------|---------------------------|
| Type 1   | Router LSA        | All areas (local only)    |
| Type 2   | Network LSA       | Multi-access segments     |
| Type 3   | Summary LSA       | Area 0 (from ABR)         |
| Type 4   | ASBR Summary LSA  | Area 0 (if ASBR present)  |
| Type 5   | External LSA      | Area 0 (default route)    |

---

## Verification Commands

```
show ip ospf neighbor          # confirm FULL state
show ip ospf database          # check LSA counts before/after summarization
show ip route ospf             # confirm O IA routes visible
show ip ospf interface         # confirm auth type, area, cost
debug ip ospf adj              # use only when troubleshooting adjacency issues
```

---

## Design Decisions

**Why multi-area instead of single-area?**
- Limits LSA flooding scope — branch routers only hold their own area's LSAs plus Type 3 summaries
- Manual summarization at ABRs reduces routing table size on branch routers
- Scales cleanly when adding more branch offices (add a new area, no impact to other areas)

**Why HQ as ABR?**
- HQ is the natural hub — all WAN links terminate here
- Centralizes summarization logic in one place
- Branch routers are simpler (single-area internal routers)