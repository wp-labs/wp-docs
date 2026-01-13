# OML Functions Reference

This document provides detailed information about all available built-in functions and pipe functions in OML.

## Table of Contents

1. [Built-in Functions](#built-in-functions)
   - [Now Namespace](#now-namespace)
2. [Pipe Functions](#pipe-functions)
   - [Encoding Functions](#encoding-functions)
   - [Escape Functions](#escape-functions)
   - [Time Functions](#time-functions)
   - [Data Access Functions](#data-access-functions)
   - [Conversion Functions](#conversion-functions)
   - [Control Functions](#control-functions)

---

## Built-in Functions

Built-in functions can be used directly in assignment expressions without the `pipe` keyword.

### Now Namespace

Functions for getting current time-related values.

#### `Now::time()`

Get the current time.

**Return Type**: `time`

**Example**:
```oml
occur_time : time = Now::time() ;
```

#### `Now::date()`

Get the current date as an integer in `YYYYMMDD` format.

**Return Type**: `digit`

**Example**:
```oml
today : digit = Now::date() ;
# Output example: 20251225 (represents December 25, 2025)
```

#### `Now::hour()`

Get the current time precise to the hour as an integer in `YYYYMMDDHH` format.

**Return Type**: `digit`

**Example**:
```oml
current_hour : digit = Now::hour() ;
# Output example: 2025122515 (represents December 25, 2025 at 15:00)
```

---

## Pipe Functions

Pipe functions are chained using the `pipe` keyword and `|` operator.

```oml
result = pipe read(field) | function1 | function2(param) ;
```

---

### Encoding Functions

#### `base64_encode`

Encode a string to Base64.

**Syntax**: `base64_encode`

**Input**: `chars`
**Output**: `chars`

**Example**:
```oml
encoded = pipe read(payload) | base64_encode ;
# "hello" -> "aGVsbG8="
```

#### `base64_decode`

Decode a Base64 encoded string.

**Syntax**: `base64_decode` | `base64_decode(<encoding>)`

**Parameters**:
- `encoding` (optional): Character encoding after decoding, default is `Utf8`

**Input**: `chars`
**Output**: `chars`

**Example**:
```oml
# Standard UTF-8 decoding
decoded = pipe read(data) | base64_decode ;
decoded = pipe read(data) | base64_decode(Utf8) ;

# GBK Chinese decoding
gbk_text = pipe read(gbk_data) | base64_decode(Gbk) ;

# IMAP variant decoding (handles binary/non-ASCII data, escapes to readable format)
raw = pipe read(binary_data) | base64_decode(Imap) ;
```

---

### Escape Functions

#### `html_escape`

Escape HTML special characters.

**Syntax**: `html_escape`

**Input**: `chars`
**Output**: `chars`

**Escape Rules**:
- `<` → `&lt;`
- `>` → `&gt;`
- `&` → `&amp;`
- `"` → `&quot;`
- `'` → `&#x27;`

**Example**:
```oml
safe_html = pipe read(user_input) | html_escape ;
# "<script>" -> "&lt;script&gt;"
```

#### `html_unescape`

Restore HTML entities to original characters.

**Syntax**: `html_unescape`

**Input**: `chars`
**Output**: `chars`

**Example**:
```oml
original = pipe read(escaped_html) | html_unescape ;
# "&lt;div&gt;" -> "<div>"
```

#### `json_escape`

Escape special characters in JSON strings.

**Syntax**: `json_escape`

**Input**: `chars`
**Output**: `chars`

**Example**:
```oml
json_safe = pipe read(text) | json_escape ;
# Escapes quotes, backslashes, control characters, etc.
```

#### `json_unescape`

Restore JSON escape sequences to original characters.

**Syntax**: `json_unescape`

**Input**: `chars`
**Output**: `chars`

**Example**:
```oml
original = pipe read(escaped_json) | json_unescape ;
```

#### `str_escape`

Escape special characters in strings (mainly quotes and backslashes).

**Syntax**: `str_escape`

**Input**: `chars`
**Output**: `chars`

**Example**:
```oml
escaped = pipe read(raw_string) | str_escape ;
# 'hello"world' -> 'hello\"world'
```

---

### Time Functions

#### `Time::to_ts`

Convert time to Unix timestamp (seconds). Uses UTC+8 timezone.

**Syntax**: `Time::to_ts`

**Input**: `time`
**Output**: `digit`

**Example**:
```oml
timestamp = pipe read(occur_time) | Time::to_ts ;
# 2000-10-10 00:00:00 -> 971107200
```

#### `Time::to_ts_ms`

Convert time to Unix timestamp (milliseconds). Uses UTC+8 timezone.

**Syntax**: `Time::to_ts_ms`

**Input**: `time`
**Output**: `digit`

**Example**:
```oml
timestamp_ms = pipe read(occur_time) | Time::to_ts_ms ;
# 2000-10-10 00:00:00 -> 971107200000
```

#### `Time::to_ts_us`

Convert time to Unix timestamp (microseconds). Uses UTC+8 timezone.

**Syntax**: `Time::to_ts_us`

**Input**: `time`
**Output**: `digit`

**Example**:
```oml
timestamp_us = pipe read(occur_time) | Time::to_ts_us ;
# 2000-10-10 00:00:00 -> 971107200000000
```

#### `Time::to_ts_zone`

Convert time to Unix timestamp with specified timezone.

**Syntax**: `Time::to_ts_zone(<timezone_offset>, <unit>)`

**Parameters**:
- `timezone_offset`: Timezone offset (hours), e.g., `0` for UTC, `8` for UTC+8, `-5` for UTC-5
- `unit`: Timestamp unit
  - `s` or `ss`: Seconds
  - `ms`: Milliseconds
  - `us`: Microseconds

**Input**: `time`
**Output**: `digit`

**Example**:
```oml
# UTC timestamp (seconds)
utc_ts = pipe read(occur_time) | Time::to_ts_zone(0, ss) ;

# UTC+8 timestamp (milliseconds)
beijing_ts_ms = pipe read(occur_time) | Time::to_ts_zone(8, ms) ;

# UTC-5 timestamp (seconds)
eastern_ts = pipe read(occur_time) | Time::to_ts_zone(-5, s) ;

# UTC timestamp (microseconds)
utc_ts_us = pipe read(occur_time) | Time::to_ts_zone(0, us) ;
```

---

### Data Access Functions

#### `nth`

Get the element at a specified index in an array.

**Syntax**: `nth(<index>)`

**Parameters**:
- `index`: Array index (starting from 0)

**Input**: `array`
**Output**: Element type of the array

**Example**:
```oml
first_item = pipe read(items) | nth(0) ;
third_item = pipe read(items) | nth(2) ;
```

#### `get`

Get the value of a specified key in an object.

**Syntax**: `get(<key>)`

**Parameters**:
- `key`: Object field name

**Input**: `obj`
**Output**: Field value type

**Example**:
```oml
# Get object field value
name = pipe read(user) | get(name) ;

# Combined with nth
first_name = pipe read(users) | nth(0) | get(name) ;
```

#### `path`

Extract a specified part from a file path.

**Syntax**: `path(<part>)`

**Parameters**:
- `part`: Part to extract
  - `name`: Filename (with extension)
  - `path`: Parent directory path

**Input**: `chars`
**Output**: `chars`

**Example**:
```oml
# Input: "C:\Users\test\file.txt"
filename = pipe read(file_path) | path(name) ;   # "file.txt"
parent = pipe read(file_path) | path(path) ;     # "C:/Users/test"
```

#### `url`

Extract a specified part from a URL.

**Syntax**: `url(<part>)`

**Parameters**:
- `part`: Part to extract
  - `domain`: Domain (without port)
  - `host`: Host (with port)
  - `path`: Path
  - `uri`: Complete URI (path + query + fragment)
  - `params`: Query parameters

**Input**: `chars`
**Output**: `chars`

**Example**:
```oml
# Input: "https://api.example.com:8080/v1/users?id=1#section"
domain = pipe read(http_url) | url(domain) ;  # "api.example.com"
host = pipe read(http_url) | url(host) ;      # "api.example.com:8080"
path = pipe read(http_url) | url(path) ;      # "/v1/users"
uri = pipe read(http_url) | url(uri) ;        # "/v1/users?id=1#section"
params = pipe read(http_url) | url(params) ;  # "id=1"
```

#### `sxf_get`

Extract field values from specially formatted text (used to parse special format logs or messages).

**Syntax**: `sxf_get(<field_name>)`

**Parameters**:
- `field_name`: Field name to extract (only letters and numbers supported)

**Input**: `chars`
**Output**: `chars`

**Example**:
```oml
# Extract fields from formatted text
status = pipe read(log_line) | sxf_get(statusCode) ;
username = pipe read(log_line) | sxf_get(username) ;
```

---

### Conversion Functions

#### `to_str`

Convert a value to string.

**Syntax**: `to_str`

**Input**: Any type
**Output**: `chars`

**Example**:
```oml
ip_str = pipe read(src_ip) | to_str ;
num_str = pipe read(count) | to_str ;
```

#### `to_json`

Convert a value to JSON string.

**Syntax**: `to_json`

**Input**: Any type
**Output**: `chars`

**Example**:
```oml
# Array to JSON
ports_json = pipe read(ports) | to_json ;
# [80, 443] -> "[80,443]"

# Object to JSON
user_json = pipe read(user) | to_json ;
# {name: "John", age: 30} -> '{"name":"John","age":30}'
```

#### `ip4_to_int`

Convert IPv4 address to integer.

**Syntax**: `ip4_to_int`

**Input**: `ip` or `chars`
**Output**: `digit`

**Example**:
```oml
ip_int = pipe read(src_ip) | ip4_to_int ;
# 127.0.0.1 -> 2130706433
# 10.0.0.1 -> 167772161
```

---

### Control Functions

#### `skip_empty`

Skip the field output if the input value is empty (empty string, empty array, zero value, etc.).

**Syntax**: `skip_empty`

**Input**: Any type
**Output**: Original type or skipped

**Example**:
```oml
# If optional_field is empty, result field will not be output
result = pipe read(optional_field) | skip_empty ;

# Commonly used to filter empty arrays
items = pipe read(items_array) | skip_empty ;
```

---

## Function Combination Examples

### Example 1: Time Processing

```oml
name : time_processing
---
# Get current time
occur_time : time = Now::time() ;

# Convert to various timestamp formats (using default UTC+8 timezone)
ts_seconds = pipe read(occur_time) | Time::to_ts ;
ts_millis = pipe read(occur_time) | Time::to_ts_ms ;

# Specify timezone
ts_utc = pipe read(occur_time) | Time::to_ts_zone(0, ss) ;
ts_beijing = pipe read(occur_time) | Time::to_ts_zone(8, ms) ;
```

### Example 2: Data Extraction and Conversion

```oml
name : data_extraction
---
# URL parsing
request_host = pipe read(http_url) | url(host) ;
request_path = pipe read(http_url) | url(path) ;

# File path processing
file_name = pipe read(file_path) | path(name) ;

# Array processing
first_port = pipe read(ports) | nth(0) ;
ports_json = pipe read(ports) | to_json ;
```

### Example 3: Encoding and Escaping

```oml
name : encoding_example
---
# Base64 encode/decode
encoded_payload = pipe read(raw_data) | base64_encode ;
decoded_data = pipe read(b64_data) | base64_decode ;

# Use GBK encoding to decode Chinese
gbk_decoded = pipe read(gbk_b64) | base64_decode(Gbk) ;

# HTML safety processing
safe_content = pipe read(user_input) | html_escape ;

# JSON processing
json_safe_str = pipe read(text) | json_escape ;
```

### Example 4: Chained Processing

```oml
name : chained_processing
---
# Get a specific field from the first element of an array
first_user_name = pipe read(users) | nth(0) | get(name) ;

# Encode then Base64
encoded_json = pipe read(data) | to_json | base64_encode ;

# Convert IP to integer then skip if empty
ip_int = pipe read(src_ip) | ip4_to_int | skip_empty ;
```

---

## Function Summary Table

### Built-in Functions

| Function | Description | Return Type |
|----------|-------------|-------------|
| `Now::time()` | Get current time | `time` |
| `Now::date()` | Get current date (YYYYMMDD) | `digit` |
| `Now::hour()` | Get current time to the hour (YYYYMMDDHH) | `digit` |

### Pipe Functions

| Function | Description | Input Type | Output Type |
|----------|-------------|------------|-------------|
| `base64_encode` | Base64 encoding | `chars` | `chars` |
| `base64_decode` | Base64 decoding | `chars` | `chars` |
| `html_escape` | HTML escape | `chars` | `chars` |
| `html_unescape` | HTML unescape | `chars` | `chars` |
| `json_escape` | JSON escape | `chars` | `chars` |
| `json_unescape` | JSON unescape | `chars` | `chars` |
| `str_escape` | String escape | `chars` | `chars` |
| `Time::to_ts` | Time to timestamp (seconds) | `time` | `digit` |
| `Time::to_ts_ms` | Time to timestamp (milliseconds) | `time` | `digit` |
| `Time::to_ts_us` | Time to timestamp (microseconds) | `time` | `digit` |
| `Time::to_ts_zone` | Time to specified timezone timestamp | `time` | `digit` |
| `nth` | Get array element | `array` | Element type |
| `get` | Get object field | `obj` | Field type |
| `path` | Extract file path part | `chars` | `chars` |
| `url` | Extract URL part | `chars` | `chars` |
| `sxf_get` | Extract special format field | `chars` | `chars` |
| `to_str` | Convert to string | Any | `chars` |
| `to_json` | Convert to JSON | Any | `chars` |
| `ip4_to_int` | IPv4 to integer | `ip`/`chars` | `digit` |
| `skip_empty` | Skip empty values | Any | Any |
