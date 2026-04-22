# AGENTS.md

This file provides guidance to opencode (and Claude Code as fallback) when working with code in this repository.

## ⚠️ CRITICAL POLICIES

### Integrity Rule (ABSOLUTE)
- ❌ NO shortcuts - do the work properly or don't do it
- ❌ NO fake data - use real data, real tests, real results
- ❌ NO false claims - only report what actually works and is verified
- ✅ ALWAYS implement all code/tests with proper implementation
- ✅ ALWAYS verify before claiming success
- ✅ ALWAYS use real database queries, not mocks, for integration tests
- ✅ ALWAYS run actual tests, not assume they pass

**We value the quality we deliver to our users.**

### Git Operations
- ❌ NEVER auto-commit/push without explicit user request
- ✅ ALWAYS wait for: "commit this" or "push to main"


## Project Overview

**{PROJECT_NAME}** - brief description of what this project does:
- Key feature 1 (e.g., data storage layer)
- Key feature 2 (e.g., API integration)
- Key feature 3 (e.g., workflow engine)
- Key feature 4 (e.g., UI application)

## Repository Structure

```
{project-name}/
├── backend/             # Backend code (language-specific)
│   ├── core/            # Core library
│   ├── api/             # API layer
├── frontend/            # Frontend application
│   ├── web/             # Web app
├── packages/            # Shared packages/libraries
├── tests/               # Integration tests
└── docs/                # Documentation
```

## Build Commands

### Quick Actions
- `{package-manager} dev` - Start development server
- `{package-manager} build` - Build for production
- `{package-manager} test` - Run all tests
- `{package-manager} lint` - Lint all code
- `make check` - Run pre-push checks

### Backend Development
```bash
{build-tool} build -p {package-name}    # Build specific packages
{build-tool} test --all-features        # Run tests
{build-tool} fmt && {build-tool} lint   # Format and lint
```

**IMPORTANT:** Always use the installed `{cli-name}` CLI when available, NOT the development build command.

### CLI Tool
```bash
{cli-name} {command}             # Primary command
{cli-name} {subcommand} <args>   # Subcommand with arguments
{cli-name} --help                # Show help
```

## Architecture

### Core Components
- **{core-package}** - Core business logic and data layer
- **{cli-package}** - Command-line interface tool
- **{frontend-package}** - User interface application
- **{shared-package}** - Shared types and utilities

### Tech Stack
- **Backend**: {language}, {framework-1}, {framework-2}, {database}
- **Frontend**: {ui-framework}, {state-management}, {ui-library}, {styling}, {build-tool}

## Testing

Test organization:
- Unit tests: Inline with source (language-specific pattern)
- Integration: `{backend-dir}/*/tests/`
- End-to-end: `{e2e-tests-dir}/`

```bash
{test-command}                    # All tests
{test-command} -p {package}       # Specific package
```

## Development Conventions

### File Organization

**NEVER save working files, text/mds, and tests to the root folder.** Use these directories:

- `/{backend-dir}/{package}/src/` - Backend source code
- `/{backend-dir}/*/tests/` - Backend integration tests
- `/{frontend-dir}/src/` - Frontend source code
- `/docs/` - Documentation and architecture files
- `/scripts/` - Build and utility scripts

### Code Style & Best Practices

- **Modular Design**: Files under 500 lines
- **Environment Safety**: Never hardcode secrets
- **Test-First**: Write tests before implementation
- **Clean Architecture**: Separate concerns
- **Documentation**: Keep updated

### TODO Annotations

We use a priority-based TODO annotation system throughout the codebase:

- `TODO(0)`: Critical - never merge
- `TODO(1)`: High - architectural flaws, major bugs
- `TODO(2)`: Medium - minor bugs, missing features
- `TODO(3)`: Low - polish, tests, documentation
- `TODO(4)`: Questions/investigations needed
- `PERF`: Performance optimization opportunities

## Development Methodology

### SPARC Framework

For complex features or refactors, use this structured approach:

1. **Specification** - Requirements analysis & acceptance criteria
2. **Pseudocode** - Algorithm design & logic flow
3. **Architecture** - System design & component structure
4. **Refinement** - TDD implementation & iteration
5. **Completion** - Integration & verification

## Development Workflow

### Task/Issue Management
- Items stored in `knowledge/tickets/` directory
- Use `/prepare_ticket` to create new tickets
- Use `/create_plan_generic` to research and plan
- Use `/implement_plan` to execute
- Use `/create_handoff` to transfer work between sessions

### Logging
- Backend: `{LOG_LEVEL_VAR}=debug`
- CLI: `--verbose` or `-v` flag

## Important Notes

### Workspace Organization
- Backend code isolated in `{backend-dir}/` directory
- Root workspace includes all sub-projects

### Technology Choices
- Current: {current-tech} (MVP/initial implementation)
- Planned: {planned-tech} (future enhancement)

## Configuration Files

- `opencode.json` - opencode configuration (MCP servers, model, instructions)
- `AGENTS.md` - This file (primary instructions for opencode)
- `CLAUDE.md` - Claude Code instructions (also read by opencode as fallback)
- `.opencode/` - opencode-specific commands, agents, and skills
- `.claude/` - Claude Code-specific commands, agents, and skills
- `knowledge/` - Project knowledge base (tickets, research, plans, handoffs)

## Claude Code Behavior

### WebFetch Fallback
When WebFetch fails, use `curl`:
```bash
curl -sL "https://raw.githubusercontent.com/{owner}/{repo}/{branch}/{file}"
curl -sL -H "Accept: application/json" "https://api.example.com/{endpoint}"
```

### Pre-commit/Pre-push Checks
Run `make check` or equivalent before committing:
- `{format-command}` - Format check
- `{lint-command}` - Lint check
- `{test-command}` - Run tests

## Documentation

Key docs in `docs/`:
- `GETTING_STARTED.md` - Initial setup and quickstart
- `ARCHITECTURE.md` - System architecture and design
- `DEPLOYMENT.md` - Deployment instructions
