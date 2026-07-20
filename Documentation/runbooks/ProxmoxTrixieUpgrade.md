# Proxmox VE 8 → 9 Upgrade Guide (Bookworm → Trixie)

This guide documents the steps to upgrade Proxmox VE from Debian Bookworm to Trixie using the Mujin Aptly mirror.

---

## Pre-Upgrade Checklist

- [ ] Backup VMs and important data
- [ ] Document current kernel version: `uname -r`
- [ ] Check BIOS/firmware compatibility with new kernel
- [ ] Ensure console access (IPMI/BMC) is available

---

## Step 1: Download Mujin GPG Key

```bash
curl -fsSL http://mjpn-tyo-apt01.mujin.co.jp/mujin-apt-archive.gpg | sudo tee /usr/share/keyrings/mujin-apt-archive.gpg > /dev/null
```

---

## Step 2: Update `/etc/apt/sources.list`

```bash
sudo tee /etc/apt/sources.list > /dev/null << 'EOF'
# Debian Trixie from Mujin Aptly Mirror
deb [signed-by=/usr/share/keyrings/mujin-apt-archive.gpg] http://mjpn-tyo-apt01.mujin.co.jp/debian trixie main
deb [signed-by=/usr/share/keyrings/mujin-apt-archive.gpg] http://mjpn-tyo-apt01.mujin.co.jp/debian trixie-updates main

# Proxmox VE 9 (Trixie)
deb [signed-by=/usr/share/keyrings/mujin-apt-archive.gpg] http://mjpn-tyo-apt01.mujin.co.jp/proxmox/pve trixie pve-no-subscription

# Proxmox Ceph Squid (Trixie)
deb [signed-by=/usr/share/keyrings/mujin-apt-archive.gpg] http://mjpn-tyo-apt01.mujin.co.jp/proxmox/ceph-squid trixie no-subscription
EOF
```

---

## Step 3: Update `/etc/apt/sources.list.d/debian.sources`

```bash
sudo tee /etc/apt/sources.list.d/debian.sources > /dev/null << 'EOF'
Types: deb deb-src 
URIs: mirror+file:///etc/apt/mirrors/debian.list 
Suites: trixie trixie-updates trixie-backports 
Components: main contrib non-free non-free-firmware 
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg 

Types: deb deb-src
URIs: mirror+file:///etc/apt/mirrors/debian-security.list 
Suites: trixie-security 
Components: main contrib non-free non-free-firmware 
Signed-By: /usr/share/keyrings/debian-archive-keyring.gpg 
EOF
```

---

## Step 4: Update Zabbix Repos (Keep on Bookworm - No Trixie Support Yet)

```bash
# Zabbix main repo
sudo tee /etc/apt/sources.list.d/zabbix.list > /dev/null << 'EOF'
# Zabbix main repository
deb https://repo.zabbix.com/zabbix/6.0/debian bookworm main
deb-src https://repo.zabbix.com/zabbix/6.0/debian bookworm main
EOF

# Zabbix agent2-plugins
sudo tee /etc/apt/sources.list.d/zabbix-agent2-plugins.list > /dev/null << 'EOF'
deb [arch=amd64] https://repo.zabbix.com/zabbix-agent2-plugins/1/debian bullseye main
deb-src [arch=amd64] https://repo.zabbix.com/zabbix-agent2-plugins/1/debian bullseye main
EOF
```

---

## Step 5: Remove Duplicate Source Files

```bash
# Remove if exists (check first)
sudo rm -f /etc/apt/sources.list.d/pve-no-subscription.list
```

---

## Step 6: Verify No Old Codenames Remain

```bash
grep -rE "(bullseye|bookworm|buster)" /etc/apt/sources.list /etc/apt/sources.list.d/ 2>/dev/null
```

**Expected:** Only Zabbix should show `bookworm`/`bullseye` (no Trixie support yet)

---

## Step 7: Verify All Sources

```bash
grep -rhE "^deb |^Types:|^Suites:" /etc/apt/sources.list /etc/apt/sources.list.d/ 2>/dev/null
```

---

## Step 8: Test Connectivity to Aptly Server

```bash
nc -zv -w5 10.2.25.160 80
```

**If timeout:** Check firewall rules (see [Firewall Troubleshooting](#firewall-troubleshooting) below)

---

## Step 9: Run Upgrade

```bash
sudo apt update
sudo apt full-upgrade
```

---

## Step 10: Reboot

```bash
sudo reboot
```

> ⚠️ **IMPORTANT:** Have console access ready in case of boot issues (kernel/BIOS conflicts)

---

## Post-Upgrade Verification

```bash
# Check Proxmox version
pveversion -v

# Check kernel
uname -r

# Check services
systemctl --failed

# Check VMs are running
qm list
```

---

## Firewall Troubleshooting

If `nc -zv -w5 10.2.25.160 80` times out from the Proxmox host:

### 1. Check local firewall

```bash
sudo iptables -L -n | grep -iE "reject|drop"
sudo pve-firewall status
```

### 2. Check routing

```bash
ip route get 10.2.25.160
```

### 3. Identify source IP/VLAN

```bash
ip route get 10.2.25.160 | grep src
```

### 4. Add firewall rule in pfSense

Edit `terragrunt/firewall/pfsense/oob/rules.yaml`:

- Ensure apt repo rule comes **BEFORE** the RFC1918 block rule (rule 0180)
- Rule should allow source VLAN → `MJPN_TYO_APT01` (10.2.25.160) on `HTTP_HTTPS` ports

Example rule (place before 0180):

```yaml
- {name: 0175_Allow HTTP and HTTPS to apt repo, action: pass, proto: tcp, source: lagg0.1043, destination: MJPN_TYO_APT01, destination_port: HTTP_HTTPS, log: true}
```

Then apply:

```bash
cd ~/my_projects/terragrunt/firewall/pfsense/oob
terragrunt apply
```

---

## Repos That Don't Need Changes

| Repo | Reason |
|------|--------|
| Elastic 7.x/8.x | Uses `stable`, not Debian codenames |
| Docker | Uses `stable`, not Debian codenames |
| Grafana | Uses `stable`, not Debian codenames |

---

## Quick One-Liner Summary

```bash
# 1. Get key
curl -fsSL http://mjpn-tyo-apt01.mujin.co.jp/mujin-apt-archive.gpg | sudo tee /usr/share/keyrings/mujin-apt-archive.gpg > /dev/null

# 2. Update sources (run the tee commands from Steps 2-4)

# 3. Clean duplicates
sudo rm -f /etc/apt/sources.list.d/pve-no-subscription.list

# 4. Upgrade
sudo apt update && sudo apt full-upgrade

# 5. Reboot
sudo reboot
```

---

## Known Issues

### Kernel/BIOS Conflict
After upgrading, the new kernel may conflict with certain BIOS settings. If the system doesn't boot:
1. Access via console (IPMI/BMC)
2. Boot with older kernel from GRUB menu
3. Adjust BIOS settings as needed

### Zabbix Trixie Support
As of January 2026, Zabbix does not have official Trixie repositories. Keep using `bookworm` repos until Zabbix releases Trixie packages.

---

## References

- Mujin Aptly Server: http://mjpn-tyo-apt01.mujin.co.jp/
- Setup Guide: http://mjpn-tyo-apt01.mujin.co.jp/setup.html
- Status Page: http://mjpn-tyo-apt01.mujin.co.jp/status.html

---

*Last updated: January 2026*
