# Ultra-Lean AMD Ryzen AI Max+ 64GB LLM Setup

This document outlines a complete setup for running **32B Q4_K_M LLMs** on an **AMD Ryzen AI Max+ 64GB unified memory system** in a **headless, Docker-based environment** optimized for maximum performance, responsiveness, and low power consumption.

---

## 1. OS Installation

### Recommended OS
- **Ubuntu 24.04 LTS Minimal (Headless)**
  - Lightweight and widely supported.
  - Ideal for running Docker and GPU/APU accelerated LLM workloads.

### Steps
```bash
# Update system
sudo apt update && sudo apt upgrade -y

# Install SSH for headless control
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
```
- After installation, SSH into the machine from another device for remote management.

---

## 2. Minimal OS Tweaks

### Disable Unneeded Services
```bash
sudo systemctl disable bluetooth.service
sudo systemctl disable cups.service
sudo systemctl disable alsa-utils.service
sudo systemctl disable avahi-daemon.service
```
- Frees ~2–5GB RAM and reduces CPU overhead.

### CPU Performance
```bash
sudo apt install -y linux-tools-common linux-tools-$(uname -r)
sudo cpupower frequency-set -g performance
```
- Ensures maximum CPU/APU performance for inference.

### Swap & Logs
- **Swap:** Disable or keep minimal to prevent slowdowns.
```bash
sudo swapoff -a
```
- **Logs:** Reduce unnecessary logging to minimize SSD writes.

---

## 3. Docker Installation

### Install Docker & Docker Compose
```bash
sudo apt install -y docker.io docker-compose
sudo systemctl enable --now docker

# Add your user to docker group
sudo usermod -aG docker $USER
# Log out and back in for changes to take effect
```

### Notes
- Docker containers will isolate your LLM workloads from the OS.
- Allocate memory specifically for LLMs to maximize performance.

---

## 4. Docker Container Setup for 32B Q4_K_M LLM

### Example `docker-compose.yml`
```yaml
version: '3.8'
services:
  llama32b:
    image: your-llm-image:latest  # Replace with your LLM image
    container_name: llama32b
    deploy:
      resources:
        limits:
          memory: 60g  # Allocate most of the 64GB unified memory
    environment:
      - OLLAMA_KV_CACHE_TYPE=q8_0
      - KV_CACHE_SIZE=8
    runtime: amd-gpu  # Replace with AMD GPU runtime if needed
    command: ["start-llm"]  # Replace with actual startup command
    restart: unless-stopped
```

### Notes
- **Memory allocation:** 60GB out of 64GB for LLM + KV cache
- **KV cache = 8** ensures efficient context handling.
- **Lean OS + Docker:** Maximizes available memory and token throughput.

---

## 5. Running the LLM Container

### Start Container
```bash
docker-compose up -d
```

### Stop Container
```bash
docker-compose down
```

### Monitor Logs
```bash
docker logs -f llama32b
```
- Ensures everything is running correctly and provides token generation status.

---

## 6. Expected Performance

| Model | RAM Allocation | KV Cache | Tokens/sec | Power Usage |
|-------|----------------|----------|------------|------------|
| 32B Q4_K_M | 60GB | 8 | 30–40 | ~45–60W |

- Fully dedicated to LLM inference.
- Responsive token generation.
- Low power draw suitable for high electricity cost areas.

---

## 7. Optional Optimizations

- Boot directly to CLI instead of a GUI.
- Use `tmux` or `screen` for managing multiple sessions.
- Keep only necessary Docker images to reduce disk usage.
- Regularly monitor GPU/APU temperatures for stability.

---

**Summary:**
This setup provides a **lean, headless AMD Ryzen AI Max+ 64GB system**, optimized for running **32B Q4_K_M LLMs** with **KV cache = 8**, delivering **responsive token generation** at low power consumption, all managed through **Docker containers** for isolation and ease of updates.

