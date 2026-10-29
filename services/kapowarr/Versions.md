# Pinned image versions

| Image | Tag | Notes |
|---|---|---|
| mrcas/kapowarr | v1.3.2 | Current stable upstream release (GitHub release V1.3.2, published 2026-09-14). Pinned by version tag, consistent with the repository convention for images that publish stable version tags (e.g. Sonarr, Radarr, Prowlarr, Ollama, Home Assistant). `latest` is not used. |

## Recorded digest (reference only)

The `mrcas/kapowarr:v1.3.2` multi-arch manifest index digest observed during
research (Docker Hub tags API) is:

```
sha256:cd3f004caff59636dde73b06df5b2f8068b485b47ff5fe82f6129562c0f2ac3b
```

At the time of research this digest was identical to `mrcas/kapowarr:latest`
(same build, pushed 2026-09-14). The compose file pins the version tag only;
digest pinning is reserved by repository convention for images that do not
publish stable version tags. If byte-exact reproducibility is later required,
append the digest to the image reference.

## Upgrade notes

- Upstream requires upgrading one minor version at a time (database migration).
- Update procedure: bump the tag here and in `compose.yaml`, then recreate the
  service through the approved deployment path.
