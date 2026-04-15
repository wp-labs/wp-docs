# Wparse

`wparse` is the main runtime entry that actually executes the parsing engine. It mainly provides two modes:

- `daemon`: persistent mode for online ingestion
- `batch`: batch mode for offline replay and validation

## Recommended Reading

- Authoritative page: [`wparse` Runtime Usage](../06-usage/cli/runtime.md)
- For admin API and reload: read [Runtime Admin Usage](../06-usage/operations/admin.md)
- For remote sync and hot reload workflows: read [Remote Project Sync and Rule Reload SOP](../06-usage/operations/project-sync.md)

## Common Entry Points

```bash
wparse --help
wparse daemon --work-root .
wparse batch --work-root .
```

## Note

This page is kept as a short navigation summary inside the aggregated docs site. For detailed runtime semantics, parameters, and operations guidance, prefer the synced content in `06-usage`.
