# LEGACY COMPOSE OWNERSHIP — DO NOT USE
#
# As of Phase 14.2 preflight (2026-08-01), Docker Compose ownership for Ollama
# moved to:
#
#   /home/fatherfrank/projects/homelab/services/ollama/compose.yaml
#
# This directory (/hive/ollama) remains the **model/runtime data bind** only:
#   - models/
#   - cache/
#   - other Ollama state under /root/.ollama
#
# The Docker network ollama_ollama-net must NOT be deleted.
# Do not run `docker compose down` from this directory.
#
# Archived compose: compose.yml.LEGACY-DO-NOT-USE
