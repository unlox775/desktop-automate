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
pip install -r requirements.txt  # If you have a requirements file
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

### Basic Usage

```bash
./cron_run_w_log.sh /path/to/your/script.py [arg1 arg2 ...]
```

### Examples

1. **Run a script with arguments**:

```bash
./cron_run_w_log.sh feed_mailer/send_new_feeds_email.py check --feed https://example.com/feed.xml
```

2. **Run with custom Python interpreter**:

```bash
VENV_PYTHON=/custom/path/to/python ./cron_run_w_log.sh your_script.py
```

3. **Use a custom secrets file**:

```bash
SECRETS_FILE=/path/to/your/secrets.sh ./cron_run_w_log.sh your_script.py
```

4. **Customize log location**:

```bash
LOG=/var/log/my_scripts.log ./cron_run_w_log.sh your_script.py
```

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

## Troubleshooting

### Script fails with "Python executable not found"

Ensure the virtual environment exists and is correctly referenced:

```bash
# Check if the Python executable exists
ls -l /path/to/your/venv/bin/python3

# If not, create the virtual environment
python3 -m venv /path/to/your/venv
```

### Logs not being written

Check file permissions for the log file and its directory:

```bash
# Create log directory if it doesn't exist
mkdir -p $(dirname $LOG)

# Ensure proper permissions
touch $LOG
chmod 644 $LOG
```

### Environment variables not loading

If your script isn't receiving environment variables from your secrets file, ensure:

1. The secrets file exists and is properly formatted
2. The script has permission to read the file
3. Variables are exported in the secrets file:

```bash
# In your secrets file:
export MY_VARIABLE="value"
```

## Advanced Usage

### Using with log_prefix Tool

If you have the `log_prefix` tool installed, the script will automatically use it for better log formatting:

```bash
# Install log_prefix (example for macOS with Homebrew)
brew install log_prefix

# Or specify a custom path
LOG_PREFIX=/usr/local/bin/log_prefix ./cron_run_w_log.sh your_script.py
```

### Working with Multiple Virtual Environments

If you have multiple projects with different virtual environments:

```bash
# For project A
VENV_PYTHON=/path/to/projA/venv/bin/python3 ./cron_run_w_log.sh projA/script.py

# For project B
VENV_PYTHON=/path/to/projB/venv/bin/python3 ./cron_run_w_log.sh projB/script.py
```

## License

This script is released under the same license as the desktop-automate project.