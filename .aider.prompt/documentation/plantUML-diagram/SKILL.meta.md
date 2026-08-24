# PlantUML Generator Prompt

## Description

Interactive step-by-step workflow for creating focused, readable PlantUML diagrams that effectively visualize complex systems. The assistant asks staged questions, includes a review/refine loop, and stops for user input at each step until the diagram is finalized.

## Usage

1. Switch to `/ask` mode before using this prompt.
2. Ensure the relevant project source files are available in context, or let the assistant ask you to add them.
3. Use the shorthand command: `$documentation-plantUML-diagram`

## Best suited for

- Architecture documentation
- System visualization
- Component relationship mapping
- Process flow documentation
- Interface design
- Dependency analysis

## Output format

- PlantUML syntax in a fenced code block with language `plantuml`
- Optionally saved as `*.puml` file for rendering

## Quality goals

- Focused component selection
- Clear relationships
- Optimized diagram size
- Ready-to-render code

## Workflow behavior

- Step-by-step guided interaction
- Stops for user input at each step
- Includes final review and refinement loop
