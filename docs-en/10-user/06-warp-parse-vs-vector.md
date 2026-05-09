# WarpParse vs Vector

This page is for users evaluating tooling choices or planning a replacement. It helps answer three practical questions:

- When WarpParse is the better fit
- When Vector may still be a reasonable option
- Where the two differ in parsing model, performance, maintainability, and product completeness

## Short Conclusion

- If your core goal is **high-throughput log parsing, complex field extraction, and long-term rule engineering**, WarpParse is the stronger fit.
- If your core goal is **general-purpose data collection and broad off-the-shelf pipeline components**, Vector can still be an option.

Both can process logs, but their product centers are different:

- **WarpParse** is centered on a high-performance parsing engine plus a rule-engineering workflow
- **Vector** is centered on a general observability data pipeline

## Core Positioning

| Dimension | WarpParse | Vector |
| --- | --- | --- |
| Product position | An ETL engine focused on log parsing and security-data processing | A general data pipeline for logs, metrics, and traces |
| Main strengths | High-performance parsing, complex text extraction, rule governance | Broad connector ecosystem, general collection and forwarding, strong community reach |
| Main modeling approach | WPL + OML | TOML + VRL / built-in transforms |
| Typical scenarios | Security log normalization, heterogeneous log parsing, rule-platform workflows | Unified collection, routing, and observability-pipeline integration |
| Main concerns | Parsing accuracy, rule expressiveness, throughput, latency | Breadth of integrations, deployment convenience, ecosystem compatibility |
| Xinchuang support | More targeted, stronger compatibility | Not a primary strength |

## Parsing Model Differences

### WarpParse

WarpParse separates processing into two main stages:

- **WPL** for raw log parsing and field extraction
- **OML** for object assembly, field mapping, transformation, and output shaping

The practical benefits are:

- Parsing rules and output modeling are clearly separated
- Complex log formats remain easier to maintain
- Teams can split work between parsing-rule ownership and output-model ownership

### Vector

Vector usually uses:

- sources for input
- transforms for processing
- VRL or built-in transforms for extraction, routing, and mutation
- sinks for output

The upside is:

- fast to start
- a unified pipeline model
- convenient for collection, transformation, and forwarding in one config

The tradeoff is that once parsing logic becomes complex, rules tend to collapse into large regex blocks plus transformation scripts, which raises maintenance cost over time.

## Rule Maintenance

| Dimension | WarpParse | Vector |
| --- | --- | --- |
| Parse vs transform responsibilities | Clearly separated | Often completed along the same event-processing chain |
| Complex text logs | Better fit | Possible, but rules tend to bloat |
| Rule reuse | Better suited to rule engineering and governance | Better suited to pipeline-level config reuse |
| Debugging focus | Which WPL rule matched and how OML mapped it | How the event changes across the transform chain |

WarpParse becomes more advantageous when:

- log formats are numerous and change often
- you need stable extraction from unstructured text
- parsing rules are maintained by a dedicated team
- throughput, accuracy, and rule testability all matter

Vector remains easier when:

- the main goal is collection and forwarding, not deep parsing
- you already depend heavily on the Vector ecosystem
- log formats are relatively stable and parsing is simple
- you need quick access to many ready-made components

## Performance

Based on the benchmark data already included in this repository, WarpParse is usually much faster than Vector in parsing-heavy scenarios, especially for:

- small-message high-concurrency logs
- long-text or large-field logs
- workloads that still need field transformation after parsing
- end-to-end paths such as TCP input to file output

For example, in the `Mac M4 Mini` benchmark:

- Nginx `File -> BlackHole`: WarpParse `2,789,800 EPS`, Vector-VRL `572,076 EPS`
- APT `File -> BlackHole`: WarpParse `328,000 EPS`, Vector-VRL `37,777 EPS`

See the detailed benchmark pages for full data:

- [Benchmark Report](../20-report/benchmark.md)
- [Performance Benchmark Report](../20-report/report_mac.md)

These numbers should not be blindly generalized to every production environment. Actual results still depend on log structure, I/O topology, rule complexity, and downstream sink behavior.

## Ecosystem and Integration

| Dimension | WarpParse | Vector |
| --- | --- | --- |
| Source / Sink coverage | Under the current Chinese-doc inventory: `5` sources and `15` sinks | Broader and more mature |
| Community ecosystem | More product- and project-practice-oriented | Larger open-source ecosystem |
| Observability scenarios | Supported, but not the only center of gravity | Covers logs / metrics / traces |
| Security log engineering | Stronger fit | Possible, but usually not the best expression model |
| Xinchuang compatibility | Stronger; better aligned with domestic deployment requirements | Not a primary selling point |

Under the current documented inventory, WarpParse has:

- `Source 5`: `file`, `kafka`, `syslog`, `http`, `tcp`
- `Sink 15`: `file`, `syslog`, `prometheus`, `tcp`, `victorialogs`, `doris`, `kafka`, `mysql`, `arrow-ipc`, `elasticsearch`, `arrow-file`, `clickhouse`, `http`, `postgresql`, `dmdb`

That means WarpParse community edition is not just a parsing engine. It already has a standalone connector layer that can support real deployment.

## Xinchuang Support

For many public-sector, enterprise, and security-focused projects, the ability to land cleanly on domestic infrastructure is a separate decision factor.

WarpParse has a clearer advantage here:

- more targeted support for Xinchuang environments
- stronger compatibility in domestic deployment scenarios
- a better fit when performance, parsing capability, and domestic-platform adaptation all matter

If your project explicitly requires:

- compatibility with domestic operating systems
- adaptation to domestic hardware and software stacks
- stable rollout in Xinchuang environments

then this is a concrete advantage of WarpParse over Vector.

## Community Edition Completeness

Here, "completeness" means whether a user can independently download, learn, try, develop rules, and observe runtime behavior using the community edition.

| Dimension | WarpParse Community Edition | Vector Community Edition |
| --- | --- | --- |
| Program | Can directly run the core parsing pipeline | Can directly run a full data pipeline |
| Documentation | Documentation is already fairly complete, covering product usage, rules, configuration, connectors, tutorials, and benchmark reports | Mature documentation covering general pipeline usage and ecosystem integration |
| Examples | Has a dedicated `wp-example` project that can be downloaded and run directly | Spread across official docs, repositories, and community content |
| Rule editor | Provides a dedicated `wp-editor` | No equivalent official rule editor |
| Processing monitor | Provides a dedicated `wp-monitor` | Mostly depends on third-party tooling |
| Compatibility | Mainstream platforms plus stronger Xinchuang compatibility | Mainstream platforms |

From a community-edition completeness perspective, WarpParse has a more direct advantage:

- a complete runnable program
- a structured documentation system
- `wp-example` for direct hands-on use
- `wp-editor` for rule development
- `wp-monitor` for runtime observation
- stronger Xinchuang compatibility

So for the question "can a user independently learn, try, build rules, and observe processing with the community edition", the conclusion is:

- **WarpParse is clearly more complete than Vector**

## Common Judgment

### We already use Vector. Do we need to migrate?

If your main pain points are:

- VRL rules are getting longer and harder to maintain
- regex-based parsing is becoming fragile
- parsing throughput is insufficient
- security-log normalization is expensive

then it is worth evaluating a migration of the parsing-intensive parts first, rather than replacing everything at once.

## Next Steps

- Want the basic concepts first: see [WarpParse Core Concepts Quick Reference](00-core-concepts.md)
- Want to run a local example quickly: see [Getting Started](01-getting-started.md)
- Want the full benchmark data: see [Benchmark Report](../20-report/benchmark.md)
