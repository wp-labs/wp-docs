# OML Practical Examples

This document provides a rich collection of practical OML examples. Each example includes complete input data, OML configuration, and expected output to help you quickly master various OML usages.

## Table of Contents

1. [Basic Operations Examples](#basic-operations-examples)
2. [Data Type Conversion](#data-type-conversion)
3. [Pipeline Operations Examples](#pipeline-operations-examples)
4. [Conditional Matching Examples](#conditional-matching-examples)
5. [Array Operations Examples](#array-operations-examples)
6. [Object Aggregation Examples](#object-aggregation-examples)
7. [Wildcard Pattern Examples](#wildcard-pattern-examples)
8. [SQL Query Examples](#sql-query-examples)
9. [Advanced Pipeline Operations](#advanced-pipeline-operations)
10. [Real-World Cases](#real-world-cases)
11. [Comprehensive Examples](#comprehensive-examples)

## Basic Operations Examples

### 1. Simple Field Reading

**Input Data**:
```
user_id = "user123"
username = "john_doe"
email = "john@example.com"
```

**OML Configuration**:
```oml
name : simple_read
---
# Read specified field
uid = read(user_id) ;
name = read(username) ;

# Use take (destructive read)
email = take(email) ;
```

**Output Result**:
```
uid = "user123"
name = "john_doe"
email = "john@example.com"
```

### 2. Reading with Default Values

**Input Data**:
```
user_id = "user123"
# country field does not exist
```

**OML Configuration**:
```oml
name : read_with_default
---
# Use default value when field doesn't exist
country = read() { _ : chars(CN) } ;
version = read() { _ : chars(1.0) } ;

# Normal read for existing field
user_id = read() ;
```

**Output Result**:
```
country = "CN"
version = "1.0"
user_id = "user123"
```

### 3. Multi-Option Reading

**Input Data**:
```
# id field does not exist
uid = "user456"
```

**OML Configuration**:
```oml
name : option_read
---
# Try multiple fields, return by priority
user_id = read(option:[id, uid, user_id]) ;
```

**Output Result**:
```
user_id = "user456"  # uid exists, returned
```

### 4. JSON Path Reading

**Input Data**:
```
/details[0]/name = "process1"
/details[0]/pid = "1001"
/details[1]/name = "process2"
/details[1]/pid = "1002"
/user/info/name = "John"
/user/info/age = "30"
```

**OML Configuration**:
```oml
name : json_path_read
---
# Read JSON path
first_process = read(/details[0]/name) ;
first_pid = read(/details[0]/pid) ;
username = read(/user/info/name) ;
age = read(/user/info/age) ;
```

**Output Result**:
```
first_process = "process1"
first_pid = "1001"
username = "John"
age = "30"
```

## Data Type Conversion

### 1. Basic Type Conversion

**Input Data**:
```
ip_addr = "192.168.1.100"
port = "8080"
cpu_usage = "85.5"
is_active = "true"
event_time = "2024-01-15 14:30:00"
```

**OML Configuration**:
```oml
name : type_conversion
---
ip : ip = read(ip_addr) ;
port : digit = read() ;
cpu : float = read() ;
active : bool = read() ;
time : time = read() ;
```

**Output Result**:
```
ip = 192.168.1.100     # IP type
port = 8080             # Integer
cpu = 85.5              # Float
active = true           # Boolean
time = "2024-01-15 14:30:00"  # Time type
```

### 2. Time Conversion Example

**Input Data**:
```
log_time = "15/Jan/2024:14:30:00 +0800"
```

**OML Configuration**:
```oml
name : time_conversion
---
# Use time functions to get current time
now = Now::time() ;
now_date = Now::date() ;
now_hour = Now::hour() ;
```

**Output Result**:
```
now = "2024-01-15 14:30:45"   # Current time (time type)
now_date = 20240115           # Current date (digit type, format YYYYMMDD)
now_hour = 2024011514         # Current hour (digit type, format YYYYMMDDHH)
```

## Pipeline Operations Examples

### 1. Timestamp Conversion

**Input Data**:
```
occur_time = "2024-01-15 14:30:00"
```

**OML Configuration**:
```oml
name : timestamp_conversion
---
# Use Time::to_ts_zone to specify timezone and precision
ts_ss = pipe read(occur_time) | Time::to_ts_zone(0, ss) ;
ts_ms = pipe read(occur_time) | Time::to_ts_zone(0, ms) ;
ts_us = pipe read(occur_time) | Time::to_ts_zone(0, us) ;
# Use s as shorthand for seconds
ts_utc8 = pipe read(occur_time) | Time::to_ts_zone(8, s) ;
```

**Output Result**:
```
ts_ss = 1705318200          # Seconds
ts_ms = 1705318200000       # Milliseconds
ts_us = 1705318200000000    # Microseconds
ts_utc8 = 1705289400        # UTC+8 timezone seconds
```

**Notes**:
- `Time::to_ts`, `Time::to_ts_ms`, `Time::to_ts_us` use UTC+8 timezone by default
- `Time::to_ts_zone(timezone, unit)` can specify timezone and precision, unit supports `s`/`ss` (seconds), `ms` (milliseconds), `us` (microseconds)

### 2. Array Operations Pipeline

**Input Data**:
```
sport = "8080"
dport = "443"
protocol = "tcp"
```

**OML Configuration**:
```oml
name : array_pipe
---
# Collect ports into array
ports = collect read(keys:[sport, dport]) ;
# Convert to JSON
ports_json = pipe read(ports) | to_json ;
# Get first port
first_port = pipe read(ports) | nth(0) ;
```

**Output Result**:
```
ports = [8080, 443]                    # Array
ports_json = "[8080,443]"              # JSON string
first_port = 8080                      # First element
```

### 3. URL Parsing Pipeline

**Input Data**:
```
url = "https://www.example.com:8080/path/to/resource?param1=value1&param2=value2#section"
```

**OML Configuration**:
```oml
name : url_parsing
---
domain = pipe read(url) | url(domain) ;
host = pipe read(url) | url(host) ;
path = pipe read(url) | url(path) ;
uri = pipe read(url) | url(uri) ;
params = pipe read(url) | url(params) ;
```

**Output Result**:
```
domain = "www.example.com"
host = "www.example.com:8080"
path = "/path/to/resource"
uri = "/path/to/resource?param1=value1&param2=value2#section"
params = "param1=value1&param2=value2"
```

### 4. Encoding Conversion Pipeline

**Input Data**:
```
message = "Hello, OML!"
html = "<script>alert('xss')</script>"
```

**OML Configuration**:
```oml
name : encoding_pipe
---
# Base64 encode/decode
b64_encoded = pipe read(message) | base64_encode ;
b64_decoded = pipe read(b64_encoded) | base64_decode ;

# Use specified encoding for Base64 decode (supports multiple character encodings)
gbk_decoded = pipe read(gbk_data) | base64_decode(Gbk) ;
imap_decoded = pipe read(binary_data) | base64_decode(Imap) ;

# HTML escape
html_escaped = pipe read(html) | html_escape ;
html_unescaped = pipe read(html_escaped) | html_unescape ;

# JSON escape
json_escaped = pipe read(json_text) | json_escape ;
json_unescaped = pipe read(json_escaped) | json_unescape ;
```

**Output Result**:
```
b64_encoded = "SGVsbG8sIE9NTCE="
b64_decoded = "Hello, OML!"
html_escaped = "&lt;script&gt;alert(&#x27;xss&#x27;)&lt;/script&gt;"
html_unescaped = "<script>alert('xss')</script>"
```

**Notes**:
`base64_decode` supports multiple character encodings, see [Functions Reference](./03-oml_functions.md#base64_decode). Common ones include:
- `Utf8` (default): Standard UTF-8 encoding
- `Gbk`: GBK Chinese encoding
- `Imap`: Escapes non-ASCII bytes to `\xNN` format, suitable for binary data processing

## Conditional Matching Examples

### 1. Quarter Determination

**Input Data**:
```
month = "6"  # June
```

**OML Configuration**:
```oml
name : quarter_match
---
quarter = match read(month) {
    in (digit(1), digit(3)) => chars(Q1) ;
    in (digit(4), digit(6)) => chars(Q2) ;
    in (digit(7), digit(9)) => chars(Q3) ;
    in (digit(10), digit(12)) => chars(Q4) ;
    _ => chars(Invalid) ;
};
```

**Output Result**:
```
quarter = "Q2"  # June belongs to Q2
```

### 2. Port Service Identification

**Input Data**:
```
port = "22"
```

**OML Configuration**:
```oml
name : port_service_match
---
service = match read(port) {
    digit(22) => chars(SSH) ;
    digit(80) => chars(HTTP) ;
    digit(443) => chars(HTTPS) ;
    digit(3306) => chars(MySQL) ;
    digit(5432) => chars(PostgreSQL) ;
    digit(6379) => chars(Redis) ;
    _ => chars(Unknown) ;
};
```

**Output Result**:
```
service = "SSH"
```

### 3. IP Address Range Matching

**Input Data**:
```
src_ip = "10.0.1.50"
dst_ip = "192.168.1.100"
```

**OML Configuration**:
```oml
name : ip_range_match
---
src_zone = match take(src_ip) {
    in (ip(10.0.0.0), ip(10.255.255.255)) => chars(Internal) ;
    in (ip(172.16.0.0), ip(172.31.255.255)) => chars(Internal) ;
    in (ip(192.168.0.0), ip(192.168.255.255)) => chars(Internal) ;
    _ => chars(External) ;
};

dst_zone = match take(dst_ip) {
    ip(192.168.1.100) => chars(Server-1) ;
    ip(192.168.1.101) => chars(Server-2) ;
    _ => chars(Other) ;
};
```

**Output Result**:
```
src_zone = "Internal"
dst_zone = "Server-1"
```

### 4. Multi-Condition Combined Matching

**Input Data**:
```
protocol = "tcp"
status = "200"
size = "1024"
```

**OML Configuration**:
```oml
name : multi_condition_match
---
traffic_type = match (read(protocol), read(status), read(size)) {
    (chars(tcp), digit(200), in (digit(0), digit(1024))) => chars(Small-TCP-Success) ;
    (chars(tcp), digit(200), digit(_)) => chars(Large-TCP-Success) ;
    (chars(tcp), digit(_), digit(_)) => chars(TCP-Other) ;
    (chars(udp), digit(_), digit(_)) => chars(UDP-All) ;
    _ => chars(Other) ;
};
```

**Output Result**:
```
traffic_type = "Small-TCP-Success"
```

## Array Operations Examples

### 1. Collecting Fields by Prefix

**Input Data**:
```
cpu_user = "45"
cpu_system = "15"
cpu_idle = "40"
memory_used = "2048"
memory_free = "4096"
disk_used = "102400"
disk_free = "204800"
```

**OML Configuration**:
```oml
name : collect_by_prefix
---
# Collect all CPU-related fields
cpu_metrics = collect read(keys:[cpu_*]) ;
# Collect all memory-related fields
memory_metrics = collect read(keys:[memory_*]) ;
# Collect all disk-related fields
disk_metrics = collect read(keys:[disk_*]) ;
```

**Output Result**:
```
cpu_metrics = [45, 15, 40]
memory_metrics = [2048, 4096]
disk_metrics = [102400, 204800]
```

### 2. Multi-Field Collection

**Input Data**:
```
port_http = "80"
port_https = "443"
port_ssh = "22"
```

**OML Configuration**:
```oml
name : array_collect
---
# Collect multiple port fields into array
all_ports = collect read(keys:[port_http, port_https, port_ssh]) ;
# Convert to JSON
ports_json = pipe read(all_ports) | to_json ;
```

**Output Result**:
```
all_ports = ["80", "443", "22"]
ports_json = "[\"80\",\"443\",\"22\"]"
```

## Object Aggregation Examples

### 1. System Metrics Aggregation

**Input Data**:
```
hostname = "web-server-01"
cpu_usage = "75.5"
memory_usage = "60.2"
disk_usage = "45.8"
network_in = "1024000"
network_out = "512000"
```

**OML Configuration**:
```oml
name : system_metrics
---
system_info = object {
    host : chars = read(hostname) ;
    cpu : float = read() ;
    memory : float = read() ;
    disk : float = read() ;
} ;

network_stats = object {
    host : chars = read(hostname) ;
    bytes_in : digit = read() ;
    bytes_out : digit = read() ;
} ;
```

**Output Result**:
```json
{
    "system_info": {
        "host": "web-server-01",
        "cpu": 75.5,
        "memory": 60.2,
        "disk": 45.8
    },
    "network_stats": {
        "host": "web-server-01",
        "bytes_in": 1024000,
        "bytes_out": 512000
    }
}
```

### 2. Nested Object Creation

**Input Data**:
```
app_name = "myapp"
version = "1.2.3"
env = "production"
region = "us-west-2"
az = "us-west-2a"
instance_id = "i-1234567890abcdef0"
```

**OML Configuration**:
```oml
name : nested_object
---
deployment = object {
    application : object {
        name : chars = read() ;
        version : chars = read() ;
        environment : chars = read() ;
    } ;

    infrastructure : object {
        region : chars = read() ;
        availability_zone : chars = read() ;
        instance : object {
            id : chars = read() ;
            state : chars(running) ;
        } ;
    } ;
} ;
```

**Output Result**:
```json
{
    "deployment": {
        "application": {
            "name": "myapp",
            "version": "1.2.3",
            "environment": "production"
        },
        "infrastructure": {
            "region": "us-west-2",
            "availability_zone": "us-west-2a",
            "instance": {
                "id": "i-1234567890abcdef0",
                "state": "running"
            }
        }
    }
}
```

## Wildcard Pattern Examples

### 1. Batch Processing Alert Fields

**Input Data**:
```
alert_cpu_high = "CPU usage above 80%"
alert_memory_low = "Memory below 10%"
alert_disk_full = "Disk usage above 95%"
alert_network_error = "Network connection failed"
normal_field = "This is not an alert"
```

**OML Configuration**:
```oml
name : batch_alerts
---
# All fields starting with alert_
aler* : auto = take() ;

# Keep other fields
normal_field = take() ;
```

**Output Result**:
```
alert_cpu_high = "CPU usage above 80%"
alert_memory_low = "Memory below 10%"
alert_disk_full = "Disk usage above 95%"
alert_network_error = "Network connection failed"
normal_field = "This is not an alert"
```

### 2. Collecting by Path Pattern

**Input Data**:
```
process[0]/name = "chrome"
process[0]/pid = "1001"
process[0]/cpu = "15.5"
process[1]/name = "firefox"
process[1]/pid = "1002"
process[1]/cpu = "8.2"
process[2]/name = "explorer"
process[2]/pid = "1003"
process[2]/cpu = "5.0"
```

**OML Configuration**:
```oml
name : path_pattern
---
# Collect all process names
process_names = collect read(keys:[process[*]/name]) ;
# Collect all process PIDs
process_pids = collect read(keys:[process[*]/pid]) ;
# Collect all process CPU usage
process_cpus = collect read(keys:[process[*]/cpu]) ;
```

**Output Result**:
```
process_names = ["chrome", "firefox", "explorer"]
process_pids = [1001, 1002, 1003]
process_cpus = [15.5, 8.2, 5.0]
```

## SQL Query Examples

### 1. User Information Enrichment

**Input Data**:
```
user_id = "1001"
```

**Database Table (users)**:
| id | name | email | department |
|----|------|-------|------------|
| 1001 | John | john@example.com | R&D |
| 1002 | Jane | jane@example.com | Product |

**OML Configuration**:
```oml
name : user_enrichment
---
user_name, user_email, user_dept =
    select name, email, department
    from users
    where id = read(user_id) ;
```

**Output Result**:
```
user_name = "John"
user_email = "john@example.com"
user_dept = "R&D"
```

### 2. IP Geolocation Query

**Input Data**:
```
src_ip = "203.0.113.1"
dst_ip = "198.51.100.1"
```

**Database Table (ip_geo)**:
| ip_start | ip_end | country | city | isp |
|----------|--------|---------|------|-----|
| 203.0.113.0 | 203.0.113.255 | US | Los Angeles | ISP1 |
| 198.51.100.0 | 198.51.100.255 | CA | Toronto | ISP2 |

**OML Configuration**:
```oml
name : ip_geo_enrichment
---
# Convert IP to integer for comparison
src_country, src_city =
    select country, city
    from ip_geo
    where ip_start_int <= ip4_int(read(src_ip))
      and ip_end_int   >= ip4_int(read(src_ip)) ;

dst_country, dst_city =
    select country, city
    from ip_geo
    where ip_start_int <= ip4_int(read(dst_ip))
      and ip_end_int   >= ip4_int(read(dst_ip)) ;
```

**Output Result**:
```
src_country = "US"
src_city = "Los Angeles"
dst_country = "CA"
dst_city = "Toronto"
```

### 3. Multi-Table Join Query

**Input Data**:
```
order_id = "ORD-2024-001"
```

**Database Tables**:
- orders: | id | user_id | amount | status |
- users: | id | name | level |
- user_levels: | level | discount |

**OML Configuration**:
```oml
name : order_details
---
# Get order information
user_id, order_amount, order_status =
    select user_id, amount, status
    from orders
    where id = read(order_id) ;

# Get user information
user_name, user_level =
    select name, level
    from users
    where id = read(user_id) ;

# Get discount information
discount =
    select discount
    from user_levels
    where level = read(user_level) ;
```

**Output Result**:
```
user_id = "U1001"
order_amount = "199.99"
order_status = "completed"
user_name = "Mike"
user_level = "VIP"
discount = "0.9"
```

## Advanced Pipeline Operations

### 1. JSON Data Processing

**Input Data**:
```
json_data = '{"user":{"id":123,"name":"John","profile":{"age":30,"city":"Beijing"}},"orders":[{"id":"ORD001","amount":100},{"id":"ORD002","amount":200}]}'
```

**OML Configuration**:
```oml
name : json_processing
---
# Extract nested JSON values
user_id = pipe take(json_data) | sxf_get(user.id) ;
user_name = pipe take(json_data) | sxf_get(user.name) ;
user_age = pipe take(json_data) | sxf_get(user.profile.age) ;
user_city = pipe take(json_data) | sxf_get(user.profile.city) ;

# Extract first element of orders array
first_order_id = pipe take(json_data) | sxf_get(orders[0].id) ;
first_order_amount = pipe take(json_data) | sxf_get(orders[0].amount) ;
```

**Output Result**:
```
user_id = "123"
user_name = "John"
user_age = "30"
user_city = "Beijing"
first_order_id = "ORD001"
first_order_amount = "100"
```


### 3. IP Address Operations

**Input Data**:
```
src_ip = "192.168.1.100"
dst_ip = "10.0.0.50"
```

**OML Configuration**:
```oml
name : ip_operations
---
# IP to integer
src_ip_int = pipe read(src_ip) | ip4_to_int ;
dst_ip_int = pipe read(dst_ip) | ip4_to_int ;

# Check if in specific subnet
is_private = match (take(src_ip)) {
    in (ip(10.0.0.0), ip(10.255.255.255)) => chars(True) ;
    in (ip(172.16.0.0), ip(172.31.255.255)) => chars(True) ;
    in (ip(192.168.0.0), ip(192.168.255.255)) => chars(True) ;
    _ => chars(False) ;
} ;
```

**Output Result**:
```
src_ip_int = 3232235876
dst_ip_int = 167772160
is_private = "True"
```

## Real-World Cases

### Case 1: Web Access Log Analysis

**Input Data**:
```
timestamp = "15/Jan/2024:14:30:00 +0800"
src_ip = "203.0.113.1"
method = "GET"
url = "/api/users?page=1&limit=10"
status = "200"
response_size = "1234"
user_agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
referer = "https://example.com/"
```

**OML Configuration**:
```oml
name : web_access_analysis
---
# Basic field processing
event_time = pipe read(timestamp) | Time::to_ts_zone(0, ss) ;
source_ip = take(src_ip) ;
http_method = read(method) ;
request_uri = read(url) ;
response_code = read(status) ;
size = read(response_size) ;

# URL parsing
host = pipe read(request_uri) | url(host) ;
path = pipe read(request_uri) | url(path) ;
query = pipe read(request_uri) | url(params) ;

# Status code classification
status_category = match read(response_code) {
    in (digit(200), digit(299)) => chars(Success) ;
    in (digit(300), digit(399)) => chars(Redirect) ;
    in (digit(400), digit(499)) => chars(Client_Error) ;
    in (digit(500), digit(599)) => chars(Server_Error) ;
    _ => chars(Unknown) ;
} ;

# Aggregated output
access_log = object {
    time : digit = read(event_time) ;
    client : object {
        ip : ip = read(source_ip) ;
        agent : chars = read(user_agent) ;
    } ;
    request : object {
        method : chars = read(http_method) ;
        host : chars = read(host) ;
        path : chars = read(path) ;
        query : chars = read(query) ;
    } ;
    response : object {
        code : digit = read(response_code) ;
        category : chars = read(status_category) ;
        size : digit = read(size) ;
    } ;
    referer : chars = read(referer) ;
} ;
```

**Output Result**:
```json
{
    "access_log": {
        "time": 1705318200,
        "client": {
            "ip": "203.0.113.1",
            "agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        },
        "request": {
            "method": "GET",
            "host": "",
            "path": "/api/users",
            "query": "page=1&limit=10"
        },
        "response": {
            "code": 200,
            "category": "Success",
            "size": 1234
        },
        "referer": "https://example.com/"
    }
}
```

### Case 2: System Monitoring Data Processing

**Input Data**:
```
hostname = "prod-web-01"
timestamp = "2024-01-15 14:30:00"
cpu_user = "65.5"
cpu_system = "15.2"
cpu_idle = "19.3"
mem_total = "8192"
mem_used = "6144"
mem_free = "2048"
disk_read = "1048576"
disk_write = "524288"
net_in = "10485760"
net_out = "5242880"
load_1m = "2.5"
load_5m = "2.1"
load_15m = "1.8"
```

**OML Configuration**:
```oml
name : system_monitoring
---
# Time processing
event_ts = pipe read(timestamp) | Time::to_ts_zone(8, ss) ;

# Alert evaluation (based on CPU user usage)
cpu_alert = match read(cpu_user) {
    in (digit(0), digit(60)) => chars(Normal) ;
    in (digit(60), digit(80)) => chars(Warning) ;
    _ => chars(Critical) ;
} ;

# Alert evaluation (based on memory usage)
mem_alert = match read(mem_used) {
    in (digit(0), digit(6000)) => chars(Normal) ;
    in (digit(6000), digit(7000)) => chars(Warning) ;
    _ => chars(Critical) ;
} ;

# Final output
metrics = object {
    host : object {
        name : chars = read(hostname) ;
        timestamp : digit = read(event_ts) ;
    } ;

    cpu : object {
        user : float = read(cpu_user) ;
        system : float = read(cpu_system) ;
        idle : float = read(cpu_idle) ;
        alert : chars = read(cpu_alert) ;
    } ;

    memory : object {
        total : digit = read(mem_total) ;
        used : digit = read(mem_used) ;
        free : digit = read(mem_free) ;
        alert : chars = read(mem_alert) ;
    } ;

    disk : object {
        read_bytes : digit = read(disk_read) ;
        write_bytes : digit = read(disk_write) ;
    } ;

    network : object {
        in_bytes : digit = read(net_in) ;
        out_bytes : digit = read(net_out) ;
    } ;

    load : object {
        avg_1m : float = read(load_1m) ;
        avg_5m : float = read(load_5m) ;
        avg_15m : float = read(load_15m) ;
    } ;
} ;
```

**Output Result**:
```json
{
    "metrics": {
        "host": {
            "name": "prod-web-01",
            "timestamp": 1705285800
        },
        "cpu": {
            "user": 65.5,
            "system": 15.2,
            "idle": 19.3,
            "alert": "Warning"
        },
        "memory": {
            "total": 8192,
            "used": 6144,
            "free": 2048,
            "alert": "Warning"
        },
        "disk": {
            "read_bytes": 1048576,
            "write_bytes": 524288
        },
        "network": {
            "in_bytes": 10485760,
            "out_bytes": 5242880
        },
        "load": {
            "avg_1m": 2.5,
            "avg_5m": 2.1,
            "avg_15m": 1.8
        }
    }
}
```

## Comprehensive Examples

### Example 1: Complete Log Processing Pipeline

**Input Data**:
```
# Basic log fields
log_time = "2024-01-15T14:30:00Z"
src_ip = "203.0.113.100"
dst_ip = "192.168.1.10"
protocol = "TCP"
sport = "54321"
dport = "443"
action = "allow"
rule_name = "ALLOW-HTTPS-OUT"

# Application layer information
app_name = "myapp"
app_version = "1.2.3"
user_id = "user1001"
session_id = "sess_abc123"

# Load information
cpu_usage = "45.2"
memory_usage = "60.8"
```

**OML Configuration**:
```oml
name : complete_log_processing
---
# === Time and Basic Information ===
event_time = pipe read(log_time) | Time::to_ts_zone(0, ss) ;
event_date = Now::date() ;

# === Network Information Processing ===
# IP address conversion
src_ip_int = pipe read(src_ip) | ip4_to_int ;
dst_ip_int = pipe read(dst_ip) | ip4_to_int ;

# Port processing
src_port : digit = read() ;
dst_port : digit = read() ;

# Service identification
service = match read(dst_port) {
    digit(22) => chars(SSH) ;
    digit(80) => chars(HTTP) ;
    digit(443) => chars(HTTPS) ;
    digit(3306) => chars(MySQL) ;
    digit(5432) => chars(PostgreSQL) ;
    _ => chars(Unknown) ;
} ;

# === SQL Enrichment Queries ===
# Query source IP geolocation
src_country, src_city, src_isp =
    select country, city, isp
    from ip_geo
    where ip_start_int <= read(src_ip_int)
      and ip_end_int   >= read(src_ip_int) ;

# Query destination asset information
dst_asset, dst_owner =
    select asset_name, owner
    from assets
    where ip = read(dst_ip) ;

# Query user information
user_name, user_role, user_dept =
    select name, role, department
    from users
    where id = read(user_id) ;

# === Risk Assessment ===
# Determine if internal communication
is_internal = match (take(src_ip), take(dst_ip)) {
    (in (ip(10.0.0.0), ip(10.255.255.255)), ip(_)) => chars(True) ;
    (in (ip(172.16.0.0), ip(172.31.255.255)), ip(_)) => chars(True) ;
    (in (ip(192.168.0.0), ip(192.168.255.255)), ip(_)) => chars(True) ;
    _ => chars(False) ;
} ;

# Risk level assessment
risk_level = match (read(is_internal), read(action), read(dst_port)) {
    (chars(False), chars(deny), digit(_)) => chars(Low) ;
    (chars(True), chars(deny), digit(_)) => chars(Low) ;
    (chars(False), chars(allow), in (digit(22), digit(3389))) => chars(Medium) ;
    (chars(False), chars(allow), digit(443)) => chars(Low) ;
    (chars(False), chars(allow), digit(_)) => chars(High) ;
    _ => chars(Medium) ;
} ;

# === Formatted Output ===
# Create connection identifier
connection_id = fmt("{}:{}->{}:{}", @src_ip, read(src_port), @dst_ip, read(dst_port)) ;

# === Final Output Structure ===
network_event = object {
    # Event basic information
    event : object {
        timestamp : digit = read(event_time) ;
        date : chars = read(event_date) ;
        id : chars = read(connection_id) ;
        action : chars = read() ;
        rule : chars = read(rule_name) ;
        risk : chars = read(risk_level) ;
    } ;

    # Network layer information
    network : object {
        protocol : chars = read(protocol) ;
        source : object {
            ip : ip = read(src_ip) ;
            port : digit = read(src_port) ;
            geo : object {
                country : chars = read(src_country) ;
                city : chars = read(src_city) ;
                isp : chars = read(src_isp) ;
            } ;
        } ;
        destination : object {
            ip : ip = read(dst_ip) ;
            port : digit = read(dst_port) ;
            service : chars = read(service) ;
            asset : chars = read(dst_asset) ;
            owner : chars = read(dst_owner) ;
        } ;
    } ;

    # Application layer information
    application : object {
        name : chars = read(app_name) ;
        version : chars = read(app_version) ;
        session : chars = read(session_id) ;
        user : object {
            id : chars = read(user_id) ;
            name : chars = read(user_name) ;
            role : chars = read(user_role) ;
            department : chars = read(user_dept) ;
        } ;
    } ;

    # System information
    system : object {
        cpu : float = read() ;
        memory : float = read() ;
    } ;

    # Processing tags
    tags : array = collect read(keys:[is_internal]) ;
} ;
```

**Output Result**:
```json
{
    "network_event": {
        "event": {
            "timestamp": 1705318200,
            "date": "2024-01-15",
            "id": "203.0.113.100:54321->192.168.1.10:443",
            "action": "allow",
            "rule": "ALLOW-HTTPS-OUT",
            "risk": "Low"
        },
        "network": {
            "protocol": "TCP",
            "source": {
                "ip": "203.0.113.100",
                "port": 54321,
                "geo": {
                    "country": "US",
                    "city": "Los Angeles",
                    "isp": "ISP1"
                }
            },
            "destination": {
                "ip": "192.168.1.10",
                "port": 443,
                "service": "HTTPS",
                "asset": "WEB-SRV-01",
                "owner": "IT-Dept"
            }
        },
        "application": {
            "name": "myapp",
            "version": "1.2.3",
            "session": "sess_abc123",
            "user": {
                "id": "user1001",
                "name": "John",
                "role": "Developer",
                "department": "R&D"
            }
        },
        "system": {
            "cpu": 45.2,
            "memory": 60.8
        },
        "tags": ["False"]
    }
}
```

## Summary

Through the rich examples above, you can see the powerful capabilities of OML:

1. **Flexible data reading**: Supports multiple reading methods and parameters
2. **Strong type system**: Automatic type inference and explicit type conversion
3. **Rich pipeline operations**: Supports various data processing and transformations
4. **Intelligent pattern matching**: Flexible branch processing based on conditions
5. **Convenient aggregation operations**: Creation and manipulation of arrays and objects
6. **Wildcard support**: Batch processing and pattern matching
7. **SQL integration**: Directly query databases for data enrichment
8. **Real-world cases**: Complete examples close to actual application scenarios

It is recommended to start practicing with basic examples, gradually master advanced features, and finally improve comprehensive application skills through real-world cases.
