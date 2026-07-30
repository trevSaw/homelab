# Diff vs prior compose source

- CasaOS project name was glorious_thomas; repo project name=prowlarr
- CasaOS image listed cr.hotio.dev/hotio/prowlarr:latest; live image is ghcr.io/hotio/prowlarr:latest — import uses live
- CasaOS bind was /DATA/AppData//config (double slash); import normalizes to /DATA/AppData/config (same path)
- Stripped x-casaos metadata and CasaOS icon label
