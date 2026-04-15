# Wpgen

`wpgen` is the Warp Parse test-data generation tool. It is mainly used to:

- initialize and validate generator configuration
- generate test data from rules
- generate replay or integration data from samples

## Recommended Reading

- Authoritative page: [`wpgen` Generator Usage](../06-usage/cli/generator.md)
- If you do not have a workspace yet: read [Getting Started](../01-getting-started.md)
- If you want the overall CLI split: read [Warp Parse CLI Usage Guide](../06-usage/cli/index.md)

## Common Entry Points

```bash
wpgen --help
wpgen conf init --work-root .
wpgen conf check --work-root .
```

## Note

This page is kept as a short navigation summary inside the aggregated docs site. For detailed configuration, subcommands, and runtime semantics, prefer the synced content in `06-usage`.
