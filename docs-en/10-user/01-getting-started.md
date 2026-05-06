# Getting Started

## Prerequisites

- [Download wparse](https://github.com/wp-labs/warp-parse/releases)
- Copy it to an executable path, such as `/usr/local/bin` or `/${HOME}/bin`

## 1. Initialize the Working Directory

```bash
wproj init --mode full
wproj check
```

After execution, the working directory will contain:

```
├── conf
│   ├── wparse.toml
│   └── wpgen.toml
├── connectors
│   ├── sink.d
│   └── source.d
├── data
│   ├── in_dat
│   ├── logs
│   ├── out_dat
│   └── rescue
├── models
│   ├── knowledge
│   ├── oml
│   └── wpl
└── topology
    ├── sinks
    └── sources
```

## 2. Generate Data and Clean Up

```bash
wproj data clean
wpgen data clean

# Generate sample data (example: 3000 lines, 3-second stats interval)
wpgen sample -n 3000 --stat 3
```

## 3. Run Parsing

```bash
# Batch mode (-p prints stats; check ./logs/ if something fails)
wparse batch --stat 3 -p
```

## 4. Collect Statistics

```bash
# Statistics for both sources and file sinks
wproj data stat
```

## Next Steps

- For core concepts and terminology: read [WarpParse Core Concepts Quick Reference](00-core-concepts.md)
- For the full product, CLI, and operations manual: read [CLI Usage Guide](01-cli/README.md)
- For language details: read [WPL Rule Language](03-wpl/README.md) and [OML Object Model Language](04-oml/README.md)
