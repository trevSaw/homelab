# Pinned image versions

| Image | Tag | Pinned as | Notes |
|---|---|---|---|
| `ghcr.io/angelosha/uchiyomi` | *(none)* | `@sha256:a3b5ccc3d6ffd9b6544c968df7cb286bf79889db458ad12b4b6e3086a67128ea` | Upstream v0.55.6 (released 2026-10-06). GHCR publishes **only `latest`**; no version tags exist, so per repository convention the image is pinned by digest rather than by tag. |
| `ghcr.io/flaresolverr/flaresolverr` | `v3.5.2` | `v3.5.2@sha256:c80ae007ce2ccdcd217a12426e4f039ef763ff90738c808d38810c3e59323767` | Current stable upstream release. Tag + digest pinned. |
| `ghcr.io/suwayomi/suwayomi-server` | `v2.3.2243` | `v2.3.2243@sha256:e59f212ccf91b26de8676a063a2db90256c148c6261535c7c477d47a43d9751b` | Version used by upstream's own `deploy/docker-compose.yml`. Tag + digest pinned. |

## Digest convention

Repository convention pins images by stable version tag where the project publishes
one (`flaresolverr`, `suwayomi-server`), and by digest where it does **not**
(`uchiyomi`). `latest` is never used in `compose.yaml`.

The digests above are the multi-arch manifest-index digests resolved from GHCR on
2026-10-07 (amd64 + arm64 manifests under one index).

## Upgrade procedure

1. Resolve the new upstream version / digest:
   - App: read the release on `github.com/AngeloSha/uchiyomi/releases/latest`, then
     `docker manifest inspect ghcr.io/angelosha/uchiyomi:latest` (or the GHCR
     tags API) for the new index digest.
   - Sidecars: pick the new tag, then resolve its digest the same way.
2. Bump the image reference(s) here and in `compose.yaml`.
3. `docker compose pull && docker compose up -d` from `services/uchiyomi/`.
4. Verify `/livez` and `Admin → Health`; volumes and database migrate themselves.
