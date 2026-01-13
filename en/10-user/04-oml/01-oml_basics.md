# OML Basics

This document introduces the basic syntax and core concepts of OML (Object Modeling Language), helping you quickly understand the design philosophy and basic usage of OML.

## Table of Contents

1. [What is OML](#what-is-oml)
2. [Basic Syntax Structure](#basic-syntax-structure)
3. [Data Reading Modes](#data-reading-modes)
4. [Data Types](#data-types)
5. [Expressions and Operators](#expressions-and-operators)
6. [Core Constructs](#core-constructs)
   - [object Object Aggregation](#object-object-aggregation)
   - [collect Array Aggregation](#collect-array-aggregation)
   - [match Pattern Matching](#match-pattern-matching)
   - [pipe Pipeline Operations](#pipe-pipeline-operations)
7. [Advanced Features](#advanced-features)
   - [SQL Queries](#sql-queries)
   - [Batch Targets](#batch-targets)
   - [Format Strings](#format-strings)
   - [Privacy Section](#privacy-section)
8. [Comments](#comments)
9. [Common Pitfalls](#common-pitfalls)
10. [Best Practices](#best-practices)

## What is OML

OML (Object Modeling Language) is an object construction language used to assemble and aggregate parsed data. It provides powerful data transformation capabilities, converting structured input data into the desired output format.

### Core Features

- **Declarative syntax**: Describe what you want, not how to do it
- **Type safety**: Supports rich data types and automatic type inference
- **Pipeline processing**: Supports chained data transformations
- **Pattern matching**: Conditional branch processing
- **SQL integration**: Directly query databases for data enrichment

## Basic Syntax Structure

### Minimal Working Example

```oml
name : minimal
---
# Read user_id from input record; defaults to auto type when not specified
user_id = read(user_id) ;
# Call built-in time function
occur_time : time = Now::time() ;
```

### Syntax Elements

1. **Name declaration**
   ```oml
   name : <configuration_name>
   ---
   ```

2. **Separator**: `---` separates the declaration section from the configuration section

3. **Configuration entry**
   ```oml
   <target_field>[:<type>] = <expression>;
   ```

4. **Terminator**: Each entry must end with a semicolon `;`

## Data Reading Modes

OML provides two semantically distinct modes when reading input records:

### read (Non-destructive Read)

- **Characteristic**: Multiple reads of the same key still return the value
- **Mechanism**: First searches in target record dst, if not found, clones from input src
- **Use case**: Same field reused by multiple targets, or when you don't want to "consume" the source field

### take (Destructive Read)

- **Characteristic**: After reading, the key is removed from src
- **Mechanism**: Takes the value from src (and removes it), subsequent takes of the same key will fail
- **Use case**: One-time field consumption, preventing reuse by subsequent logic

### Comparison Example

```oml
name : read_take_diff
---
# Assume input src: A1=hello, B1=world

# Non-destructive read: can repeat
X1 = read(A1) ;   # X1 <- hello
X2 = read(A1) ;   # X2 <- hello (still readable)

# Destructive read: removed from src after taking
Y1 = take(B1) ;   # Y1 <- world (B1 removed from src)
Y2 = take(B1) ;   # Cannot read (B1 no longer in src)
```

### Read Parameters

read/take support the following parameters:

1. **No parameters**: Read current field
   ```oml
   value = read() ;
   ```

2. **Specify field name**
   ```oml
   value = read(user_id) ;
   ```

3. **Option parameter**: Try in priority order
   ```oml
   value = read(option:[user_id, uid]) ;
   ```

4. **Batch parameter**: Collect multiple fields
   ```oml
   value = read(keys:[sport, dport]) ;
   ```

5. **JSON path**
   ```oml
   name = read(/details[0]/name) ;
   ```

## Data Types

OML supports the following data types:

### Basic Types

- `chars` - String
- `digit` - Integer
- `float` - Floating point number
- `ip` - IP address
- `time` - Time
- `bool` - Boolean

### Composite Types

- `array` - Array
- `obj` - Object
- `auto` - Auto-infer (default)

### Type Conversion Examples

```oml
name : type_conversion
---
# Read from string and convert type
ip_addr : ip = read(src_ip) ;        # "192.168.1.1" -> IP
port_num : digit = read(port) ;      # "8080" -> 8080
cpu_usage : float = read(cpu) ;      # "85.5" -> 85.5
timestamp : time = read(time) ;      # String to time
is_active : bool = read(active) ;    # "true" -> true
```

## Expressions and Operators

### Literals

```oml
# String
name = chars("John") ;
# Number
count = digit(42) ;
# IP
addr = ip(192.168.1.1) ;
# Time
now = Now::time() ;
# Boolean
flag = bool(true) ;
```

### Pipeline Operations

```oml
# Pipeline can use pipe keyword
result = pipe read(value) | to_json ;

# Pipe keyword can also be omitted
result = read(value) | to_json ;
```

### Conditional Expressions

```oml
# match expression
quarter = match read(month) {
    in (digit(1), digit(3)) => chars(Q1) ;
    _ => chars(UNKNOWN) ;
};
```

## Core Constructs

### object Object Aggregation

Create structured objects, aggregating multiple fields:

```oml
name : object_example
---
values : obj = object {
  # Multiple targets + specified type
  cpu_free, memory_free : digit = read() ;
  # Type can be omitted (defaults to auto)
  process, disk_used = read() ;
};
```

**Notes**:
- `object { ... }` contains a set of sub-assignments `targets = <value>`
- Semicolons are optional but recommended
- Output is a nested JSON object

### collect Array Aggregation

Collect multiple fields into an array:

```oml
name : collect_example
---
# Collect multiple fields into array
ports : array = collect read(keys:[sport,dport]) ;
# Use wildcards to collect a batch
all_vals : array = collect read(keys:[metrics/*]) ;
```

### match Pattern Matching

Branch processing based on conditions:

#### Single Source Matching

```oml
name : match_single
---
quarter : chars = match read(month) {
  in (digit(1), digit(3))   => chars(Q1) ;
  in (digit(4), digit(6))   => chars(Q2) ;
  in (digit(7), digit(9))   => chars(Q3) ;
  in (digit(10), digit(12)) => chars(Q4) ;
  _ => chars(UNKNOWN) ;
};
```

#### Multiple Source Matching

```oml
name : match_double
---
X : chars = match (read(city1), read(city2)) {
  (ip(127.0.0.1), ip(127.0.0.100)) => chars(bj) ;
  _ => chars(sz) ;
};
```

**Note**: Both commas and semicolons at the end of branches are optional; using semicolons consistently is recommended.

### pipe Pipeline Operations

Chain process data:

```oml
name : pipe_example
---
# Array to JSON
ports_json = pipe read(ports) | to_json ;
# Get first element of array
first_port = pipe read(ports) | nth(0) ;
# URL parsing
host = pipe read(http_uri) | url(host) ;
# Timestamp conversion (with specified timezone)
occur_ms = pipe read(occur_time) | Time::to_ts_zone(0,ms) ;
# Base64 encoding
raw_b64 = pipe read(payload) | base64_encode ;

# Omitting the pipe keyword
host2 = read(http_uri) | url(host) ;
```

## Advanced Features

### SQL Queries

Directly query databases for data enrichment:

```oml
name : sql_example
---
# Where clause can use read/take/Now::time/constants
name,pinying = select name,pinying from example where pinying = read(py) ;

# Use string constant
_,_ = select name,pinying from example where pinying = 'xiaolongnu' ;

# Use built-in UDF (e.g., IPv4 range matching)
from_zone = select zone from zone
  where ip_start_int <= ip4_int(read(src_ip))
    and ip_end_int   >= ip4_int(read(src_ip)) ;
```

**Tip**: Basic validation is implemented for `select <columns from table>`; explicitly listing columns and using a single table name is recommended.

### Batch Targets

Process multiple targets using wildcards:

```oml
name : batch_example
---
# When target name contains *, enters batch mode; right-hand side only supports take/read
* = take() ;           # Take all fields
*/path = take() ;      # Take all fields ending with /path
aler* : auto = take() ; # Take all fields starting with aler
```

### Format Strings

```oml
name : fmt_example
---
# Supports @ref (equivalent to read(ref)) mixed with read/get
full = fmt("{}-{}", @user, read(city)) ;
```

**Note**: `@ref` is only syntactic sugar for `read(ref)` and does not support default body.

### Privacy Section

Used for data masking (not enabled by default in the engine):

```oml
name : privacy_example
---
field = read() ;
---
# Privacy processing
src_ip : privacy_ip
pos_sn : privacy_keymsg
```

## Comments

```oml
name : with_comment
---
// Single-line comments are removed during parsing
version = chars(1.0.0) ;
```

## Common Pitfalls

1. **Parameter key restrictions**: Only supports `option`, `keys`, `get`, and JSON paths; other keys are not supported
2. **Semicolons required**: Top-level entries must end with semicolon `;`
3. **match branches**: Both commas and semicolons are optional; using semicolons consistently is recommended
4. **Batch mode**: When target contains `*`, enters batch mode; right-hand side limited to `take/read`
5. **@ref limitations**: Only used as syntactic sugar in specific positions; does not support default body
6. **Timestamp timezone**: `Time::to_ts`/`Time::to_ts_ms`/`Time::to_ts_us` use UTC+8 timezone by default

## Best Practices

### 1. Naming Conventions

```oml
# Recommended: Use descriptive names
user_id = read() ;
occur_time = Now::time() ;

# Avoid: Abbreviations or meaningless names
uid = read() ;
ot = Now::time() ;
```

### 2. Type Declarations

```oml
# Recommended: Explicitly declare types
port : digit = read() ;
is_active : bool = read() ;

# Acceptable: Use auto for simple fields
name = read() ;  # Auto-inferred as chars
```

### 3. Error Handling

```oml
# Recommended: Provide default values
user_id = read() { _ : chars(unknown) } ;
version = read() { _ : chars(1.0.0) } ;
```

### 4. Organization Structure

```oml
# Recommended: Group by logic
# === Basic Fields ===
user_id = read() ;
occur_time = Now::time() ;

# === Transformed Fields ===
timestamp = pipe read(occur_time) | Time::to_ts_zone(0,ms) ;

# === Aggregated Fields ===
summary = object {
    user = read(user_id) ;
    time = read(timestamp) ;
};
```

### 5. Performance Considerations

```oml
# Recommended: Use take to reduce data copying
temp = take(data) ;
result = pipe read(temp) | to_json ;

# Avoid: Multiple reads of the same field (consider storing to target field first for reuse)
```

### 6. SQL Usage

```oml
# Recommended: Use parameterized queries
name = select name from users where id = read(user_id) ;

# Also supports string constants
name = select name from users where type = 'admin' ;
```

### 7. Pipeline Chain Length

```oml
# Recommended: Keep pipelines concise
result = pipe read(data) | to_json ;

# Avoid: Overly long pipeline chains
# bad: result = pipe read(data) | step1 | step2 | step3 | step4 | step5 ;
#      Consider using intermediate variables
```

By following these best practices, you can write clearer and more maintainable OML configurations.
