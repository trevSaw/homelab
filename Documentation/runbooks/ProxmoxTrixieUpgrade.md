# Proxmox VE 8 → 9 Upgrade Guide (Bookworm → Trixie)

This guide documents upgrading Proxmox VE from Debian Bookworm to Trixie using the **official Debian and Proxmox repositories**. It is intended for personal / self-hosted Proxmox hosts (not mocha Ubuntu Server, which uses apt from Ubuntu directly).

---

## Pre-Upgrade Checklist

- [ ] Backup VMs and important data
- [ ] Document current kernel version: `uname -r`
- [ ] Check BIOS/firmware compatibility with the new kernel
- [ ] Ensure console access (IPMI/BMC or physical) is available

---

## Step 1: Ensure the Proxmox archive keyring is present

```bash
# On a normal Proxmox install this package is already present
sudo apt-get install -y proxmox-archive-keyring
```

Official docs: https://pve.proxmox.com/wiki/Package_Repositories

---

## Step 2: Update `/etc/apt/sources.list`

```bash
sudo tee /etc/apt/sources.list > /dev/null << 'EOF'
# Debian Trixie (official)
deb http://deb.debian.org/debian trixie main contrib non-free non-free-firmware
deb http://deb.debian.org/debian trixie-updates main contrib non-free non-free-firmware
deb http://security.debian.org/debian-security trixie-security main contrib non-free non-free-firmware
EOF
```

---

## Step 3: Configure Proxmox VE and Ceph (no-subscription) repos

```bash
sudo tee /etc/apt/sources.list.d/pve-install-repo.list > /dev/null << 'EOF'
# Proxmox VE 9 (Trixie) — no-subscription
deb [arch=amd64] http://download.proxmox.com/debian/pve trixie pve-no-subscription
EOF

sudo tee /etc/apt/sources.list.d/ceph.list > /dev/null << 'EOF'
# Proxmox Ceph Squid (Trixie) — no-subscription
deb http://download.proxmox.com/debian/ceph-squid trixie no-subscription
EOF
```

Also update any deb822-style `debian.sources` files under `/etc/apt/sources.list.d/` so suites say `trixie` / `trixie-updates` / `trixie-security` instead of `bookworm`.

---

## Step 4: Optional monitoring agents

If you run a personal monitoring agent (Zabbix, Beszel, etc.), update those package sources only if upstream publishes Trixie packages. Otherwise keep the previous Debian codename until upstream supports Trixie.

---

## Step 5: Remove duplicate / stale Proxmox source files

```bash
# Remove if a leftover duplicate exists (check first)
sudo rm -f /etc/apt/sources.list.d/pve-no-subscription.list
```

---

## Step 6: Verify no old codenames remain (except intentional holdouts)

```bash
grep -rE "(bullseye|bookworm|buster)" /etc/apt/sources.list /etc/apt/sources.list.d/ 2>/dev/null
```

**Expected:** Only optional third-party agents that lack Trixie packages should still reference older codenames.

---

## Step 7: Verify all sources

```bash
grep -rhE "^deb |^Types:|^Suites:" /etc/apt/sources.list /etc/apt/sources.list.d/ 2>/dev/null
```

---

## Step 8: Test connectivity to official mirrors

```bash
nc -zv -w5 deb.debian.org 80
nc -zv -w5 download.proxmox.com 80
```

**If timeout:** Check local firewall, DNS, and outbound HTTP/HTTPS from the Proxmox host.

---

## Step 9: Run upgrade

Follow the official Proxmox major-upgrade procedure as well:

https://pve.proxmox.com/wiki/Upgrade_from_8_to_9

```bash
sudo apt update
sudo apt full-upgrade
```

---

## Step 10: Reboot

```bash
sudo reboot
```

> **IMPORTANT:** Have console access ready in case of boot issues (kernel/BIOS conflicts).

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

If mirror connectivity fails from the Proxmox host:

### 1. Check local firewall

```bash
sudo iptables -L -n | grep -iE "reject|drop"
sudo pve-firewall status
```

### 2. Check routing / DNS

```bash
ip route get 1.1.1.1
getent hosts deb.debian.org download.proxmox.com
```

### 3. Homelab firewall (if applicable)

Allow the Proxmox host outbound TCP 80/443 to the public Debian and Proxmox mirrors. Do not point package updates at employer or corporate apt mirrors.

---

## Repos That Often Need No Codename Change

| Repo | Reason |
|------|--------|
| Elastic 7.x/8.x | Uses `stable`, not Debian codenames |
| Docker | Uses `stable`, not Debian codenames |
| Grafana | Uses `stable`, not Debian codenames |

---

## Quick One-Liner Summary

```bash
# 1. Ensure keyring
sudo apt-get install -y proxmox-archive-keyring

# 2. Update sources (run the tee commands from Steps 2–3)

# 3. Clean duplicates
sudo rm -f /etc/apt/sources.list.d/pve-no-subscription.list

# 4. Upgrade
sudo apt update && sudo apt full-upgrade

# 5. Reboot
sudo reboot
```

---

## Known Issues

### Kernel/BIOS conflict
After upgrading, the new kernel may conflict with certain BIOS settings. If the system does not boot:
1. Access via console (IPMI/BMC or physical)
2. Boot with an older kernel from the GRUB menu
3. Adjust BIOS settings as needed

### Third-party Trixie support
Some monitoring or agent vendors lag Debian releases. Keep older-codename repos only for those packages until upstream publishes Trixie builds.

---

## References

- Proxmox package repositories: https://pve.proxmox.com/wiki/Package_Repositories
- Upgrade from 8 to 9: https://pve.proxmox.com/wiki/Upgrade_from_8_to_9
- Debian mirrors: https://www.debian.org/mirror/list

---

*Last updated: July 2026*
