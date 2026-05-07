# DMDB Sink

## 1. Prerequisites

Before using the `dmdb` sink, first install the ODBC driver. Then follow the setup and verification steps for either `connection_string` / `endpoint` mode or `dsn` mode, depending on how you plan to connect.

### 1.1 Common Preparation: Install the ODBC Environment and the DM Driver

#### Install System Dependencies (Ubuntu Example)

```bash
apt-get update
apt-get install -y unixodbc unixodbc-dev odbcinst
```

Run the following commands to verify the installation:

```bash
root@ent-rdd-WarpParse-01:~/wp/dameng_odbc_linux# which isql
/usr/bin/isql
root@ent-rdd-WarpParse-01:~/wp/dameng_odbc_linux# isql --version
unixODBC 2.3.12
root@ent-rdd-WarpParse-01:~/wp/dameng_odbc_linux# odbcinst -j
unixODBC 2.3.12
DRIVERS............: /etc/odbcinst.ini
SYSTEM DATA SOURCES: /etc/odbc.ini
FILE DATA SOURCES..: /etc/ODBCDataSources
USER DATA SOURCES..: /root/.odbc.ini
SQLULEN Size.......: 8
SQLLEN Size........: 8
SQLSETPOSIROW Size.: 8
```

#### Install the DM ODBC Driver

- Windows version: <https://dn.navicat.com/drivers/dameng_odbc_win.zip>
- Linux version: <https://dn.navicat.com/drivers/dameng_odbc_linux.tar.gz>

The following example assumes the archive is downloaded to `/root/wp`:

#### Configure the Dynamic Library Path

```bash
echo "/root/wp/dameng_odbc_linux/libdodbc.so" > /etc/ld.so.conf.d/dameng.conf
ldconfig
```

Run the following command to verify that the dynamic library has been loaded successfully:

```bash
root@ent-rdd-WarpParse-01:~/wp/dameng_odbc_linux# ldconfig -p | grep libdodbc
        libdodbc.so (libc6,x86-64) => /root/wp/dameng_odbc_linux/libdodbc.so
```

### 1.2 Common Preparation: Register the ODBC Driver

Edit `/etc/odbcinst.ini`. If the file already exists, append the following content. If it does not exist, create it and write the content below:

```ini
[DM8 ODBC DRIVER]
Description = DM8 ODBC DRIVER for DM8
Driver = /root/wp/dameng_odbc_linux/libdodbc.so
FileUsage = 1
```

After the configuration is complete, run the following command to verify that the driver registration output is correct:

```bash
root@ent-rdd-WarpParse-01:~/wp/dameng_odbc_linux# odbcinst -q -d -n "DM8 ODBC DRIVER"
[DM8 ODBC DRIVER]
Description=ODBC DRIVER FOR DM8
Driver=/root/wp/dameng_odbc_linux/libdodbc.so
Setup=/root/wp/dameng_odbc_linux/libdodbc.so
```

After these steps are complete, the host machine is ready to use the DM ODBC driver. Next, continue with one of the following paths based on your connection mode.

### 1.3 `connection_string` / `endpoint` Mode Setup

These two modes do not depend on a DSN entry in `/etc/odbc.ini`. They only require the ODBC driver to be installed and registered successfully.

- `connection_string` mode: provide the full ODBC connection string directly.
- `endpoint` mode: build the connection string automatically from `endpoint + driver + username + password`.

You can run the following command on the machine where `wparse` is running to verify that the driver and direct connection parameters are valid. Replace the host, port, username, and password with actual values:

```bash
root@ent-rdd-WarpParse-01:~/wp/dameng_odbc_linux# isql -v -k "Driver={DM8 ODBC DRIVER};Server=127.0.0.1;Port=5236;UID=SYSDBA;PWD=SYSDBA"
+---------------------------------------+
| Connected!                            |
|                                       |
| sql-statement                         |
| help [tablename]                      |
| echo [string]                         |
| quit                                  |
|                                       |
+---------------------------------------+
SQL>
```

If the command above connects successfully, the host-side preparation required for `connection_string` or `endpoint` mode is complete.

### 1.4 `dsn` Mode Setup

In addition to installing and registering the ODBC driver, `dsn` mode also requires a data source name to be configured in `/etc/odbc.ini`. That name must match the `dsn` parameter in the sink configuration.

For example, you can add a DM data source to `/etc/odbc.ini`:

```ini
[DM_DSN]
Description = DM8 Database
Driver = /root/wp/dameng_odbc_linux/libdodbc.so
Server = 159.75.175.212
Port = 5236
User = SYSDBA
Password = <replace with the actual password>
```

After the configuration is complete, run the following commands to verify that the DSN is available. Replace the host, username, and password with actual values:

```bash
root@ent-rdd-WarpParse-01:~/wp/dameng_odbc_linux# cat /etc/odbc.ini
[DM_DSN]                          ; DSN name
Description = DM8 Database
Driver = /root/wp/dameng_odbc_linux/libdodbc.so
Server = 127.0.0.1
Port = 5236
User = SYSDBA
Password = Dayu@1234
root@ent-rdd-WarpParse-01:~/wp/dameng_odbc_linux# isql DM_DSN SYSDBA SYSDBA
+---------------------------------------+
| Connected!                            |
|                                       |
| sql-statement                         |
| help [tablename]                      |
| echo [string]                         |
| quit                                  |
|                                       |
+---------------------------------------+
SQL>
```

