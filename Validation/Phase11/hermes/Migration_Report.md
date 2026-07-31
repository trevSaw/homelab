# Phase 11 — Hermes Migration Report

**Service:** hermes  
**Batch:** 04  
**Final status:** SOAK FAILED  
**Completed:** 2026-07-30T11:15:30Z

## Summary

Already on appdata (`migration_required=no`). Framework inventory OK. Smoke **failed** due to uid mismatch (process 10000 vs data 1000) causing kanban `PermissionError`. UI login redirect still works.

## Required remediation (before READY FOR SOAK)

In a maintenance window, either:

1. `chown -R 10000:10000 /mnt/monarch/appdata/hermes` (match runtime user), **or**
2. Align compose/`user:` so the process matches current ownership,

then confirm kanban ticks without `PermissionError` and re-smoke.

## Final decision

**SOAK FAILED**
