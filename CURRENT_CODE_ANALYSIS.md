# Current Code Overview

This document provides an overview of the existing Zabbix server source tree for new contributors.  It summarizes the main components and references relevant code sections.

## Project Structure

- **Build System:** Autotools is used (`configure.ac`, `bootstrap.sh`, multiple `Makefile.am` files).  Run `./bootstrap.sh` then `./configure` and `make` to compile the C sources.
- **Top-level Directories:**
  - `src/zabbix_server/` – core server implementation in C.
  - `src/libs/` – internal libraries shared across components (e.g., `zbxalgo`, `zbxdb`, `zbxlog`).
  - `src/zabbix_proxy/`, `src/zabbix_agent/` – proxy and agent implementations.
  - `database/` – SQL schema files.
  - `tests/` – Perl-based test runner (`tests_run.pl`).
  - `misc/` – helper scripts such as `images/png_to_sql.sh`.

## Server Entry Point

The main process lives in `src/zabbix_server/server.c`.  The `main()` function starts around line 1273 and performs library initialization followed by command line parsing:

```c
int     main(int argc, char **argv)
{
    static zbx_config_icmpping_t    config_icmpping = {
        get_zbx_config_source_ip,
        get_zbx_config_fping_location,
        get_zbx_config_fping6_location,
        get_zbx_config_tmpdir,
        get_zbx_progname};
    ZBX_TASK_EX                     t = {ZBX_TASK_START, 0, 0, NULL};
    char                            ch;
    int                             opt_c = 0, opt_r = 0, opt_t = 0, opt_f = 0;
    /* ... initialization omitted ... */
    /* parse the command-line */
    while ((char)EOF != (ch = (char)zbx_getopt_long(argc, argv, shortopts,
                        longopts, NULL, &zbx_optarg, &zbx_optind)))
    {
        switch (ch)
        {
            case 'c':
                opt_c++;
                if (NULL == config_file)
                    config_file = zbx_strdup(config_file, zbx_optarg);
                break;
            case 'R':
                opt_r++;
                t.opts = zbx_strdup(t.opts, zbx_optarg);
                t.task = ZBX_TASK_RUNTIME_CONTROL;
                break;
            case 'T':
                opt_t++;
                t.task = ZBX_TASK_TEST_CONFIG;
                break;
            /* ... other options ... */
        }
    }
```
【F:src/zabbix_server/server.c†L1273-L1352】

After parsing, the code checks for duplicate options and validates parameters:

```c
/* every option may be specified only once */
if (1 < opt_c || 1 < opt_r || 1 < opt_t || 1 < opt_f)
{
    if (1 < opt_c)
        zbx_error("option \"-c\" or \"--config\" specified multiple times");
    if (1 < opt_r)
        zbx_error("option \"-R\" or \"--runtime-control\" specified multiple times");
    if (1 < opt_t)
        zbx_error("option \"-T\" or \"--test-config\" specified multiple times");
    if (1 < opt_f)
        zbx_error("option \"-f\" or \"--foreground\" specified multiple times");
    exit(EXIT_FAILURE);
}

if (0 != opt_t && 0 != opt_r)
{
    zbx_error("option \"-T\" or \"--test-config\" cannot be specified with \"-R\"");
    exit(EXIT_FAILURE);
}
```
【F:src/zabbix_server/server.c†L1355-L1374】

If no configuration file is provided, the default path is used and the configuration is loaded:

```c
if (NULL == config_file)
    config_file = zbx_strdup(NULL, DEFAULT_CONFIG_FILE);

/* required for simple checks */
zbx_init_metrics();
zbx_init_library_cfg(zbx_program_type, config_file);

if (ZBX_TASK_TEST_CONFIG == t.task)
    printf("Validating configuration file \"%s\"\n", config_file);

zbx_load_config(&t);

if (ZBX_TASK_TEST_CONFIG == t.task)
{
    printf("Validation successful\n");
    exit(EXIT_SUCCESS);
}
```
【F:src/zabbix_server/server.c†L1388-L1404】

### Configuration Loading

`zbx_load_config()` builds a large array describing every configuration parameter. An excerpt illustrates the pattern:

