# crafty

Phase 10.75 repository import of the live deployment.

## Purpose
Crafty Controller (Minecraft server manager)

## Runtime
- Container(s): `big-bear-crafty`
- Compose: `services/crafty/compose.yaml`
- Former source of truth: CasaOS `big-bear-crafty`

## Important
This import **does not** migrate storage. Bind mounts are unchanged from the live container.

## Operations
```bash
cd services/crafty
cp -n .env.example .env   # if required
docker compose -f compose.yaml config
# Do not recreate unless cutting over from CasaOS/Portainer intentionally
```

## Documentation
See `Documentation/services/crafty/`.
