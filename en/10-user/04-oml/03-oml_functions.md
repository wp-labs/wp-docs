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
# Output example: 20251225
```

#### `Now::hour()`

Get the current time precise to the hour as an integer in `YYYYMMDDHH` format.

**Return Type**: `digit`

**Example**:

```oml
current_hour : digit = Now::hour() ;
# Output example: 2025122515
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

- `encoding` (optional): Character encoding after decoding, supports `Utf8` (default), `Imap` (IMAP variant, handles non-ASCII characters)

**Input**: `chars`
**Output**: `chars`

**Example**:

```oml
# Standard UTF-8 decoding
decoded = pipe read(data) | base64_decode ;
decoded = pipe read(data) | base64_decode(Utf8) ;

# IMAP variant decoding (handles binary/non-ASCII data)
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

- `<` -> `&lt;`
- `>` -> `&gt;`
- `&` -> `&amp;`
- `"` -> `&quot;`
- `'` -> `&#x27;`

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

Convert time to Unix timestamp (seconds).

**Syntax**: `Time::to_ts`

**Input**: `time`
**Output**: `digit`

**Example**:

```oml
timestamp = pipe read(occur_time) | Time::to_ts ;
# 2000-10-10 00:00:00 -> 971107200
```

#### `Time::to_ts_ms`

Convert time to Unix timestamp (milliseconds).

**Syntax**: `Time::to_ts_ms`

**Input**: `time`
**Output**: `digit`

**Example**:

```oml
timestamp_ms = pipe read(occur_time) | Time::to_ts_ms ;
# 2000-10-10 00:00:00 -> 971107200000
```

#### `Time::to_ts_us`

Convert time to Unix timestamp (microseconds).

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

- `timezone_offset`: Timezone offset (hours), e.g., `0` for UTC, `8` for UTC+8
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

Get the value at a specified path in an object.

**Syntax**: `get(<path>)`

**Parameters**:

- `path`: Object path, using `/` to separate nested levels

**Input**: `obj`
**Output**: Field value type

**Example**:

```oml
# Get value from nested object
name = pipe read(user) | get(profile/name) ;

# Combined with nth
first_name = pipe read(users) | nth(0) | get(name) ;
```

#### `path`

Extract a specified part from a file path.

**Syntax**: `path(<part>)`

**Parameters**:

- `part`: Part to extract
  - `name`: Filename (with extension)
  - `path`: Directory path

**Input**: `chars`
**Output**: `chars`

**Example**:

```oml
# Input: "C:\Users\test\file.txt"
filename = pipe read(file_path) | path(name) ;   # "file.txt"
stem = pipe read(file_path) | path(stem) ;       # "file"
ext = pipe read(file_path) | path(ext) ;         # "txt"
dir = pipe read(file_path) | path(dir) ;         # "C:\Users\test"
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

- `field_name`: Field name to extract

**Input**: `chars`
**Output**: `chars`

**Example**:

```oml
# Extract fields from formatted text
status = pipe read(log_line) | sxf_get(statusCode) ;
password = pipe read(log_line) | sxf_get(password) ;
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

**Input**: `ip`
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

# Convert to various timestamp formats
ts_seconds = pipe read(occur_time) | Time::to_ts ;
ts_millis = pipe read(occur_time) | Time::to_ts_ms ;

# With timezone
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
file_ext = pipe read(file_path) | path(ext) ;

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

## Version Notes

The following is a historical changelog for function naming:

| Old Name | New Name | Description |
|----------|----------|-------------|
| `Time::now` | `Now::time` | Moved to Now namespace |
| `Time::now_date` | `Now::date` | Moved to Now namespace |
| `Time::now_hour` | `Now::hour` | Moved to Now namespace |
| `to_timestamp` | `Time::to_ts` | Moved to Time namespace |
| `to_timestamp_ms` | `Time::to_ts_ms` | Moved to Time namespace |
| `to_timestamp_us` | `Time::to_ts_us` | Moved to Time namespace |
| `to_timestamp_zone` | `Time::to_ts_zone` | Moved to Time namespace |
| `arr_get` | `nth` | Simplified naming |
| `obj_get` | `get` | Simplified naming |
| `path_get` | `path` | Simplified naming |
| `url_get` | `url` | Simplified naming |
| `base64_en` | `base64_encode` | Clearer naming |
| `base64_de` | `base64_decode` | Clearer naming |
| `html_escape_en` | `html_escape` | Simplified naming |
| `html_escape_de` | `html_unescape` | Using unescape is more accurate |
| `json_escape_en` | `json_escape` | Simplified naming |
| `json_escape_de` | `json_unescape` | Using unescape is more accurate |
| `str_escape_en` | `str_escape` | Simplified naming |
| `skip_if_empty` | `skip_empty` | Simplified naming |
| `to_string` | `to_str` | Simplified naming |
| `to_ip4_int` | `ip4_to_int` | Unified naming style |
