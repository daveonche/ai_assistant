# Codebase Health Check Prompt

## Version
- Current Version: 1.1.0
- Last Updated: 2026-08-24
- Stability: Experimental

## Description
Comprehensive source code analysis tool that identifies critical issues across multiple dimensions of code quality.

## Purpose
This prompt guides the user through analyzing the codebase for quality, security, and performance issues, providing a categorized report of findings.

## Usage
Use this prompt when you need to perform a health check on your source code, identify technical debt, or prepare for a code review.

### Commands
- `#analyze-health`: Starts or resumes the codebase health analysis workflow.

### Workflow
For the full step-by-step workflow, see `SKILL.md`.

The analysis proceeds through these high-level stages:

1. **Mode & Context Verification**: Ensure `/ask` mode and relevant source files are loaded.
2. **File Collection**: Scan and build a list of source files to analyze.
3. **Per-File Analysis**: Analyze each file for logic, performance, security, error handling, import statements, and structure; then perform project/import-level dependency analysis. Before moving to categorization, validate that at least one finding per file has been recorded.
4. **Issue Categorization**: Organize findings into logic, performance, security, error handling, dependencies, and structure categories. Keep these categories high-level unless the user asks for additional detail.
5. **Interactive Issue Review**: Present categorized findings with issue counts and allow the user to dive deeper, generate the full health report, or focus on critical issues only. Generating the full health report is the default when no selection is made.
6. **Generate Report**: Output the final health analysis report, using severity classification and a `Critical Issues Summary`, and provide instructions to save it.

## Best suited for
- Pre-update code review
- Quality assessment
- Technical debt identification
- Security audit
- Performance optimization
- Maintenance planning
