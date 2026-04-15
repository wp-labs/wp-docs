# Wprescue

`wprescue` is the dedicated entry for rescue-data processing. It is used to reprocess failed data and route it through the current project configuration.

Two things matter most:

- it only supports `batch`
- it is typically used together with an existing workspace and sink routing

## Recommended Reading

- Authoritative page: [`wprescue` And Rescue Data Usage](../06-usage/cli/rescue.md)
- For project-level commands around rescue data: read [`wproj` Project Tool Usage](../06-usage/cli/project.md)

## Common Entry Points

```bash
wprescue --help
wprescue batch --work-root .
```

## Note

This page is kept as a short navigation summary inside the aggregated docs site. For detailed usage constraints and related statistics flows, prefer the synced content in `06-usage`.
