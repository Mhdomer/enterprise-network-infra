# IPSec VPN Design

## Overview

Site-to-site IPSec VPNs using IKEv2 protect traffic between HQ and each branch.
All inter-site traffic traverses encrypted tunnels — no cleartext data crosses WAN links.

---

## VPN Tunnels

| Tunnel       | HQ Endpoint    | Branch Endpoint | Protected Traffic          |
|--------------|----------------|-----------------|----------------------------|
| HQ ↔ BranchA | 192.168.1.1    | 192.168.1.2     | 10.0.0.0/8 ↔ 10.1.0.0/24  |
| HQ ↔ BranchB | 192.168.2.1    | 192.168.2.2     | 10.0.0.0/8 ↔ 10.2.0.0/24  |

---

## IKEv2 Configuration

### Phase 1 — IKE SA (Peer Authentication & Key Exchange)

```
crypto ikev2 proposal IKEV2_PROP
  encryption aes-cbc-256
  integrity sha256
  group 14

crypto ikev2 policy IKEV2_POL
  proposal IKEV2_PROP

crypto ikev2 keyring KEYRING
  peer BRANCH_A
    address 192.168.1.2
    pre-shared-key LOCAL_PSK_2026
  peer BRANCH_B
    address 192.168.2.2
    pre-shared-key LOCAL_PSK_2026

crypto ikev2 profile IKEV2_PROFILE
  match identity remote address 192.168.1.2 255.255.255.255
  authentication remote pre-share
  authentication local pre-share
  keyring local KEYRING
```

### Phase 2 — IPSec SA (Data Encryption)

```
crypto ipsec transform-set TS esp-aes 256 esp-sha256-hmac
  mode tunnel

crypto ipsec profile IPSEC_PROFILE
  set transform-set TS
  set ikev2-profile IKEV2_PROFILE
```

---

## Crypto ACLs (Traffic Selectors)

### HQ Router — for Branch A tunnel

```
ip access-list extended VPN_TO_BRANCH_A
  permit ip 10.0.0.0 0.0.255.255 10.1.0.0 0.0.255.255
```

### Branch A Router — mirror of HQ ACL

```
ip access-list extended VPN_TO_HQ
  permit ip 10.1.0.0 0.0.255.255 10.0.0.0 0.0.255.255
```

> Both sides of the crypto ACL must be exact mirrors — asymmetry causes Phase 2 failures.

---

## Crypto Map (applied to WAN interface)

```
crypto map CMAP 10 ipsec-isakmp
  set peer 192.168.1.2
  set transform-set TS
  set ikev2-profile IKEV2_PROFILE
  match address VPN_TO_BRANCH_A

interface GigabitEthernet0/0
  crypto map CMAP
```

---

## Verification Commands

```
show crypto ikev2 sa           # Phase 1 — confirm READY state
show crypto ipsec sa           # Phase 2 — confirm pkts encaps/decaps incrementing
show crypto session            # summary of all active sessions
debug crypto ikev2             # use only when Phase 1 is stuck
```

---

## VPN + OSPF Interaction

- OSPF runs over the physical WAN interfaces (not GRE tunnels)
- IPSec encrypts the OSPF hello/LSA packets in transport mode on point-to-point /30 links
- MTU must match on both sides to avoid OSPF adjacency issues (use `ip ospf mtu-ignore` if needed)
- Confirm no routing asymmetry: traffic out one path must return the same path

---

## Security Parameters Summary

| Parameter       | Value              | Reason                                    |
|-----------------|--------------------|-------------------------------------------|
| Encryption      | AES-256-CBC        | NIST-approved, strong symmetric cipher    |
| Integrity       | SHA-256 (HMAC)     | Collision-resistant hash                  |
| DH Group        | Group 14 (2048-bit)| Minimum recommended for IKEv2             |
| Auth method     | Pre-shared key     | Sufficient for lab; use certs in prod     |
| PSK storage     | Ansible vault      | Never committed in plaintext              |

---

## Design Decisions

**Why IKEv2 over IKEv1?**
- IKEv2 is simpler (fewer message exchanges), more resilient, and supports EAP/MOBIKE
- IKEv1 is legacy — IKEv2 is the current standard (RFC 7296)

**Why PSK over certificates?**
- Certificates require a PKI (CA server) — outside scope of this lab phase
- PSK is acceptable for a controlled lab environment with a small number of peers
- Production deployment would use certificates with a CA