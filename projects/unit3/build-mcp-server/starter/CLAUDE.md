# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

This is a Module 1 starter template for building an MCP (Model Context Protocol) server that helps developers create better pull requests by analyzing code changes and suggesting appropriate templates. The project uses FastMCP for server implementation and is designed as a learning exercise.

## Development Commands

```bash
# Install dependencies
uv sync

# Install with dev dependencies for testing
uv sync --all-extras

# Run unit tests
uv run pytest test_server.py -v

# Validate starter code (for instructors)
python validate_starter.py

# Run the MCP server
python server.py
# or
uv run server.py
```

## Architecture

### Core Components

- `server.py`: Main MCP server implementation using FastMCP
- `test_server.py`: Comprehensive unit tests for all tools
- `validate_starter.py`: Validation script for starter code integrity

### FastMCP Server Structure

The server implements three main tools using the `@mcp.tool()` decorator:

1. **analyze_file_changes**: Retrieves git diff information and changed files
2. **get_pr_templates**: Lists available PR templates from the shared templates directory
3. **suggest_template**: Allows Claude to suggest the most appropriate template based on change analysis

### Template System

- Templates are stored in `../../../templates/` relative to the server
- Available templates: bug.md, docs.md, feature.md, performance.md, refactor.md, security.md, test.md
- Templates are accessed via the `TEMPLATES_DIR` constant

### Design Philosophy

The server follows a "data provider" approach rather than implementing complex logic:

- Provides raw git data to Claude
- Lets Claude's intelligence determine change types and appropriate templates
- Focuses on data retrieval rather than rule-based classification

## Implementation Notes

### Git Operations

- Git commands run in the server's directory by default
- To run in Claude's working directory, use MCP roots:

  ```python
  context = mcp.get_context()
  roots_result = await context.session.list_roots()
  working_dir = roots_result.roots[0].uri.path
  subprocess.run(["git", "diff"], cwd=working_dir)
  ```

### Response Limits

- MCP tools have a 25,000 token response limit
- Large diffs can exceed this limit - consider:
  - Adding max_diff_lines parameter (e.g., 500 lines)
  - Truncating large outputs with messages
  - Returning summary statistics alongside limited diffs

### Testing Strategy

- Unit tests validate both starter code (with "Not implemented" stubs) and full implementations
- Tests check for proper JSON responses, required fields, and tool registration
- Flexible assertions accommodate different implementation approaches

## MCP Configuration

To configure in Claude Code:

```bash
# Add the MCP server
claude mcp add pr-agent -- uv --directory /absolute/path/to/module1/starter run server.py

# Verify configuration
claude mcp list
```

## Dependencies

- Python >=3.10
- mcp[cli] >=1.0.0
- pytest >=8.3.0 (dev)
- pytest-asyncio >=0.21.0 (dev)

<!-- EOF -->
