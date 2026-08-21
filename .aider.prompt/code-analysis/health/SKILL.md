# Codebase Health Check Analyzer

When analyzing codebase health:

1. File Collection
- Scan for source code files (.ts, .tsx, .js, .jsx, .css, etc.)
- Exclude documentation files (.md, etc.)
- Build complete file list for review

2. Per-File Analysis
For each source file:
- Check logical flow and correctness
- Evaluate performance characteristics
- Scan for security issues
- Review error handling patterns
- Assess dependency usage
- Examine code structure

3. Issue Categories
Track findings under:
- Logic Issues
  - Control flow problems
  - Data handling errors
  - State management flaws
  
- Performance Issues
  - Resource inefficiencies
  - Unnecessary operations
  - Memory management
  
- Security Issues
  - Input validation
  - Data exposure
  - Authentication/authorization
  
- Error Handling
  - Missing try/catch blocks
  - Uncaught exceptions
  - Error propagation
  
- Dependencies
  - Deprecated packages
  - Version conflicts
  - Unused imports
  
- Structure
  - Code organization
  - Component coupling
  - Pattern consistency

4. Generate Report in below format:

Codebase Health Analysis
Files Reviewed
[List of analyzed files]

Critical Issues
[Priority findings requiring immediate attention]

Issue Details
[Categorized findings with file locations and recommendations]

Summary
[Overall health assessment and next steps]
