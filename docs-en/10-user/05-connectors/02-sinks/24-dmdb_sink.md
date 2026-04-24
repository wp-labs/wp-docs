# DMDB Sink Usage and Configuration Guide

## 1. Prerequisites

Before using the `dmdb` sink, make sure the ODBC driver is installed and the database connection has been verified.

### 1.1 Prepare the ODBC Environment

- The host machine must have the DM ODBC driver installed.

#### Install System Dependencies (Ubuntu Example)

```bash
apt-get update
apt-get install -y unixodbc unixodbc-dev odbcinst
```

Run the following commands to verify the installation:

```bash
which isql
isql --version
odbcinst -j
```

Expected output example:

```text
unixODBC 2.x.x
DRIVERS............: /etc/odbcinst.ini
SYSTEM DATA SOURCES: /etc/odbc.ini
...
```

#### Install the DM ODBC Driver

- Windows version: <https://dn.navicat.com/drivers/dameng_odbc_win.zip>
- Linux version: <https://dn.navicat.com/drivers/dameng_odbc_linux.tar.gz>

The following example assumes the archive is downloaded to `/root`:

```bash
cd /root
tar -xvf dameng_odbc_linux.tar.gz
cd dameng_odbc_linux
ls
```

Expected output example:

```text
bin  install_odbc.sh  libcrypto.so  libdmdpi.so  libdmfldr.so  libdodbc.a  libdodbc.so  libssl.so
```

#### Configure the Dynamic Library Path

```bash
echo "/root/dameng_odbc_linux" > /etc/ld.so.conf.d/dameng.conf
ldconfig
```

Run the following command to verify that the dynamic library is available:

```bash
ldconfig -p | grep libdodbc
```

Expected output example:

```text
libdodbc.so.2 => /root/dameng_odbc_linux/libdodbc.so
```

### 1.2 Register the ODBC Driver

Edit `/etc/odbcinst.ini`. If the file already exists, append the following content. If it does not exist, create it and write the content below:

```ini
[DM8 ODBC DRIVER]
Description = DM8 ODBC DRIVER for DM8
Driver = /root/dameng_odbc_linux/libdodbc.so
FileUsage = 1
```

After the configuration is complete, run the following commands to verify that the driver has been registered successfully:

```bash
odbcinst -q -d
odbcinst -q -d -n "DM8 ODBC DRIVER"
```

Expected output example:

```text
[DM8 ODBC DRIVER]
```

You should also see driver details similar to the following:

```ini
[DM8 ODBC DRIVER]
Description=DM8 ODBC DRIVER for DM8
Driver=/root/dameng_odbc_linux/libdodbc.so
FileUsage=1
```

### 1.3 Verify the Database Connection

Run the following command on the machine where `wparse` is running, and replace the database host, port, username, and password with actual values:

```bash
isql -v -k "Driver={DM8 ODBC DRIVER};Server=localhost;Port=5236;UID=SYSDBA;PWD=password"
```

### 1.4 Prepare the Target Table

- The target table must already exist.
- `table` and `columns` must match the actual target table schema, including column names and column types.

## 2. Connection Modes

### 2.1 Priority

The current implementation selects the connection mode with the following priority:

```text
connection_string > endpoint > dsn
```

This means:

- If `connection_string` is configured, it is always used first. Even if `dsn`, `endpoint`, `driver`, `username`, and `password` are also present, they will not participate in connection setup.
- If `connection_string` is not configured but `endpoint` is configured, the sink automatically builds an ODBC connection string from `endpoint + driver + username + password`.
- `dsn` mode is used only when neither of the first two options is configured. In that case, the sink connects with `dsn + username + password`.

### 2.2 `connection_string` Mode

This mode is suitable when you already have a complete ODBC connection string.

- Required parameters: `connection_string`, `table`, `columns`
- Optional parameters: `schema`, `batch_size`, `connect_timeout_secs`, `query_timeout_secs`
- Not additionally required: `dsn`, `endpoint`, `driver`, `username`, `password`

