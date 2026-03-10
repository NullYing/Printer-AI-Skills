# Printer AI Skills

[中文文档](README_CN.md)

A cross-platform local printer CLI that lets AI assistants drive printing operations on Windows, macOS, and Linux. Works with OpenClaw / Cursor / Claude and other AI Skill systems.

## Features

- 🌍 **Cross-platform**: Windows, macOS, Linux (CUPS)
- 🖨️ **Printer Management**: List printers, query status and capabilities
- 📄 **File Printing**: Print with customizable options (paper, color, duplex, etc.)
- 📊 **Job Management**: Track and cancel print jobs
- 🤖 **AI-ready**: CLI + SKILL.md for seamless AI integration

## Quick Start

### Installation

```bash
# Install globally (recommended)
uv tool install git+https://github.com/NullYing/printer-ai-skills.git

# Or local development
git clone https://github.com/NullYing/printer-ai-skills.git
cd printer-ai-skills
uv sync
```

### Usage

```bash
printer-ai printers              # List printers
printer-ai status 1              # Check printer status
printer-ai print file.pdf        # Print a file
printer-ai job-status 123        # Check job status
```

## OpenClaw Skill

Use with [OpenClaw](https://openclaw.com) for the best AI printing experience:

```bash
# 1. Install the Skill
npx clawhub@latest install printer-ai-skills

# 2. Install the CLI tool
uv tool install git+https://github.com/NullYing/printer-ai-skills.git

# 3. Verify
printer-ai printers
```

Once installed, AI will automatically read `SKILL.md` and use CLI commands to manage your local printers — list printers, print files, check job status, and more.

## Cursor / Claude Integration

For Cursor or other AI tools that support Skills:

1. **Install the CLI tool:**
   ```bash
   uv tool install git+https://github.com/NullYing/printer-ai-skills.git
   ```

2. **Add Skill to your project:**
   Copy `SKILL.md` to your project's `.cursor/skills/` directory, or reference it from the repository.

3. **Verify installation:**
   ```bash
   printer-ai printers
   ```

The AI will follow the workflow defined in `SKILL.md` to operate your printers.

## Commands

| Command | Description |
|---------|-------------|
| `printers [--json]` | List all printers |
| `status [INDEX] [--json]` | Get printer status |
| `attrs [INDEX]` | Get printer capabilities |
| `print FILE [--index N] [--options JSON]` | Print a file |
| `jobs [--printer NAME] [--json]` | List print jobs |
| `job-status JOB_ID` | Get job status |
| `cancel-job JOB_ID` | Cancel a job |

## License

MIT License

## Related

- [Original MCP version](https://github.com/NullYing/printer-ai-mcp)
- [CUPS Documentation](https://www.cups.org/)