```c
static void     zbx_load_config(ZBX_TASK_EX *task)
{
    zbx_cfg_line_t  cfg[] =
    {
        /* PARAMETER,                   VAR,                           TYPE,
                            MANDATORY,              MIN,                   MAX */
        {"StartDBSyncers",              &config_forks[ZBX_PROCESS_TYPE_HISTSYNCER],
                                        ZBX_CFG_TYPE_INT,
                            ZBX_CONF_PARM_OPT,      1,                     100},
        {"StartDiscoverers",            &config_forks[ZBX_PROCESS_TYPE_DISCOVERER],
                                        ZBX_CFG_TYPE_INT,
                            ZBX_CONF_PARM_OPT,      0,                     1000},
        {"StartHTTPPollers",            &config_forks[ZBX_PROCESS_TYPE_HTTPPOLLER],
                                        ZBX_CFG_TYPE_INT,
                            ZBX_CONF_PARM_OPT,      0,                     1000},
        /* many more parameters ... */
        {"DBName",                      &(zbx_db_config->dbname),      ZBX_CFG_TYPE_STRING,
                            ZBX_CONF_PARM_MAND,     0,                     0},
        {"DBUser",                      &(zbx_db_config->dbuser),      ZBX_CFG_TYPE_STRING,
                            ZBX_CONF_PARM_OPT,      0,                     0},
        {"DBPassword",                  &(zbx_db_config->dbpassword),  ZBX_CFG_TYPE_STRING,
                            ZBX_CONF_PARM_OPT,      0,                     0},
        /* ... */
    };
```
【F:src/zabbix_server/server.c†L867-L999】

This array is passed to `zbx_parse_cfg_file()` which populates global variables controlling the server behaviour (number of pollers, database settings, log files, etc.).

## Supporting Libraries

Common functionality is placed under `src/libs/`.  For example, the `zbxalgo` directory contains data structures like heaps and hash maps:

```
src/libs/zbxalgo/
├── algodefs.c
├── binaryheap.c
├── hashmap.c
└── ...
```
【F:src/libs/zbxalgo/Makefile.am†L1-L4】

These libraries are linked into the server during compilation.

## Tests

Automated tests are executed via a Perl script `tests/tests_run.pl`.  It requires several Perl modules as shown at the top of the file:

```perl
use YAML::XS qw(LoadFile Dump);
use Path::Tiny qw(path);
use IPC::Run3 qw(run3);
use Time::HiRes qw(time);
use File::Basename qw(dirname);
use Getopt::Long qw(GetOptions);
```
【F:tests/tests_run.pl†L1-L12】

Missing these modules will cause the tests to fail. Test definitions reside under `tests/` in YAML files.

## Helper Scripts

The script `misc/images/png_to_sql.sh` converts PNG images into SQL inserts.  It contains a TODO noting that directory paths with spaces break the loop:

```bash
# TODO: this loop won't work with directory names, containing spaces
# using 'find' here seems to be a bit excessive for now
for imagefile in $pngdir/*.png; do
    ((imagesdone++))
    imagename="$(basename "${imagefile%.png}")"
    # ...
```
【F:misc/images/png_to_sql.sh†L22-L32】

## Server Modules

The server is composed of many C source files grouped by subsystem.  Examples include:

- `actions/actions.c` – alerting logic
- `autoreg/autoreg_server.c` – auto-registration of agents
- `cachehistory/cachehistory_server.c` – history cache management
- `discovery/discovery_server.c` – network discovery
- `escalator/escalator.c` – event escalation engine
- `poller/checks_internal_server.c` – internal check poller
- `timer/timer.c` – timers and scheduling
- `trapper/trapper_server.c` – incoming data processing

In total there are over fifty `.c` files under `src/zabbix_server/` implementing these subsystems.

## Summary

- **Language:** C (AGPLv3)
- **Build:** Autotools; run `./bootstrap.sh`, `./configure`, and `make`
- **Entry Point:** `src/zabbix_server/server.c` handles initialization and command‑line options
- **Configuration:** Parameters defined in `zbx_load_config()` map directly to variables
- **Tests:** Perl-based runner with additional CPAN dependencies
- **Scripts:** Auxiliary tools in `misc/`, some requiring fixes (e.g., handling spaces in `png_to_sql.sh`)

This overview should help new developers navigate the codebase and understand where major functionality resides.
