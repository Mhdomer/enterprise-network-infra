# ACL Security Policy

## Inter-VLAN Traffic Policy

| Source VLAN | Destination VLAN | Action  | Allowed Ports           |
|-------------|------------------|---------|-------------------------|
| 10 (Mgmt)   | Any              | PERMIT  | All                     |
| 20 (Users)  | 40 (Servers)     | PERMIT  | TCP 80, 443, 53 (DNS)   |
| 20 (Users)  | 30 (Voice)       | DENY    | All                     |
| 30 (Voice)  | 40 (Servers)     | DENY    | All                     |
| 30 (Voice)  | 20 (Users)       | DENY    | All                     |
| Any         | Any              | PERMIT  | (implicit — intra-VLAN) |

---

## Named Extended ACLs

### MGMT_ACCESS — Applied inbound on VLAN 10 SVI
```
ip access-list extended MGMT_ACCESS
  permit ip 10.x.10.0 0.0.0.63 any
```

### USERS_TO_SERVERS — Applied inbound on VLAN 20 SVI
```
ip access-list extended USERS_TO_SERVERS
  permit tcp 10.x.20.0 0.0.0.127 10.0.40.0 0.0.0.63 eq 80
  permit tcp 10.x.20.0 0.0.0.127 10.0.40.0 0.0.0.63 eq 443
  permit udp 10.x.20.0 0.0.0.127 10.0.40.0 0.0.0.63 eq 53
  deny   ip  10.x.20.0 0.0.0.127 10.x.30.0 0.0.0.63
  permit ip any any
```

### BLOCK_VOICE_TO_SERVERS — Applied inbound on VLAN 30 SVI
```
ip access-list extended BLOCK_VOICE_TO_SERVERS
  deny ip 10.x.30.0 0.0.0.63 10.0.40.0 0.0.0.63
  deny ip 10.x.30.0 0.0.0.63 10.x.20.0 0.0.0.127
  permit ip any any
```

---

## ACL Application Points

| ACL Name                | Applied On  | Direction |
|-------------------------|-------------|-----------|
| MGMT_ACCESS             | VLAN 10 SVI | inbound   |
| USERS_TO_SERVERS        | VLAN 20 SVI | inbound   |
| BLOCK_VOICE_TO_SERVERS  | VLAN 30 SVI | inbound   |

---

## Verification

```
show ip access-lists                # confirm ACL entries exist
show ip access-lists BLOCK_VOICE_TO_SERVERS  # check hit counts
```

Test procedure:
1. From Voice VLAN host, ping Server VLAN — expect: unreachable (DENY hit count increments)
2. From Users VLAN host, HTTP to Server VLAN — expect: success
3. From Users VLAN host, ping Voice VLAN — expect: unreachable
4. From Mgmt VLAN host, ping any — expect: success