If the command above connects successfully, the system-level data source for `dsn = "DM_DSN"` has been configured correctly.

### 1.5 Prepare the Target Table

- The target table must already exist.
- `table` and `columns` must match the actual target table schema, including column names and column types.

## 2. Connection Modes

### 2.1 `connection_string` Mode

Suitable when you already have a complete ODBC connection string.

- Required parameters: `connection_string`, `table`, `columns`
- Optional parameters: `schema`, `batch_size`, `connect_timeout_secs`, `query_timeout_secs`
- Not additionally required: `dsn`, `endpoint`, `driver`, `username`, `password`

Example:

```toml
[sink_group]
name = "database"
rule = ["/*"]
parallel = 8
[[sink_group.sinks]]
name = "dmdb_sink"
connect = "dmdb_connect_string"
[sink_group.sinks.params]
connection_string = "Driver={DM8 ODBC DRIVER};SERVER=127.0.0.1;TCP_PORT=5236;UID=SYSDBA;PWD=Dayu@1234;"
table = "nginx_logs"
columns = ["sip", "timestamp", "http/request", "status", "size", "referer", "http/agent"]
batch_size = 2000
query_timeout_secs = 15
```

### 2.2 `endpoint` Mode

Suitable when you do not want to preconfigure a DSN and prefer to connect directly by host and port.

- Required parameters: `endpoint`, `driver`, `username`, `password`, `table`, `columns`
- Optional parameters: `schema`, `batch_size`, `connect_timeout_secs`, `query_timeout_secs`
- `endpoint` must be in `host:port` format, and `port` must be parseable as a valid `u16`

Example:

```toml
[sink_group]
name = "database"
rule = ["/*"]
parallel = 8
[[sink_group.sinks]]
name = "dmdb_sink"
connect = "dmdb_endpoint"
[sink_group.sinks.params]
endpoint = "127.0.0.1:5236"
driver = "DM8 ODBC DRIVER"
username = "SYSDBA"
password = "SYSDBA"
schema = "WP_DATA"
table = "EVENTS"
columns = ["event_id", "event_time", "source", "payload"]
batch_size = 2000
connect_timeout_secs = 8
query_timeout_secs = 15
```

### 2.3 `dsn` Mode

Suitable when the host machine has already configured an ODBC DSN and neither `connection_string` nor `endpoint` is provided.

- Required parameters: `dsn`, `username`, `password`, `table`, `columns`
- Optional parameters: `schema`, `batch_size`, `connect_timeout_secs`, `query_timeout_secs`
- Not additionally required: `endpoint`, `driver`

Example:

```toml
[sink_group]
name = "database"
rule = ["/*"]
parallel = 8
[[sink_group.sinks]]
name = "dmdb_sink"
connect = "dmdb_dsn"
[sink_group.sinks.params]
dsn = "DM_DSN"
username = "SYSDBA"
password = "SYSDBA"
schema = "WP_DATA"
table = "EVENTS"
columns = ["event_id", "event_time", "source", "payload"]
batch_size = 2000
connect_timeout_secs = 8
query_timeout_secs = 15
```

## 3. Parameter Reference

| Parameter | Type | Required | Applicable Modes | Description |
| --- | --- | --- | --- | --- |
| `connection_string` | `string` | Required in `connection_string` mode | All | A complete ODBC connection string. This has the highest priority. |
| `endpoint` | `string` | Required in `endpoint` mode | All | The DM database address. The format must be `host:port`; it has higher priority than `dsn`. |
| `dsn` | `string` | Required in `dsn` mode | All | The ODBC data source name. It is used only when neither `connection_string` nor `endpoint` is configured. |
| `driver` | `string` | Required in `endpoint` mode | All | The DM ODBC driver name, for example `DM8 ODBC DRIVER`. |
| `username` | `string` | Required in `dsn` and `endpoint` modes | All | The DM username. It does not need to be provided separately in `connection_string` mode. |
| `password` | `string` | Required in `dsn` and `endpoint` modes | All | The DM password. It does not need to be provided separately in `connection_string` mode. |
| `schema` | `string` | No | All | Used to build the qualified target table name. In `endpoint` mode, it is also appended to the generated connection string. |
| `table` | `string` | Yes | All | The target table name. It cannot be empty. |
| `columns` | `string[]` | Yes | All | The list of target column names. It must be a string array, and each item must be a non-empty string. |
| `batch_size` | `integer` | No | All | The maximum number of records written in a single SQL statement. It must be greater than `0`. If not configured, the sink falls back to `1024`. |
| `connect_timeout_secs` | `integer` | No | All | The ODBC login timeout in seconds. It must be greater than `0`. When configured, it is passed to `ConnectionOptions.login_timeout_sec`; otherwise, it is not explicitly set. |
| `query_timeout_secs` | `integer` | No | All | The execution timeout in seconds for each SQL batch. It must be greater than `0`. If not configured, it is not explicitly set. |
