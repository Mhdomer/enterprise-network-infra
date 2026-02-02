# IP Addressing Plan

## Site Networks

| Site       | Network        | OSPF Area        | Subnet Mask     |
|------------|----------------|------------------|-----------------|
| HQ         | 10.0.0.0/24    | Area 0 (Backbone)| 255.255.255.0   |
| Branch A   | 10.1.0.0/24    | Area 1           | 255.255.255.0   |
| Branch B   | 10.2.0.0/24    | Area 2           | 255.255.255.0   |
| HQ–BrA WAN | 192.168.1.0/30 | Area 0           | 255.255.255.252 |
| HQ–BrB WAN | 192.168.2.0/30 | Area 0           | 255.255.255.252 |
| Mgmt OOB   | 172.16.0.0/24  | —                | 255.255.255.0   |

---

## Interface-Level IP Table

### HQ Router (router-id 1.1.1.1)

| Interface     | Description          | IP Address       | Connected To        |
|---------------|----------------------|------------------|---------------------|
| Gi0/0         | WAN to Branch A      | 192.168.1.1/30   | Branch A Gi0/0      |
| Gi0/1         | WAN to Branch B      | 192.168.2.1/30   | Branch B Gi0/0      |
| Gi0/2         | LAN uplink to HQ-SW  | 10.0.0.1/24      | HQ L3 Switch        |
| Gi0/3         | Simulated Internet   | DHCP / 203.0.113.1/30 | ISP (NAT outside) |
| Loopback0     | Router ID / Mgmt     | 1.1.1.1/32       | —                   |
| Mgmt (OOB)    | Out-of-band          | 172.16.0.1/24    | Mgmt VLAN 10        |

### Branch A Router (router-id 2.2.2.2)

| Interface     | Description          | IP Address       | Connected To        |
|---------------|----------------------|------------------|---------------------|
| Gi0/0         | WAN to HQ            | 192.168.1.2/30   | HQ Router Gi0/0     |
| Gi0/1         | LAN uplink to BrA-SW | 10.1.0.1/24      | Branch A L2 Switch  |
| Loopback0     | Router ID            | 2.2.2.2/32       | —                   |
| Mgmt (OOB)    | Out-of-band          | 172.16.0.2/24    | Mgmt VLAN 10        |

### Branch B Router (router-id 3.3.3.3)

| Interface     | Description          | IP Address       | Connected To        |
|---------------|----------------------|------------------|---------------------|
| Gi0/0         | WAN to HQ            | 192.168.2.2/30   | HQ Router Gi0/1     |
| Gi0/1         | LAN uplink to BrB-SW | 10.2.0.1/24      | Branch B L2 Switch  |
| Loopback0     | Router ID            | 3.3.3.3/32       | —                   |
| Mgmt (OOB)    | Out-of-band          | 172.16.0.3/24    | Mgmt VLAN 10        |

### HQ L3 Switch (SVIs)

| Interface / SVI | Description       | IP Address        | VLAN  |
|-----------------|-------------------|-------------------|-------|
| VLAN 10 SVI     | Management        | 10.0.10.1/26      | 10    |
| VLAN 20 SVI     | Users             | 10.0.20.1/25      | 20    |
| VLAN 30 SVI     | Voice             | 10.0.30.1/26      | 30    |
| VLAN 40 SVI     | Servers           | 10.0.40.1/26      | 40    |
| Mgmt (OOB)      | Out-of-band       | 172.16.0.10/24    | —     |

### Branch A L2 Switch (SVIs)

| Interface / SVI | Description       | IP Address        | VLAN  |
|-----------------|-------------------|-------------------|-------|
| VLAN 10 SVI     | Management        | 10.1.10.1/26      | 10    |
| VLAN 20 SVI     | Users             | 10.1.20.1/25      | 20    |
| VLAN 30 SVI     | Voice             | 10.1.30.1/26      | 30    |
| Mgmt (OOB)      | Out-of-band       | 172.16.0.11/24    | —     |

### Branch B L2 Switch (SVIs)

| Interface / SVI | Description       | IP Address        | VLAN  |
|-----------------|-------------------|-------------------|-------|
| VLAN 10 SVI     | Management        | 10.2.10.1/26      | 10    |
| VLAN 20 SVI     | Users             | 10.2.20.1/25      | 20    |
| VLAN 30 SVI     | Voice             | 10.2.30.1/26      | 30    |
| Mgmt (OOB)      | Out-of-band       | 172.16.0.12/24    | —     |

---

## VLAN Subnet Summary (per site)

| VLAN | Name       | HQ Subnet       | Branch A Subnet | Branch B Subnet |
|------|------------|-----------------|-----------------|-----------------|
| 10   | Management | 10.0.10.0/26    | 10.1.10.0/26    | 10.2.10.0/26    |
| 20   | Users      | 10.0.20.0/25    | 10.1.20.0/25    | 10.2.20.0/25    |
| 30   | Voice      | 10.0.30.0/26    | 10.1.30.0/26    | 10.2.30.0/26    |
| 40   | Servers    | 10.0.40.0/26    | HQ only         | HQ only         |
| 99   | Native     | —               | —               | —               |