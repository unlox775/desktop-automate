# Cron Runner with Logging

## Overview

`cron_run_w_log.sh` is a utility script designed to run Python scripts in a virtual environment with proper logging. It's particularly useful for running scheduled tasks via cron jobs, ensuring that output is properly captured and timestamped.

## Features

- Runs Python scripts using a specified virtual environment
- Captures and logs both stdout and stderr
- Adds timestamps and script name prefixes to log entries
- Configurable via environment variables
- Can load environment variables/secrets from a file
- Falls back to simple timestamping if advanced logging tools aren't available

## Installation

1. **Clone the repository** or download the script to your system:

```bash
git clone https://github.com/yourusername/desktop-automate.git
cd desktop-automate
```

2. **Make the script executable**:

```bash
chmod +x cron_run_w_log.sh
```

3. **Set up a virtual environment** (if you haven't already):

```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

The script can be configured using environment variables:

| Environment Variable | Description | Default |
|---------------------|-------------|---------|
| `SECRETS_FILE` | Path to a file containing environment variables/secrets | `$HOME/.secrets/env.sh` |
| `VENV_PYTHON` | Path to Python executable in the virtual environment | `$SCRIPT_DIR/venv/bin/python3` |
| `LOG` | Path to the log file | `$HOME/cron.log` |
| `LOG_PREFIX` | Command to prefix log lines with timestamps | (None) |

## Usage

## Setting Up Cron Jobs

To run your scripts on a schedule, add them to your crontab:

1. **Open your crontab**:

```bash
crontab -e
```

2. **Add cron job entries**:

```
# Environment variables for all jobs
WORKSPACE=/path/to/desktop-automate
LOG=$WORKSPACE/data/cron.log
SECRETS=$HOME/.secrets/env.sh

# Run feed mailer every day at 9 AM
0 9 * * * $WORKSPACE/cron_run_w_log.sh $WORKSPACE/feed_mailer/send_new_feeds_email.py check --feed https://example.com/feed.xml

# Check website uptime every 30 minutes
*/30 * * * * $WORKSPACE/cron_run_w_log.sh $WORKSPACE/uptime_watch/check_url_uptime.py http://example.com
```

## Log Format

When the script runs, it logs output in the following format:

```
[YYYY-MM-DD HH:MM:SS] script_name | Output from the script
```