Example:

```toml
[[sinks]]
name = "dmdb_events"
kind = "dmdb"

[sinks.params]
connection_string = "Driver={DM8 ODBC DRIVER};SERVER=127.0.0.1;TCP_PORT=5236;UID=SYSDBA;PWD=${DMDB_PASSWORD};"
schema = "WP_DATA"
table = "EVENTS"
columns = ["event_id", "event_time", "source", "payload"]
batch_size = 2000
query_timeout_secs = 15
```

### 2.3 `endpoint` Mode

This mode is suitable when you do not want to preconfigure a DSN and prefer to connect directly with an address.

- Required parameters: `endpoint`, `driver`, `username`, `password`, `table`, `columns`
- Optional parameters: `schema`, `batch_size`, `connect_timeout_secs`, `query_timeout_secs`
- `endpoint` must be in `host:port` format, and `port` must be parseable as a valid `u16`

Example:

```toml
[[sinks]]
name = "dmdb_events"
kind = "dmdb"

[sinks.params]
endpoint = "127.0.0.1:5236"
driver = "DM8 ODBC DRIVER"
username = "SYSDBA"
password = "${DMDB_PASSWORD}"
schema = "WP_DATA"
table = "EVENTS"
columns = ["event_id", "event_time", "source", "payload"]
batch_size = 2000
connect_timeout_secs = 8
query_timeout_secs = 15
```

### 2.4 `dsn` Mode

This mode is suitable when the host machine has already configured an ODBC DSN and neither `connection_string` nor `endpoint` is provided.

- Required parameters: `dsn`, `username`, `password`, `table`, `columns`
- Optional parameters: `schema`, `batch_size`, `connect_timeout_secs`, `query_timeout_secs`
- Not additionally required: `endpoint`, `driver`

Example:

```toml
[[sinks]]
name = "dmdb_events"
kind = "dmdb"

[sinks.params]
dsn = "DM8_LOCAL"
username = "SYSDBA"
password = "${DMDB_PASSWORD}"
schema = "WP_DATA"
table = "EVENTS"
columns = ["event_id", "event_time", "source", "payload"]
batch_size = 2000
connect_timeout_secs = 8
query_timeout_secs = 15
```

## 3. Parameter Reference

| Parameter | Type | Required | Description |
| --- | --- | --- | --- |
| `connection_string` | `string` | Required in `connection_string` mode | A complete ODBC connection string. This has the highest priority. |
| `endpoint` | `string` | Required in `endpoint` mode | The DM database address. The format must be `host:port`; it has higher priority than `dsn`. |
| `dsn` | `string` | Required in `dsn` mode | The ODBC data source name. It is used only when neither `connection_string` nor `endpoint` is configured. |
| `driver` | `string` | Required in `endpoint` mode | The DM ODBC driver name, for example `DM8 ODBC DRIVER`. |
| `username` | `string` | Required in `dsn` and `endpoint` modes | The DM username. It does not need to be provided separately in `connection_string` mode. |
| `password` | `string` | Required in `dsn` and `endpoint` modes | The DM password. It does not need to be provided separately in `connection_string` mode. |
| `schema` | `string` | No | Used to build the qualified target table name. In `endpoint` mode, it is also appended to the generated connection string. |
| `table` | `string` | Yes | The target table name. It cannot be empty. |
| `columns` | `string[]` | Yes | The list of target columns. It must be a string array, and each item must be a non-empty string. |
| `batch_size` | `integer` | No | The maximum number of records written in a single SQL statement. It must be greater than `0`. If not configured, the sink falls back to `1024`. |
| `connect_timeout_secs` | `integer` | No | The ODBC login timeout in seconds. It must be greater than `0`. When configured, it is passed to `ConnectionOptions.login_timeout_sec`; otherwise, it is not explicitly set. |
| `query_timeout_secs` | `integer` | No | The execution timeout in seconds for each SQL batch. It must be greater than `0`. If not configured, it is not explicitly set. |
