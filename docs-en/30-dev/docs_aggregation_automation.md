# Docs Aggregation Automation

## Goal

This repository is acting as a documentation aggregation layer. The weak point is not mdBook itself, but the way upstream content is copied here: it is still driven by manual scripts and manual commits.

The automation should solve four things:

1. Upstream sources must be configuration-driven.
2. Local sync and CI sync must use the same entry point.
3. `SUMMARY.md` should be regenerated automatically after sync.
4. Aggregated changes should enter the default branch through pull requests.

## Proposed Structure

The implementation is split into three parts:

1. `docs-sources.json`
   - Declares every upstream documentation source.
   - Each source defines the repo, branch, local development path, and source-to-target mappings.
2. `scripts/sync_docs.py`
   - Performs the actual sync.
   - Supports both local paths and git-based checkouts in CI.
   - Default strategy is additive and non-destructive: create missing files and update changed files, without deleting destination-only files.
3. `.github/workflows/sync-docs.yml`
   - Runs on schedule, manual dispatch, or `repository_dispatch` from upstream repos.
   - Opens a pull request with the aggregated changes.

## Current Example

The current `wp-motor/docs/usage` flow is now represented as a source entry:

```json
{
  "sources": [
    {
      "name": "wp-motor-usage",
      "repo": "https://github.com/wp-labs/wp-motor.git",
      "ref": "main",
      "checkout_subdir": "docs/usage",
      "local_path": "../wp-motor/docs/usage",
      "mappings": [
        { "from": "zh", "to": "docs-zh/10-user" },
        { "from": "en", "to": "docs-en/10-user" }
      ]
    }
  ]
}
```

Adding a new upstream repo now only requires another source object entry.

## Usage

Local sync:

```bash
make sync
```

Preview changes only:

```bash
make sync-dry-run
```

Sync one source with a temporary local override:

```bash
python3 scripts/sync_docs.py \
  --source wp-motor-usage \
  --local-override wp-motor-usage=../wp-motor/docs/usage \
  --generate-summary
```

Legacy compatibility entry point:

```bash
bash sync-usage-docs.sh ../wp-motor/docs/usage
```

## CI Recommendation

Keep three trigger modes in `sync-docs.yml`:

1. `schedule`
   - Serves as a fallback.
2. `workflow_dispatch`
   - Allows manual reruns.
3. `repository_dispatch`
   - Lets upstream repos notify this repo after docs changes land.

If the upstream repositories are private, provide `DOCS_SYNC_TOKEN` so the sync job can clone them.

## Recommended Upstream Trigger

Each upstream repo can add a lightweight workflow that emits `repository_dispatch` when its docs path changes. The resulting chain becomes:

`upstream docs change -> notify wp-docs -> wp-docs pulls latest docs -> automated PR`

This is preferable to pushing directly into the aggregation repo because the sync logic stays centralized and every aggregated change remains reviewable.

## Next Steps

As the number of sources grows, the next practical improvements are:

1. Add explicit `delete = true/false` behavior per source.
2. Add destination path allowlists so sync can only write into approved directories.
3. Run Markdown validation and mdBook build after sync.
4. Record upstream commit SHAs in the generated PR description.
