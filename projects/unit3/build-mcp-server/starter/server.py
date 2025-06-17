#!/usr/bin/env python3
"""
Module 1: Basic MCP Server - Starter Code
TODO: Implement tools for analyzing git changes and suggesting PR templates
"""

import json
import subprocess
from pathlib import Path

from mcp.server.fastmcp import FastMCP

# Initialize the FastMCP server
mcp = FastMCP("pr-agent")

# PR template directory (shared across all modules)
TEMPLATES_DIR = Path(__file__).parent.parent.parent / "templates"


# TODO: Implement tool functions here
# Example structure for a tool:
# @mcp.tool()
# async def analyze_file_changes(base_branch: str = "main", include_diff: bool = True) -> str:
#     """Get the full diff and list of changed files in the current git repository.
#     
#     Args:
#         base_branch: Base branch to compare against (default: main)
#         include_diff: Include the full diff content (default: true)
#     """
#     # Your implementation here
#     pass

# Minimal stub implementations so the server runs
# TODO: Replace these with your actual implementations

@mcp.tool()
async def analyze_file_changes(base_branch: str = "main", include_diff: bool = True, max_diff_lines: int = 500) -> str:
    """Get the full diff and list of changed files in the current git repository.
    
    Args:
        base_branch: Base branch to compare against (default: main)
        include_diff: Include the full diff content (default: true)
        max_diff_lines: Maximum number of diff lines to include (default: 500)
    """
    try:
        # Get working directory from MCP context
        context = mcp.get_context()
        roots_result = await context.session.list_roots()
        working_dir = roots_result.roots[0].uri.path if roots_result.roots else Path.cwd()
        
        # Get list of changed files
        files_result = subprocess.run(
            ["git", "diff", "--name-status", f"{base_branch}...HEAD"],
            cwd=working_dir,
            capture_output=True,
            text=True
        )
        
        if files_result.returncode != 0:
            return json.dumps({
                "error": "Failed to get file changes",
                "details": files_result.stderr
            })
        
        # Parse changed files
        changed_files = []
        for line in files_result.stdout.strip().split('\n'):
            if line:
                parts = line.split('\t', 1)
                if len(parts) == 2:
                    status, filename = parts
                    changed_files.append({
                        "status": status,
                        "filename": filename
                    })
        
        result = {
            "base_branch": base_branch,
            "files_changed": len(changed_files),
            "files": changed_files
        }
        
        # Include diff if requested
        if include_diff and changed_files:
            diff_result = subprocess.run(
                ["git", "diff", f"{base_branch}...HEAD"],
                cwd=working_dir,
                capture_output=True,
                text=True
            )
            
            if diff_result.returncode == 0:
                diff_lines = diff_result.stdout.split('\n')
                
                if len(diff_lines) > max_diff_lines:
                    result["diff"] = '\n'.join(diff_lines[:max_diff_lines])
                    result["diff_truncated"] = True
                    result["total_diff_lines"] = len(diff_lines)
                    result["truncation_message"] = f"Diff truncated to {max_diff_lines} lines (total: {len(diff_lines)} lines)"
                else:
                    result["diff"] = diff_result.stdout
                    result["diff_truncated"] = False
            else:
                result["diff_error"] = diff_result.stderr
        
        return json.dumps(result, indent=2)
        
    except Exception as e:
        return json.dumps({
            "error": "Failed to analyze file changes",
            "details": str(e)
        })


@mcp.tool()
async def get_pr_templates() -> str:
    """List available PR templates with their content."""
    # TODO: Implement this tool
    return json.dumps({"error": "Not implemented yet", "hint": "Read templates from TEMPLATES_DIR"})


@mcp.tool()
async def suggest_template(changes_summary: str, change_type: str) -> str:
    """Let Claude analyze the changes and suggest the most appropriate PR template.
    
    Args:
        changes_summary: Your analysis of what the changes do
        change_type: The type of change you've identified (bug, feature, docs, refactor, test, etc.)
    """
    # TODO: Implement this tool
    return json.dumps({"error": "Not implemented yet", "hint": "Map change_type to templates"})


if __name__ == "__main__":
    mcp.run()