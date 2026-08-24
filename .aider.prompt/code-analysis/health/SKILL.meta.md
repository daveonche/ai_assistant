# Codebase Health Check Prompt

## Version
- Current Version: 1.0.0
- Last Updated: 2024-12-02
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
1. **Mode Verification**: Ensure you are in `/ask` mode.
2. **Context Verification**: Verify that the relevant source code files are loaded in the context.
3. **File Collection**: Scan and build a list of source files to analyze.
4. **Per-File Analysis**: Analyze each file for logic, performance, security, error handling, dependencies, and structure.
5. **Interactive Issue Review**: Present categorized findings and allow the user to dive deeper or generate a report.
6. **Generate Report**: Output the final health analysis report and provide instructions to save it.

## Best suited for
- Pre-update code review
- Quality assessment
- Technical debt identification
- Security audit
- Performance optimization
- Maintenance planning
