# vsce_tui

A TUI tool for managing VS Code extensions.

## Installation

Once published to PyPI:

```bash
pip install vsce_tui
```

## Usage

After installation:

```bash
code-insiders --list-extensions | vsce_tui  # Initial population of the list
vsce_tui  # Run the interactive TUI
```

To run without installing (for development/testing):

```bash
python vsce_tui/cli.py  # Run directly
code-insiders --list-extensions | python vsce_tui/cli.py # Initial population
```
To clean the extension list

```bash
python vsce_tui/cli.py clean
```

Use the arrow keys (or 'j' and 'k') to navigate, 't' or Spacebar to toggle extension status, 'q' to quit and apply changes, 'x' to quit *without* applying changes, and 'w' to apply changes without quitting.

## Development

```bash
git clone https://github.com/yourusername/vsce_tui # Replace with your repo
cd vsce_tui
uv venv
source .venv/bin/activate  # On Linux/macOS
.venv\Scripts\activate  # On Windows
pip install -e .
```