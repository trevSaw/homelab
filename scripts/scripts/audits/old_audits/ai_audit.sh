#!/bin/bash
set -euo pipefail

echo "===== AI STACK AUDIT ====="
echo "Timestamp: $(date)"
echo ""

echo "## OLLAMA MODELS"
curl -s http://localhost:11434/api/tags 2>/dev/null || echo "Ollama API unreachable"
echo ""

echo "## OLLAMA HEALTH CHECK"
curl -s http://localhost:11434/api/version 2>/dev/null || echo "No version endpoint"
echo ""

echo "## OLLAMA PROCESS CHECK"
ps aux | grep -i ollama | grep -v grep || echo "No ollama process found"
echo ""

echo "## GPU INFO (if available)"
nvidia-smi 2>/dev/null | head -n 20 || echo "No GPU or nvidia-smi unavailable"
echo ""

echo "## MEMORY USAGE (AI RELEVANT)"
ps aux --sort=-%mem | head -n 10
echo ""
