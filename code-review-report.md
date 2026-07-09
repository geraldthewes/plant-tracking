# OCR Code Review Report

**Files reviewed:** 314  
**Comments:** 242  
**Duration:** 13h47m48s

## `.agents/skills/bmad-agent-architect/customize.toml`

**Lines 1-5**

Consider adding an SPDX license identifier to comply with licensing requirements. Since the file is marked as overwritten on every update, ensure the license identifier is added to the template or generation process.

**Suggested fix:**
```diff
- # DO NOT EDIT -- overwritten on every update.
#
# Winston, the System Architect, is the hardcoded identity of this agent.
# Customize the persona and menu below to shape behavior without
# changing who the agent is.
+ # DO NOT EDIT -- overwritten on every update.
#
# Winston, the System Architect, is the hardcoded identity of this agent.
# Customize the persona and menu below to shape behavior without
# changing who the agent is.
# SPDX-License-Identifier: <license-identifier>
```

---

## `.agents/skills/bmad-distillator/scripts/analyze_sources.py`

**Lines 127-127**

Using a map keyed only by filename can cause incorrect grouping when there are files with the same name in different directories. Consider using a map keyed by the full path or, better, when looking for a base file, look in the same directory as the companion file.

---

**Lines 145-145**

This lookup uses only the filename, which may match a file in a different directory. Instead, we should check for the existence of the base file in the same directory as the companion file.

---

**Lines 203-203**

Calling f.stat() may raise an OSError (e.g., if the file is deleted after being listed or due to permission issues). Consider wrapping in a try-except block and skipping the file or logging an error.

---

**Lines 87-87**

This condition returns False for broken symlinks, which then fall through to the glob handling. This may lead to unexpected behavior. Consider explicitly checking for symlinks and handling them appropriately (e.g., skipping or reporting an error).

---

## `.agents/skills/bmad-distillator/scripts/tests/test_analyze_sources.py`

**Lines 7-7**

Unused import: 'patch' from unittest.mock is imported but not used in this test file. Remove unused imports to keep code clean.

---

## `.claude/skills/bmad-agent-analyst/customize.toml`

**Lines 38-40**

The glob pattern '**' may match an excessive number of files in large projects, potentially causing performance degradation during agent activation. Consider narrowing the pattern to specific known locations (e.g., 'file:{project-root}/project-context.md') or using a more specific glob.

---

**Lines 1-5**

This warning indicates the file is overwritten on updates, which may lead to loss of user customizations if users edit this file directly. Ensure documentation clearly explains the proper customization mechanism (e.g., via override files in _bmad/custom/) to avoid confusion.

---

## `.claude/skills/bmad-create-architecture/customize.toml`

**Lines 33-35**

TOML arrays do not allow trailing commas per the TOML v1.0.0 specification. This may cause parsing errors in strict TOML parsers. Remove the trailing comma to ensure valid TOML syntax.

**Suggested fix:**
```diff
- +persistent_facts = [
+  "file:{project-root}/**/project-context.md",
+]
+ +persistent_facts = [
+  "file:{project-root}/**/project-context.md"
+]
```

---

## `.claude/skills/bmad-distillator/scripts/analyze_sources.py`

**Lines 203-203**

Handle potential OSError when getting file size (e.g., permission issues, file removed). Skip the file and log a warning to avoid crashing the entire process.

**Suggested fix:**
```diff
- size = f.stat().st_size
+ try:
            size = f.stat().st_size
        except OSError as e:
            print(f"Warning: Could not read size for {f}: {e}", file=sys.stderr)
            continue
```

---

**Lines 142-159**

The grouping logic may create groups with only companion files when the base file is missing. Suggest only adding companions to groups when the base file exists in the input files.

**Suggested fix:**
```diff
-                 if group_key not in groups:
                    groups[group_key] = []
                    # Add the base file if it exists
                    if base_name in file_map and base_name not in assigned:
                        groups[group_key].append({
                            "path": str(file_map[base_name]),
                            "filename": base_name,
                            "role": "primary",
                        })
                        assigned.add(base_name)
                groups[group_key].append({
                    "path": str(f),
                    "filename": f.name,
                    "role": "companion",
                })
                assigned.add(f.name)
                matched = True
                break
+                 if group_key not in groups:
                    groups[group_key] = []
                    # Only add base if it exists and is not already assigned
                    if base_name in file_map and base_name not in assigned:
                        groups[group_key].append({
                            "path": str(file_map[base_name]),
                            "filename": base_name,
                            "role": "primary",
                        })
                        assigned.add(base_name)
                # Only add companion if base exists in our file set
                if base_name in file_map:
                    groups[group_key].append({
                        "path": str(f),
                        "filename": f.name,
                        "role": "companion",
                    })
                    assigned.add(f.name)
                    matched = True
                    break
```

---

## `.claude/skills/bmad-prfaq/customize.toml`

**Lines 34-34**

TOML arrays do not allow trailing commas. Please remove the trailing comma after the last element in the array to avoid a syntax error.

**Suggested fix:**
```diff
-   "file:{project-root}/**/project-context.md",
+   "file:{project-root}/**/project-context.md"
```

---

## `.claude/skills/bmad-technical-research/customize.toml`

**Lines 33-35**

TOML specification does not allow trailing commas in arrays. Remove the trailing comma after the last element in the persistent_facts array to ensure valid TOML syntax.

**Suggested fix:**
```diff
- persistent_facts = [
  "file:{project-root}/**/project-context.md",
]
+ persistent_facts = [
  "file:{project-root}/**/project-context.md"
]
```

---

## `.gitignore`

**Lines 4-4**

The pattern '*.pyo' is redundant because it is already matched by '*.py[cod]' (which includes .pyc, .pyo, and .pyd). Removing this line reduces redundancy and maintenance overhead.

---

**Lines 54-54**

The pattern '#*#' appears multiple times in this file (on this line, the next line, and in the Emacs section). Consider if this duplication is necessary for maintainability.

---

**Lines 20-23**

Duplicate line: '.env' already appears above (line 19). Remove this duplicate to reduce redundancy.

**Suggested fix:**
```diff
- +venv/
+.venv/
+env/
+.env
+ +venv/
+.venv/
+env/
```

---

## `.opencodereview/generate-rules.py`

**Lines 16-19**

The function `load_rule_file` reads a file without error handling. Consider wrapping the `path.read_text` call in a try-except block to catch potential IO errors (e.g., FileNotFoundError, PermissionError, UnicodeDecodeError) and either re-raise with more context or handle appropriately (e.g., by logging and returning a default value or raising a custom exception).

**Suggested fix:**
```diff
- def load_rule_file(path: Path) -> str:
    """Load a markdown rule file and return its content as a clean string."""
    content = path.read_text(encoding="utf-8").strip()
    return content.replace("\r\n", "\n")
+ def load_rule_file(path: Path) -> str:
    """Load a markdown rule file and return its content as a clean string."""
    try:
        content = path.read_text(encoding="utf-8").strip()
        return content.replace("\r\n", "\n")
    except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
        raise RuntimeError(f"Failed to load rule file '{path}': {e}") from e
```

---

**Lines 18-19**

The function `load_rule_file` reads a file without error handling. Consider wrapping the `path.read_text` call in a try-except block to catch potential IO errors (e.g., FileNotFoundError, PermissionError, UnicodeDecodeError) and either re-raise with more context or handle appropriately.

**Suggested fix:**
```diff
- content = path.read_text(encoding="utf-8").strip()
return content.replace("\r\n", "\n")
+ try:
    content = path.read_text(encoding="utf-8").strip()
    return content.replace("\r\n", "\n")
except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
    raise RuntimeError(f"Failed to load rule file '{path}': {e}") from e
```

---

**Lines 26-26**

The function `load_secure_coding_rules` calls `load_rule_file` in a list comprehension without error handling. If any rule file fails to load, the entire function will crash. Consider wrapping each file load in a try-except block to provide meaningful error messages.

**Suggested fix:**
```diff
- contents = [load_rule_file(f) for f in files]
+ contents = []
for f in files:
    try:
        contents.append(load_rule_file(f))
    except Exception as e:
        raise RuntimeError(f"Failed to load secure coding rule file '{f}': {e}") from e
```

---

**Lines 85-88**

The function `main` writes the output file without error handling. Consider wrapping the `OUTPUT_FILE.write_text` call in a try-except block to catch potential IO errors (e.g., FileNotFoundError, PermissionError, UnicodeDecodeError).

**Suggested fix:**
```diff
- OUTPUT_FILE.write_text(
    json.dumps(output, indent=2, ensure_ascii=False) + "\n",
    encoding="utf-8"
)
+ try:
    OUTPUT_FILE.write_text(
        json.dumps(output, indent=2, ensure_ascii=False) + "\n",
        encoding="utf-8"
    )
except (FileNotFoundError, PermissionError, UnicodeDecodeError) as e:
    raise RuntimeError(f"Failed to write rule file '{OUTPUT_FILE}': {e}") from e
```

---

**Lines 30-30**

The function `main` is missing a return type hint and a docstring. Add `-> None` and a docstring describing the function's purpose.

**Suggested fix:**
```diff
- def main():
+ def main() -> None:
    """Generate rule.json from Markdown files in the rules/ directory."""
```

---

## `.qwen/skills/bmad-agent-dev/customize.toml`

**Lines 38-40**

Trailing comma in TOML array is invalid. Remove the comma after the last element.

**Suggested fix:**
```diff
- persistent_facts = [
   "file:{project-root}/**/project-context.md",
 ]
+ persistent_facts = [
   "file:{project-root}/**/project-context.md"
 ]
```

---

**Lines 47-51**

Trailing comma in TOML array is invalid. Remove the comma after the last element.

**Suggested fix:**
```diff
- principles = [
   "No task complete without passing tests.",
   "Red, green, refactor — in that order.",
   "Tasks executed in the sequence written.",
 ]
+ principles = [
   "No task complete without passing tests.",
   "Red, green, refactor — in that order.",
   "Tasks executed in the sequence written."
 ]
```

---

## `.qwen/skills/bmad-code-review/customize.toml`

**Lines 1-1**

The warning 'DO NOT EDIT -- overwritten on every update.' may be misleading because this file is in the Qwen agent's customization directory and is described as a 'Workflow customization surface'. If the file is intended to be customized by the user (as the location and purpose suggest), then this warning should be removed. If the file is going to be overwritten by an update process, then the warning is correct and no change is needed. However, given that the file is being added to version control and there are similar files for other agents, it appears that this file is meant for customization. Consider removing the warning line.

---

## `.qwen/skills/bmad-customize/scripts/list_customizable_skills.py`

**Lines 109-109**

The call to `root.iterdir()` may raise a `PermissionError` or `OSError` if the directory is not readable (e.g., due to insufficient permissions). This would cause the script to crash without producing any output. Consider wrapping the iteration in a try-except block to catch such errors and add an appropriate error message.

**Suggested fix:**
```diff
-         for skill_dir in sorted(p for p in root.iterdir() if p.is_dir()):
+         try:
            entries = root.iterdir()
        except (PermissionError, OSError) as e:
            errors.append(f"failed to iterate skills root {root}: {e}")
            continue

        skill_dirs = [p for p in entries if p.is_dir()]
        for skill_dir in sorted(skill_dirs):
```

---

**Lines 41-41**

The FRONTMATTER_RE pattern is too strict; it requires a newline after the opening '---' and before the closing '---'. This may fail to extract descriptions from valid SKILL.md files where the frontmatter does not strictly adhere to this format (e.g., missing newlines). Consider using a more permissive pattern that allows optional whitespace around the markers.

**Suggested fix:**
```diff
- FRONTMATTER_RE = re.compile(r"^---\s*\n(.*?)\n---\s*\n", re.DOTALL)
+ FRONTMATTER_RE = re.compile(r"^---\s*(.*?)\s*---", re.DOTALL)
```

---

## `.qwen/skills/bmad-customize/scripts/tests/test_list_customizable_skills.py`

**Lines 51-52**

Add a docstring to the test class to describe what it tests.

**Suggested fix:**
```diff
- class ScannerTest(unittest.TestCase):
    def setUp(self):
+ class ScannerTest(unittest.TestCase):
    """Test suite for the list_customizable_skills scanner."""
    def setUp(self):
```

---

## `_bmad/config.toml`

**Lines 0-0**

The configuration uses unresolved placeholders (e.g., {project-root}) in path values. If the installer fails to replace these placeholders during generation of this installer-managed file, the application may interpret them as literal directory names, causing file operations to target incorrect paths and potentially leading to data loss, misplaced artifacts, or broken functionality. Although the file is marked as installer-managed, the provided resolution scripts (_bmad/scripts/resolve_config.py and _bmad/scripts/resolve_customization.py) do not perform placeholder substitution, raising concern about whether substitution occurs reliably.

**Suggested fix:**
```diff
- +output_folder = "{project-root}/_bmad-output"
+
+[modules.bmm]
+project_name = "plant-tracking"
+planning_artifacts = "{project-root}/_bmad-output/planning-artifacts"
+implementation_artifacts = "{project-root}/_bmad-output/implementation-artifacts"
+project_knowledge = "{project-root}/docs"
+ +output_folder = "{project-root}/_bmad-output"
+
+[modules.bmm]
+project_name = "plant-tracking"
+planning_artifacts = "{project-root}/_bmad-output/planning-artifacts"
+implementation_artifacts = "{project-root}/_bmad-output/implementation-artifacts"
+project_knowledge = "{project-root}/docs"
```

---

## `_bmad/config.user.toml`

**Lines 0-0**

This file contains user-specific settings (user name, language, skill level). Committing user-specific settings to the repository is not recommended as the file is installer-managed and will be overwritten by the installer, potentially losing user-specific settings and causing conflicts.

---

## `_bmad/scripts/resolve_config.py`

**Lines 45-68**

Add a docstring describing the function's purpose, parameters, return value, and error handling behavior.

---

**Lines 45-68**

Add a docstring describing the function's purpose, parameters, return value, and error handling behavior.

---

**Lines 71-77**

Add type hints: items should be list[object], return type should be str | None.

---

**Lines 80-100**

Add type hints: base: list[object] | dict | ..., override: list[object] | dict | ..., key_name: str -> list[object]. Also add a docstring describing the function's purpose, parameters, return value, and merging logic.

---

**Lines 103-109**

Add type hints: base: list[object] | object, override: list[object] | object -> list[object]. Also add a docstring describing the function's purpose, parameters, return value, and merging logic.

---

**Lines 112-123**

Add type hints: base: dict | list | any, override: dict | list | any -> dict | list | any. Also add a docstring describing the function's purpose, parameters, return value, and merging behavior (deep merge for dicts, concatenation or key-based merge for lists, override wins for scalars).

---

**Lines 126-134**

Add a docstring describing the function's purpose, parameters, return value, and behavior. Also add type hints: data: dict, dotted_key: str -> any | _MISSING.

---

**Lines 0-0**

Add a docstring describing the function's purpose, parameters, and behavior.

---

## `_bmad/scripts/resolve_customization.py`

**Lines 56-56**

Add return type hint Optional[Path] to find_project_root function.

**Suggested fix:**
```diff
- def find_project_root(start: Path):
+ def find_project_root(start: Path) -> Optional[Path]:
```

---

**Lines 56-64**

Add docstring for find_project_root function explaining its purpose, arguments, and return value.

**Suggested fix:**
```diff
- def find_project_root(start: Path):
    current = start.resolve()
    while True:
        if (current / "_bmad").exists() or (current / ".git").exists():
            return current
        parent = current.parent
        if parent == current:
            return None
        current = parent
+ """Find the project root by looking for _bmad or .git directories.

        Args:
            start: The starting path to search from.

        Returns:
            The project root as a Path object, or None if not found.
        """
```

---

**Lines 67-67**

Add docstring for load_toml function explaining its purpose, arguments, and return value.

**Suggested fix:**
```diff
- def load_toml(file_path: Path, required: bool = False) -> dict:
+ """Load a TOML file and return its contents as a dictionary.

        Args:
            file_path: Path to the TOML file.
            required: If True, exit with error if file is missing or invalid.

        Returns:
            Dictionary containing the TOML file's contents, or empty dictionary if file is missing/invalid and not required.
        """
```

---

## `alembic.ini`

**Lines 87-87**

This placeholder SQLAlchemy URL is overridden by the value from the DATABASE_URL environment variable in alembic/env.py. Ensure that the environment variable is set in all environments to avoid connection errors.

---

**Lines 96-96**

This line is part of an example configuration for post_write_hooks using black. The entire post_write_hooks section is commented out, so these hooks are inactive. If the project does not intend to use these hooks, consider removing the example to avoid confusion. If the project does use black or ruff, uncomment and configure the hooks as needed.

---

## `alembic/README`

**Lines 1-1**

The file should end with a newline. Please add a newline at the end of the file.

**Suggested fix:**
```diff
- Generic single-database configuration.
+ Generic single-database configuration.

```

---

## `alembic/env.py`

**Lines 0-0**

Module missing docstring. Add a module-level docstring describing the purpose of this Alembic environment configuration file.

**Suggested fix:**
```diff
- from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)
+ """
Alembic environment configuration for plant_service database migrations.

This file configures Alembic to work with the plant_service package,
setting up Python paths, importing models for autogeneration support,
and defining offline/online migration runners.
"""
from logging.config import fileConfig
import os
import sys

from sqlalchemy import engine_from_config
from sqlalchemy import pool

from alembic import context

config = context.config

if config.config_file_name is not None:
    fileConfig(config.config_file_name)
```

---

**Lines 38-43**

Function get_url missing return type hint and could benefit from a more detailed docstring describing return value and exceptions.

---

**Lines 38-43**

Function get_url missing return type hint and could benefit from a more detailed docstring describing return value and exceptions.

**Suggested fix:**
```diff
- def get_url():
    """Get database URL from environment variable"""
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable must be set")
    return url
+ def get_url() -> str:
    """Get database URL from environment variable.

    Returns:
        str: The database URL.

    Raises:
        ValueError: If DATABASE_URL environment variable is not set.
    """
    url = os.environ.get("DATABASE_URL")
    if not url:
        raise ValueError("DATABASE_URL environment variable must be set")
    return url
```

---

## `alembic/versions/72fff22905dd_initial_migration.py`

**Lines 71-71**

The 'timestamp' column is defined as String(length=20) but should be DateTime for proper date/time operations and consistency with other timestamp columns (created_at, updated_at).

**Suggested fix:**
```diff
- sa.Column('timestamp', sa.String(length=20), nullable=False),
+ sa.Column('timestamp', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
```

---

**Lines 48-48**

The ID length for plants is 20, while genera and seed_packets use 10. This inconsistency may cause confusion or require application-level validation. Consider making ID lengths consistent unless there is a specific reason for the difference.

**Suggested fix:**
```diff
- sa.Column('id', sa.String(length=20), nullable=False),
+ sa.Column('id', sa.String(length=10), nullable=False),
```

---

**Lines 80-80**

The check constraint for event_type_fields does not prevent setting irrelevant fields (e.g., amount_ml for a humidity event). Consider adding constraints to ensure that irrelevant fields are NULL for each event type to avoid storing unnecessary data.

---

## `alembic/versions/f6a7830adb3d_add_media_attachments_table.py`

**Lines 31-31**

Consider using sa.DateTime(timezone=True) for the timestamp column for consistency with created_at/updated_at and to enable date/time operations. If the timestamp is intended to be stored as a formatted string, please add a comment specifying the expected format.

**Suggested fix:**
```diff
- sa.Column("timestamp", sa.String(20), nullable=False),
+         sa.Column("timestamp", sa.DateTime(timezone=True), nullable=False,
```

---

## `backend/fastapi/scripts/export_openapi.py`

**Lines 0-0**

The script lacks error handling for importing the app, generating the OpenAPI spec, and writing the file. It also does not ensure the output directory exists. This could lead to silent failures or unhandled exceptions. Consider wrapping the main logic in a try-except block to handle ImportError and general exceptions, and create the output directory if it doesn't exist.

**Suggested fix:**
```diff
- if __name__ == "__main__":
    openapi_json = app.openapi()
    output_path = os.path.join(os.path.dirname(__file__), '..', 'openapi.json')
    
    with open(output_path, 'w') as f:
        json.dump(openapi_json, f, indent=2)
    
    print(f"OpenAPI spec exported to {output_path}")
+ if __name__ == "__main__":
    try:
        output_path = os.path.join(os.path.dirname(__file__), '..', 'openapi.json')
        output_dir = os.path.dirname(output_path)
        os.makedirs(output_dir, exist_ok=True)
        
        openapi_json = app.openapi()
        
        with open(output_path, 'w') as f:
            json.dump(openapi_json, f, indent=2)
        
        print(f"OpenAPI spec exported to {output_path}")
    except ImportError as e:
        print(f"Error: Unable to import the FastAPI app. {e}", file=sys.stderr)
        sys.exit(1)
    except Exception as e:
        print(f"Error: An unexpected error occurred. {e}", file=sys.stderr)
        sys.exit(1)
```

---

## `backend/fastapi/src/plant_tracking_api/config.py`

**Lines 1-2**

Missing module docstring. Add a docstring at the top of the module to describe its purpose.

**Suggested fix:**
```diff
- import os
from pathlib import Path
+ """Module docstring: Application configuration settings.

import os
from pathlib import Path"
```

---

**Lines 1-2**

Missing module docstring. Add a docstring at the top of the module to describe its purpose.

**Suggested fix:**
```diff
- import os
from pathlib import Path
+ """Application configuration settings."""
import os
from pathlib import Path
```

---

**Lines 13-18**

Missing docstring for __init__ method. Add a docstring explaining the environment variables used and their defaults.

**Suggested fix:**
```diff
- def __init__(self):
        self.database_url: Optional[str] = os.getenv("DATABASE_URL")
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.reload: bool = os.getenv("RELOAD", "false").lower() == "true"
        self.log_level: str = os.getenv("LOG_LEVEL", "info")
+ def __init__(self):
        """Initialize settings from environment variables.

        The following environment variables are used:
        - DATABASE_URL: Optional database connection string.
        - HOST: Host to bind the server to (default: "0.0.0.0").
        - PORT: Port to bind the server to (default: 8000).
        - RELOAD: Whether to enable auto-reload (default: "false").
        - LOG_LEVEL: Logging level (default: "info").
        """
        self.database_url: Optional[str] = os.getenv("DATABASE_URL")
        self.host: str = os.getenv("HOST", "0.0.0.0")
        self.port: int = int(os.getenv("PORT", "8000"))
        self.reload: bool = os.getenv("RELOAD", "false").lower() == "true"
        self.log_level: str = os.getenv("LOG_LEVEL", "info")
```

---

## `backend/fastapi/src/plant_tracking_api/dependencies.py`

**Lines 7-10**

The dependency function get_uow() creates a UnitOfWork and yields it, but does not ensure proper cleanup. Since SqlAlchemyUnitOfWork implements AbstractContextManager with __enter__ and __exit__ methods that handle session commit/rollback and closing, we need to ensure __exit__ is called after the request completes. Currently, the session may remain open and uncommitted/rolled back, leading to resource leaks and incomplete transactions.

**Suggested fix:**
```diff
- def get_uow() -> Generator[SqlAlchemyUnitOfWork, None, None]:
    """Dependency that provides a UnitOfWork instance per request."""
    uow = create_unit_of_work()
    yield uow
+ def get_uow() -> Generator[SqlAlchemyUnitOfWork, None, None]:
    """Dependency that provides a UnitOfWork instance per request."""
    with create_unit_of_work() as uow:
        yield uow
```

---

## `backend/fastapi/src/plant_tracking_api/routes/health.py`

**Lines 0-0**

Module is missing a docstring. Please add a module docstring at the top of the file.

**Suggested fix:**
```diff
- from fastapi import APIRouter

router = APIRouter()
+ """Health check routes for the Plant Tracking API."""

from fastapi import APIRouter

router = APIRouter()
```

---

**Lines 6-9**

Function `health_check` is missing a return type hint. Please add `-> dict[str, str]`.

**Suggested fix:**
```diff
- @router.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}
+ @router.get("/health")
async def health_check() -> dict[str, str]:
    """Health check endpoint."""
    return {"status": "healthy"}
```

---

**Lines 12-15**

Function `root` is missing a return type hint. Please add `-> dict[str, str]`.

**Suggested fix:**
```diff
- @router.get("/")
async def root():
    """Root endpoint."""
    return {"message": "Plant Tracking API"}
+ @router.get("/")
async def root() -> dict[str, str]:
    """Root endpoint."""
    return {"message": "Plant Tracking API"}
```

---

## `backend/fastapi/src/plant_tracking_api/routes/media_attachments.py`

**Lines 18-23**

Unused function `get_media_service` is defined but not used in any route. Consider removing it or using it as a dependency in the routes to avoid duplication.

---

**Lines 0-0**

In `create_media_attachment`, the service is created manually instead of using the `get_media_service` dependency. This leads to code duplication. Use the dependency to ensure consistency.

---

**Lines 39-42**

Reading the entire file into memory with `await file.read()` could cause memory issues for large files. Consider streaming the file to disk in chunks.

---

**Lines 169-170**

In `delete_media_attachment`, the S3 deletion is not wrapped in error handling. If S3 deletion fails, the function proceeds to delete from the database, leading to inconsistency (file remains in S3 but record deleted). Handle S3 errors appropriately.

---

**Lines 0-0**

In `get_media_attachment_url`, the `expiration` parameter is taken from Form data in a GET request. This is non-standard; use a query parameter instead.

---

## `backend/fastapi/src/plant_tracking_api/routes/plants.py`

**Lines 10-12**

Missing return type hint for public function. According to guidelines, every public function must have type hints. Please add a return type annotation. For now, since we return a dict with 'count' (int) and 'plants' (list), we can use `-> dict[str, int | list]`. Note that the 'plants' list will eventually contain plant objects, so we may update this type when the logic is implemented.

**Suggested fix:**
```diff
- +async def get_plants_needing_care(
+    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
+):
+ +async def get_plants_needing_care(
+    uow: SqlAlchemyUnitOfWork = Depends(get_uow),
+    ) -> dict[str, int | list]:
```

---

## `backend/fastapi/tests/conftest.py`

**Lines 7-9**

The function name starts with 'test_', which will cause pytest to collect it as a test function. This is not intended because it is a helper function for setting up a dependency override. Consider renaming it to avoid the 'test_' prefix (e.g., 'get_uow_mock').

---

**Lines 7-9**

The function returns `None`. If the code under test expects to use the returned unit of work object (e.g., by calling methods on it), this will result in an AttributeError. Consider returning a mock object (e.g., using unittest.mock.MagicMock) that can be configured in tests to provide the expected behavior or to record calls.

---

**Lines 7-9**

The function name starts with 'test_', which will cause pytest to collect it as a test. This is not intended because it is a helper function for setting up a dependency override. Consider renaming it to avoid the 'test_' prefix (e.g., 'get_uow_mock'). Also, the function returns `None`. If the code under test expects to use the returned unit of work object (e.g., by calling methods on it), this will result in an AttributeError. Consider returning a mock object (e.g., using unittest.mock.MagicMock) that can be configured in tests to provide the expected behavior or to record calls. Remember to import MagicMock from unittest.mock.

---

**Lines 0-0**

Add an import for MagicMock from unittest.mock to use in the get_uow_mock function.

**Suggested fix:**
```diff
- import pytest

from plant_tracking_api.dependencies import get_uow
from plant_tracking_api.main import app
+ import pytest
from unittest.mock import MagicMock

from plant_tracking_api.dependencies import get_uow
from plant_tracking_api.main import app
```

---

## `backend/fastapi/tests/test_plants.py`

**Lines 4-4**

Missing module docstring and import for TestClient. Please add a module docstring and import the TestClient at the top of the file.

**Suggested fix:**
```diff
- def test_get_plants_needing_care_returns_empty(client):
+ """
Test module for plant-related endpoints.
"""

from fastapi.testclient import TestClient

def test_get_plants_needing_care_returns_empty(client):
```

---

**Lines 4-4**

Missing type hint for the `client` argument and return type. Please add type hints: `client: TestClient` and return type `None`.

**Suggested fix:**
```diff
- def test_get_plants_needing_care_returns_empty(client):
+ def test_get_plants_needing_care_returns_empty(client: TestClient) -> None:
```

---

**Lines 14-14**

Missing type hint for the `client` argument and return type. Please add type hints: `client: TestClient` and return type `None`.

**Suggested fix:**
```diff
- def test_health_check_endpoint(client):
+ def test_health_check_endpoint(client: TestClient) -> None:
```

---

## `commands/database.py`

**Lines 21-33**

Function _get_engine() is missing a return type hint. Should return 'Engine' from sqlalchemy.engine

**Suggested fix:**
```diff
- def _get_engine():
    """Get or create the database engine."""
    global engine
    if engine is None:
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable must be set")
        engine = create_engine(
            DATABASE_URL,
            poolclass=SingletonThreadPool,
            pool_pre_ping=True,
            echo=False,
        )
    return engine
+ def _get_engine() -> Engine:
    """Get or create the database engine."""
    global engine
    if engine is None:
        if not DATABASE_URL:
            raise ValueError("DATABASE_URL environment variable must be set")
        engine = create_engine(
            DATABASE_URL,
            poolclass=SingletonThreadPool,
            pool_pre_ping=True,
            echo=False,
        )
    return engine
```

---

**Lines 36-44**

Function _get_session_factory() is missing a return type hint. Should return 'sessionmaker' from sqlalchemy.orm

**Suggested fix:**
```diff
- def _get_session_factory():
    """Get or create the session factory."""
    global SessionLocal
    if SessionLocal is None:
        eng = _get_engine()
        SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=eng, expire_on_commit=False
        )
    return SessionLocal
+ def _get_session_factory() -> sessionmaker:
    """Get or create the session factory."""
    global SessionLocal
    if SessionLocal is None:
        eng = _get_engine()
        SessionLocal = sessionmaker(
            autocommit=False, autoflush=False, bind=eng, expire_on_commit=False
        )
    return SessionLocal
```

---

**Lines 0-0**

Circular import risk: importing 'from . import models' and 'from .models.base import Base' inside init_db() may cause circular imports because model modules (e.g., commands/models/genus.py) import from commands.database at module level. Consider moving database-dependent imports inside the model functions or using dependency injection to break the cycle.

**Suggested fix:**
```diff
- def init_db() -> None:
    """Initialize database tables"""
    from . import models  # noqa: F401
    from .models.base import Base

    eng = _get_engine()
    Base.metadata.create_all(bind=eng)
+ def init_db() -> None:
    """Initialize database tables"""
    # Avoid circular imports by importing models inside function
    # Note: Model modules should avoid importing from commands.database at module level
    from . import models  # noqa: F401
    from .models.base import Base

    eng = _get_engine()
    Base.metadata.create_all(bind=eng)
```

---

**Lines 91-107**

Performance issue: Using .all() loads entire tables into memory which can cause high memory usage for large datasets. Consider using yield_per() or pagination for large datasets.

**Suggested fix:**
```diff
-         for packet in session.query(SeedPacket).all():
            packet_data = {
                "id": packet.id,
                "variety_name": packet.variety_name,
                "latin_name": packet.latin_name,
                "brand": packet.brand or "unknown",
                "days_to_maturity": packet.days_to_maturity or "unknown",
                "germination_time": packet.germination_time or "unknown",
                "planting_depth": packet.planting_depth or "unknown",
                "spacing": packet.spacing or "unknown",
                "sun_requirements": packet.sun_requirements or "unknown",
                "indoor_start_time": packet.indoor_start_time or "unknown",
            }
            markdown_packet = MarkdownSeedPacket(packet_data)
            packet_file = export_dir / "seed_packets" / f"{packet.id}.md"
            with open(packet_file, "w") as f:
                f.write(markdown_packet.to_markdown())
+         # Process in batches to avoid memory issues with large datasets
        batch_size = 1000
        offset = 0
        while True:
            packets = session.query(SeedPacket).offset(offset).limit(batch_size).all()
            if not packets:
                break
            for packet in packets:
                packet_data = {
                    "id": packet.id,
                    "variety_name": packet.variety_name,
                    "latin_name": packet.latin_name,
                    "brand": packet.brand or "unknown",
                    "days_to_maturity": packet.days_to_maturity or "unknown",
                    "germination_time": packet.germination_time or "unknown",
                    "planting_depth": packet.planting_depth or "unknown",
                    "spacing": packet.spacing or "unknown",
                    "sun_requirements": packet.sun_requirements or "unknown",
                    "indoor_start_time": packet.indoor_start_time or "unknown",
                }
                markdown_packet = MarkdownSeedPacket(packet_data)
                packet_file = export_dir / "seed_packets" / f"{packet.id}.md"
                with open(packet_file, "w") as f:
                    f.write(markdown_packet.to_markdown())
            offset += batch_size
```

---

**Lines 0-0**

Inefficient log file handling: Opening and closing the log file for each entry in append mode is inefficient. Consider collecting all entries and writing them once, or at least open the file once in append mode and write all entries.

**Suggested fix:**
```diff
-         for entry in log_entries:
            entry_data = {
                "plant_id": entry.plant_id,
                "event_type": entry.event_type,
                "timestamp": entry.timestamp,
            }
            if entry.event_type == "humidity":
                entry_data["level"] = entry.level
            elif entry.event_type == "water":
                entry_data["amount_ml"] = entry.amount_ml
            elif entry.event_type == "fertilizer":
                entry_data["type"] = entry.fertilizer_type
                entry_data["strength"] = entry.fertilizer_strength
            elif entry.event_type == "note":
                entry_data["text"] = entry.text

            from .plant_log_model import PlantLogEntry as MarkdownPlantLogEntry

            markdown_entry = MarkdownPlantLogEntry(entry_data)
            yaml_content = yaml.dump(
                markdown_entry.to_yaml_entry(), default_flow_style=False, sort_keys=False
            )
            with open(log_file, "a") as f:
                if f.tell() > 0:
                    f.write("\n")
                f.write(f"---\n{yaml_content}...\n")
+         # Open log file once for writing all entries to improve performance
        with open(log_file, "a") as log_f:
            for entry in log_entries:
                entry_data = {
                    "plant_id": entry.plant_id,
                    "event_type": entry.event_type,
                    "timestamp": entry.timestamp,
                }
                if entry.event_type == "humidity":
                    entry_data["level"] = entry.level
                elif entry.event_type == "water":
                    entry_data["amount_ml"] = entry.amount_ml
                elif entry.event_type == "fertilizer":
                    entry_data["type"] = entry.fertilizer_type
                    entry_data["strength"] = entry.fertilizer_strength
                elif entry.event_type == "note":
                    entry_data["text"] = entry.text

                from .plant_log_model import PlantLogEntry as MarkdownPlantLogEntry

                markdown_entry = MarkdownPlantLogEntry(entry_data)
                yaml_content = yaml.dump(
                    markdown_entry.to_yaml_entry(), default_flow_style=False, sort_keys=False
                )
                if log_f.tell() > 0:
                    log_f.write("\n")
                log_f.write(f"---\n{yaml_content}...\n")
```

---

**Lines 0-0**

Risk of partial export directory left on failure: If an exception occurs during file writing in export_to_markdown(), partially written files may remain in export directory without cleanup. Consider adding exception handling and cleanup mechanism.

**Suggested fix:**
```diff
-     try:
        # Export seed packets
        from .seed_packet_model import SeedPacket as MarkdownSeedPacket

        for packet in session.query(SeedPacket).all():
            packet_data = {
                "id": packet.id,
                "variety_name": packet.variety_name,
                "latin_name": packet.latin_name,
                "brand": packet.brand or "unknown",
                "days_to_maturity": packet.days_to_maturity or "unknown",
                "germination_time": packet.germination_time or "unknown",
                "planting_depth": packet.planting_depth or "unknown",
                "spacing": packet.spacing or "unknown",
                "sun_requirements": packet.sun_requirements or "unknown",
                "indoor_start_time": packet.indoor_start_time or "unknown",
            }
            markdown_packet = MarkdownSeedPacket(packet_data)
            packet_file = export_dir / "seed_packets" / f"{packet.id}.md"
            with open(packet_file, "w") as f:
                f.write(markdown_packet.to_markdown())

        # Export genera
        from .genus_model import Genus as MarkdownGenus

        for genus in session.query(Genus).all():
            genus_data = {
                "id": genus.id,
                "variety_name": genus.variety_name,
                "latin_name": genus.latin_name,
            }
            markdown_genus = MarkdownGenus(genus_data)
            genus_file = export_dir / "genera" / f"{genus.id}.md"
            with open(genus_file, "w") as f:
                f.write(markdown_genus.to_markdown())

        # Export plants
        from .plant_model import Plant as MarkdownPlant

        for plant in session.query(Plant).all():
            plant_data = {
                "id": plant.id,
                "variety_name": plant.variety_name,
                "latin_name": plant.latin_name,
                "brand": plant.brand or "unknown",
                "days_to_maturity": plant.days_to_maturity or "unknown",
                "germination_time": plant.germination_time or "unknown",
                "planting_depth": plant.planting_depth or "unknown",
                "spacing": plant.spacing or "unknown",
                "sun_requirements": plant.sun_requirements or "unknown",
                "indoor_start_time": plant.indoor_start_time or "unknown",
                "planting_date": plant.planting_date,
                "seed_packet_id": plant.seed_packet_id or "unknown",
                "genus_id": plant.genus_id or "unknown",
            }
            markdown_plant = MarkdownPlant(plant_data)
            plant_file = export_dir / f"{plant.id}.md"
            with open(plant_file, "w") as f:
                f.write(markdown_plant.to_markdown())

        # Export log entries
        log_entries = session.query(PlantLogEntry).order_by(PlantLogEntry.timestamp).all()
        log_file = export_dir / "logs" / "plant-activity-log.md"

        with open(log_file, "w") as f:
            f.write("# Plant Activity Log\n\n")
            f.write("*Consolidated log of all plant care activities*\n\n---\n")

        for entry in log_entries:
            entry_data = {
                "plant_id": entry.plant_id,
                "event_type": entry.event_type,
                "timestamp": entry.timestamp,
            }
            if entry.event_type == "humidity":
                entry_data["level"] = entry.level
            elif entry.event_type == "water":
                entry_data["amount_ml"] = entry.amount_ml
            elif entry.event_type == "fertilizer":
                entry_data["type"] = entry.fertilizer_type
                entry_data["strength"] = entry.fertilizer_strength
            elif entry.event_type == "note":
                entry_data["text"] = entry.text

            from .plant_log_model import PlantLogEntry as MarkdownPlantLogEntry

            markdown_entry = MarkdownPlantLogEntry(entry_data)
            yaml_content = yaml.dump(
                markdown_entry.to_yaml_entry(), default_flow_style=False, sort_keys=False
            )
            with open(log_file, "a") as f:
                if f.tell() > 0:
                    f.write("\n")
                f.write(f"---\n{yaml_content}...\n")

    finally:
        session.close()
+     try:
        # Export seed packets
        from .seed_packet_model import SeedPacket as MarkdownSeedPacket

        for packet in session.query(SeedPacket).all():
            packet_data = {
                "id": packet.id,
                "variety_name": packet.variety_name,
                "latin_name": packet.latin_name,
                "brand": packet.brand or "unknown",
                "days_to_maturity": packet.days_to_maturity or "unknown",
                "germination_time": packet.germination_time or "unknown",
                "planting_depth": packet.planting_depth or "unknown",
                "spacing": packet.spacing or "unknown",
                "sun_requirements": packet.sun_requirements or "unknown",
                "indoor_start_time": packet.indoor_start_time or "unknown",
            }
            markdown_packet = MarkdownSeedPacket(packet_data)
            packet_file = export_dir / "seed_packets" / f"{packet.id}.md"
            with open(packet_file, "w") as f:
                f.write(markdown_packet.to_markdown())

        # Export genera
        from .genus_model import Genus as MarkdownGenus

        for genus in session.query(Genus).all():
            genus_data = {
                "id": genus.id,
                "variety_name": genus.variety_name,
                "latin_name": genus.latin_name,
            }
            markdown_genus = MarkdownGenus(genus_data)
            genus_file = export_dir / "genera" / f"{genus.id}.md"
            with open(genus_file, "w") as f:
                f.write(markdown_genus.to_markdown())

        # Export plants
        from .plant_model import Plant as MarkdownPlant

        for plant in session.query(Plant).all():
            plant_data = {
                "id": plant.id,
                "variety_name": plant.variety_name,
                "latin_name": plant.latin_name,
                "brand": plant.brand or "unknown",
                "days_to_maturity": plant.days_to_maturity or "unknown",
                "germination_time": plant.germination_time or "unknown",
                "planting_depth": plant.planting_depth or "unknown",
                "spacing": plant.spacing or "unknown",
                "sun_requirements": plant.sun_requirements or "unknown",
                "indoor_start_time": plant.indoor_start_time or "unknown",
                "planting_date": plant.planting_date,
                "seed_packet_id": plant.seed_packet_id or "unknown",
                "genus_id": plant.genus_id or "unknown",
            }
            markdown_plant = MarkdownPlant(plant_data)
            plant_file = export_dir / f"{plant.id}.md"
            with open(plant_file, "w") as f:
                f.write(markdown_plant.to_markdown())

        # Export log entries
        log_entries = session.query(PlantLogEntry).order_by(PlantLogEntry.timestamp).all()
        log_file = export_dir / "logs" / "plant-activity-log.md"

        with open(log_file, "w") as f:
            f.write("# Plant Activity Log\n\n")
            f.write("*Consolidated log of all plant care activities*\n\n---\n")

        for entry in log_entries:
            entry_data = {
                "plant_id": entry.plant_id,
                "event_type": entry.event_type,
                "timestamp": entry.timestamp,
            }
            if entry.event_type == "humidity":
                entry_data["level"] = entry.level
            elif entry.event_type == "water":
                entry_data["amount_ml"] = entry.amount_ml
            elif entry.event_type == "fertilizer":
                entry_data["type"] = entry.fertilizer_type
                entry_data["strength"] = entry.fertilizer_strength
            elif entry.event_type == "note":
                entry_data["text"] = entry.text

            from .plant_log_model import PlantLogEntry as MarkdownPlantLogEntry

            markdown_entry = MarkdownPlantLogEntry(entry_data)
            yaml_content = yaml.dump(
                markdown_entry.to_yaml_entry(), default_flow_style=False, sort_keys=False
            )
            with open(log_file, "a") as f:
                if f.tell() > 0:
                    f.write("\n")
                f.write(f"---\n{yaml_content}...\n")

    except Exception as e:
        # Clean up partially written export directory on failure
        import shutil
        if export_dir.exists():
            shutil.rmtree(export_dir)
        raise  # Re-raise the original exception
    finally:
        session.close()
```

---

## `commands/genus_model.py`

**Lines 28-33**

Add a docstring to the __init__ method to describe its purpose, parameters, and any side effects.

**Suggested fix:**
```diff
-     def __init__(self, data: Dict[str, Any]):
        self.data = data
        self.validate()
        # Generate ID if not present
        if "id" not in self.data:
            self.data["id"] = self.generate_id()
+     def __init__(self, data: Dict[str, Any]):
        """Initialize a Genus instance with data.

        Args:
            data: Dictionary containing genus data.

        Raises:
            ValueError: If required fields are missing or empty.
        """
        self.data = data
        self.validate()
        # Generate ID if not present
        if "id" not in self.data:
            self.data["id"] = self.generate_id()
```

---

## `commands/models/plant.py`

**Lines 62-65**

The generate_id method does not validate the planting_date format when it is non-empty. If planting_date is not in YYYY-MM-DD format, it will raise a ValueError from datetime.strptime with a potentially confusing message. We should catch this exception and raise a more meaningful error.

**Suggested fix:**
```diff
-         if planting_date:
            year = datetime.strptime(planting_date, "%Y-%m-%d").year
        else:
            year = datetime.now(timezone.utc).year

+         if planting_date:
            try:
                year = datetime.strptime(planting_date, "%Y-%m-%d").year
            except ValueError:
                raise ValueError("planting_date must be in YYYY-MM-DD format or empty string")
        else:
            year = datetime.now(timezone.utc).year

```

---

## `commands/models/plant_log.py`

**Lines 0-0**

Timestamp validation has a bug: if timestamp is provided as an empty string, it passes the initial existence check (since key exists) but fails the truthiness check, so validation is skipped. Then the 'timestamp not in data' check fails (since key exists), so no default is set. This results in an empty string being stored, which violates the expected format. Should validate that if timestamp key exists, the value must be a non-empty string in correct format.

**Suggested fix:**
```diff
-         if "timestamp" in data and data["timestamp"]:
            try:
                datetime.strptime(data["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                raise ValueError("timestamp must be in YYYY-MM-DDTHH:MM:SSZ format")

        if "timestamp" not in data:
            data["timestamp"] = datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ")
+         if "timestamp" in data:
            if not data["timestamp"]:
                raise ValueError("timestamp must be a non-empty string")
            try:
                datetime.strptime(data["timestamp"], "%Y-%m-%dT%H:%M:%SZ")
            except ValueError:
                raise ValueError("timestamp must be in YYYY-MM-DDTHH:MM:SSZ format")
        else:
            data["timestamp"] = datetime.now(timezone.utc).strftime(
                "%Y-%m-%dT%H:%M:%SZ")
```

---

## `commands/models/seed_packet.py`

**Lines 0-0**

The `_find_next_sequence` method is prone to race conditions when multiple processes attempt to create seed packets concurrently. Two processes could read the same maximum sequence value and then attempt to insert records with the same ID, leading to primary key violations. Consider using a database sequence or a transaction with locking (e.g., `SELECT ... FOR UPDATE`) to ensure atomicity.

**Suggested fix:**
```diff
-     def _find_next_sequence(self) -> int:
        """
        Find next sequence number by checking existing seed packet records
        """
        from sqlalchemy import select

        from commands.database import get_db

        pattern = "SPKT-%"

        with get_db() as session:
            stmt = select(SeedPacket.id).where(SeedPacket.id.like(pattern))
            results = session.execute(stmt).scalars().all()

            max_seq = 0
            regex_pattern = re.compile(r"SPKT-(\d{3})")

            for packet_id in results:
                match = regex_pattern.match(packet_id)
                if match:
                    seq = int(match.group(1))
                    max_seq = max(max_seq, seq)

            return max_seq + 1
+     def _find_next_sequence(self) -> int:
        """
        Find next sequence number by checking existing seed packet records
        """
        from sqlalchemy import select, func

        from commands.database import get_db

        with get_db() as session:
            # Use database-side aggregation to find max sequence
            stmt = select(func.max(func.cast(func.substring(SeedPacket.id, 7), Integer))).where(
                SeedPacket.id.like('SPKT-%')
            )
            result = session.execute(stmt).scalar()
            max_seq = result or 0
            return max_seq + 1

```

---

**Lines 0-0**

The `create_from_dict` method accepts an optional 'id' field but does not validate its format (expected SPKT-NNN). This could lead to inconsistent ID formats if callers provide malformed values. Consider adding validation to ensure manually provided IDs match the expected pattern.

**Suggested fix:**
```diff
-     @classmethod
+    def create_from_dict(cls, data: dict) -> "SeedPacket":
+        """
+        Create SeedPacket instance from dictionary data
+        """
+        required_fields = ["variety_name", "latin_name"]
+        for field in required_fields:
+            if field not in data or not data[field]:
+                raise ValueError(f"Missing required field: {field}")
+
+        if "id" not in data:
+            instance = cls()
+            data["id"] = instance.generate_id()
+
+        return cls(**data)
+     @classmethod
    def create_from_dict(cls, data: dict) -> "SeedPacket":
        """
        Create SeedPacket instance from dictionary data
        """
        required_fields = ["variety_name", "latin_name"]
        for field in required_fields:
            if field not in data or not data[field]:
                raise ValueError(f"Missing required field: {field}")

        if "id" not in data:
            instance = cls()
            data["id"] = instance.generate_id()
        else:
            # Validate manually provided ID format
            import re
            if not re.match(r'^SPKT-\d{3}$', data["id"]):
                raise ValueError(f"ID must match format SPKT-NNN, got: {data['id']}")

        return cls(**data)
```

---

## `commands/plant_log_model.py`

**Lines 70-72**

The validation for water event only checks for the presence of 'amount_ml' or 'amount', but does not validate their types or values. For example, 'amount_ml' should be a positive number, and 'amount' should be a string that can be normalized by normalize_water_amount. Consider adding validation to ensure data integrity.

---

**Lines 0-0**

Missing return type hint. Should be `-> Path`.

---

## `commands/plant_model.py`

**Lines 0-0**

Add return type annotation for load_seed_packet function. It should return Optional["SeedPacket"].

**Suggested fix:**
```diff
- def load_seed_packet(packet_id: str):
    """Load a seed packet by ID. Returns None if not found."""
    from commands.seed_packet_model import load_from_file, get_seed_packets_dir

    packets_dir = get_seed_packets_dir()
    if not packets_dir.exists():
        return None

    filepath = packets_dir / f"{packet_id}.md"
    if filepath.exists():
        return load_from_file(filepath)
    return None
+ def load_seed_packet(packet_id: str) -> Optional["SeedPacket"]:
    """Load a seed packet by ID. Returns None if not found."""
    from commands.seed_packet_model import load_from_file, get_seed_packets_dir

    packets_dir = get_seed_packets_dir()
    if not packets_dir.exists():
        return None

    filepath = packets_dir / f"{packet_id}.md"
    if filepath.exists():
        return load_from_file(filepath)
    return None
```

---

**Lines 146-147**

Bare except clause catches all exceptions, including system-exiting ones. Should catch specific exceptions like IOError, yaml.YAMLError.

**Suggested fix:**
```diff
-                 except Exception:
                    continue  # Skip unreadable files
+                 except (IOError, yaml.YAMLError):
                    continue  # Skip unreadable or malformed files
```

---

**Lines 86-86**

Add return type annotation -> str

**Suggested fix:**
```diff
- def to_markdown(self) -> str:
+     def to_markdown(self) -> str:
        """Convert plant data to markdown with YAML frontmatter"""
        now = datetime.now(timezone.utc)

        # Set timestamps in ISO 8601 format
        if "created_at" not in self.data:
            self.data["created_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")
        self.data["updated_at"] = now.strftime("%Y-%m-%dT%H:%M:%SZ")

        frontmatter = yaml.dump(self.data, default_flow_style=False, sort_keys=False)
        body = (
            f"# Plant Record for {self.data['variety_name']}\n\n"
            f"*ID: {self.data['id']}*\n\n"
            f"*Created: {now.strftime('%Y-%m-%d')}*"
        )
        return f"---\n{frontmatter}---\n\n{body}"
```

---

**Lines 48-50**

Add return type annotation -> Path

**Suggested fix:**
```diff
- def get_database_dir() -> Path:
    """Get the database directory path."""
    return Path(os.environ.get("PLANT_DATABASE_DIR", "database"))
+ def get_database_dir() -> Path:
    """Get the database directory path."""
    return Path(os.environ.get("PLANT_DATABASE_DIR", "database"))
```

---

**Lines 0-0**

Add return type annotation for load_genus function. It should return Optional["Genus"].

**Suggested fix:**
```diff
- def load_genus(genus_id: str):
    """Load a genus by ID. Returns None if not found."""
    from commands.genus_model import (
        load_from_file as load_genus_from_file,
        get_genera_dir as get_genera_dir_path,
    )

    genera_dir = get_genera_dir_path()
    if not genera_dir.exists():
        return None
    filepath = genera_dir / f"{genus_id}.md"
    if filepath.exists():
        return load_genus_from_file(filepath)
    return None
+ def load_genus(genus_id: str) -> Optional["Genus"]:
    """Load a genus by ID. Returns None if not found."""
    from commands.genus_model import (
        load_from_file as load_genus_from_file,
        get_genera_dir as get_genera_dir_path,
    )

    genera_dir = get_genera_dir_path()
    if not genera_dir.exists():
        return None
    filepath = genera_dir / f"{genus_id}.md"
    if filepath.exists():
        return load_genus_from_file(filepath)
    return None
```

---

## `commands/plant_tracking_cli.py`

**Lines 0-0**

In media_delete_attachment, there's a potential inconsistency risk: if S3 file deletion succeeds (line 2438) but database deletion fails (line 2440), we'll have an orphaned S3 file. Conversely, if database deletion succeeds but S3 deletion fails, we'll have a DB record referencing a deleted file. Consider implementing a transaction-like pattern or compensating transaction to handle partial failures.

**Suggested fix:**
```diff
- def media_delete_attachment(args, db=None):
    """Delete media attachment."""
    if db is None:
        db = _get_db()

    if not db or not SERVICE_AVAILABLE:
        print("Error: Media attachments require database service")
        return

    try:
        from plant_service.service_layer.s3_service import S3Service

        with create_unit_of_work() as uow:
            media_attachment = uow.media_attachments.get_media_attachment(
                args.media_id
            )
            if not media_attachment:
                print(f"Media attachment not found: {args.media_id}")
                return

            s3_service = S3Service()
            s3_service.delete_file(media_attachment.s3_key)

            success = uow.media_attachments.delete_media_attachment(args.media_id)
            if success:
                uow.commit()
                print(f"✓ Media attachment {args.media_id} deleted successfully")
            else:
                print(f"Failed to delete media attachment {args.media_id}")
    except Exception as e:
        print(f"Error deleting media attachment: {e}")
+ def media_delete_attachment(args, db=None):
    """Delete media attachment."""
    if db is None:
        db = _get_db()

    if not db or not SERVICE_AVAILABLE:
        print("Error: Media attachments require database service")
        return

    try:
        from plant_service.service_layer.s3_service import S3Service

        with create_unit_of_work() as uow:
            media_attachment = uow.media_attachments.get_media_attachment(
                args.media_id
            )
            if not media_attachment:
                print(f"Media attachment not found: {args.media_id}")
                return

            s3_service = S3Service()
            # Delete from database first
            success = uow.media_attachments.delete_media_attachment(args.media_id)
            if not success:
                print(f"Failed to delete media attachment {args.media_id} from database")
                return
            
            # Then delete from S3
            try:
                s3_service.delete_file(media_attachment.s3_key)
                uow.commit()
                print(f"✓ Media attachment {args.media_id} deleted successfully")
            except Exception as s3_error:
                # If S3 deletion fails, we have a problem - record exists in DB but file is gone
                # In a real system, we might want to retry or alert admin
                print(f"Warning: Database record deleted but S3 deletion failed: {s3_error}")
                print(f"Media attachment {args.media_id} record removed from DB but file may still exist in S3")
                uow.commit()  # Commit the DB deletion anyway
    except Exception as e:
        print(f"Error deleting media attachment: {e}")
        # Note: If we get here, the uow context manager will rollback on exception

```

---

**Lines 0-0**

The code contains numerous triple conditional blocks (service package, original models, markdown) for database operations, causing significant duplication. This pattern appears ~38 times throughout the file, reducing maintainability and increasing risk of inconsistencies when modifying logic. Consider extracting this into a helper function or using a strategy pattern to handle the different backends.

**Suggested fix:**
```diff
- if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                packets = list(uow.seed_packets.list_seed_packets())
        except Exception:
            # Fallback to original models if service fails
            if db:
                from .models import SeedPacket

                packets = SeedPacket.list_all()
            else:
                packets = markdown_list_all()
    elif db:
        # Fallback to original models
        from .models import SeedPacket

        packets = SeedPacket.list_all()
    else:
        # Markdown fallback
        packets = markdown_list_all()
+ # Consider extracting this pattern into a helper function like:
# def get_seed_packets(db):
#     if db and SERVICE_AVAILABLE:
#         try:
#             with create_unit_of_work() as uow:
#                 return list(uow.seed_packets.list_seed_packets())
#         except Exception:
#             pass  # Fall through to next option
#     if db:
#         from .models import SeedPacket
#         return SeedPacket.list_all()
#     return markdown_list_all()
```

---

**Lines 0-0**

The log_humidity function accepts an integer level via --level but lacks validation to ensure the value is within the required 1-10 range. This could allow invalid data to be stored. Consider adding validation like: if not 1 <= args.level <= 10: print('Error: Humidity level must be between 1 and 10'); return

**Suggested fix:**
```diff
- log_humidity_parser.add_argument(
        "--level", "-l", type=int, required=True, help="Humidity level (1-10)"
    )

...

    entry_data = {
        "plant_id": args.plant_id,
        "event_type": "humidity",
        "level": args.level,
    }
+ log_humidity_parser.add_argument(
        "--level", "-l", type=int, required=True, help="Humidity level (1-10)"
    )

...

    # Validate humidity level is in range 1-10
    if not 1 <= args.level <= 10:
        print(f"✗ Error: Humidity level must be between 1 and 10, got {args.level}")
        return

    entry_data = {
        "plant_id": args.plant_id,
        "event_type": "humidity",
        "level": args.level,
    }
```

---

**Lines 0-0**

The create_plant function is excessively long (over 200 lines) with nested conditionals and repeated patterns, impairing readability and making it difficult to test or modify. Consider breaking this down into smaller, focused functions: (1) genus lookup/resolution, (2) seed packet handling, (3) data collection, (4) persistence operations. Each major phase could be extracted into its own helper function.

**Suggested fix:**
```diff
- def create_plant(args, db=None, database_dir=None, packets_dir=None, genera_dir=None):
    """Create a new plant record through interactive prompts with genus lookup."""
    from .genus_model import find_by_variety_name as markdown_find_by_variety_name

    # Backward compatibility: use module-level vars if not provided
    if database_dir is None:
        database_dir = getattr(args, "database_dir", None) or DATABASE_DIR
    if packets_dir is None:
        packets_dir = getattr(args, "packets_dir", None) or PACKETS_DIR
    if genera_dir is None:
        genera_dir = getattr(args, "genera_dir", None) or GENERA_DIR

    print("=== Create New Plant Record ===")
    print(
        "Fields needed for the label are required; record-keeping fields are optional."
    )
    print()

    plant_data = {}

    # Phase 1: Ask for variety name to look up genus
    print("--- Variety identification (used for label & genus lookup) ---")
    _prompt_field("variety_name", "Variety name (e.g., Yellow Habanero)", plant_data)

    # Try exact match by variety name first
    genus_id = None
    genus_latin = None
    genus_variety = None

    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                # Get all genera and find matching variety name
                for genus in uow.genera.list_genera():
                    if genus.variety_name == plant_data["variety_name"]:
                        genus_id = genus.id
                        genus_latin = genus.latin_name
                        genus_variety = genus.variety_name
                        break
        except Exception:
            pass
    elif db:
        # Fallback to original models if service not available
        from .models import Genus

        existing_genus = Genus.find_by_variety_name(plant_data["variety_name"])
        if existing_genus:
            genus_id = existing_genus.id
            genus_latin = existing_genus.latin_name
            genus_variety = existing_genus.variety_name
    else:
        # Markdown fallback
        existing_genus = markdown_find_by_variety_name(plant_data["variety_name"])
        if existing_genus:
            genus_id = existing_genus.data["id"]
            genus_latin = existing_genus.data["latin_name"]
            genus_variety = existing_genus.data["variety_name"]

    if genus_id:
        print(
            f"\n✓ Found genus: {genus_id} - {genus_variety}"
        )
        print(f"  Latin name: {genus_latin}")
        plant_data["latin_name"] = genus_latin
        plant_data["genus_id"] = genus_id
        print("  Latin name auto-resolved from genus database.")
    else:
        # Try fuzzy search automatically
        matched_genus_id = _fuzzy_search_genus(plant_data["variety_name"], db)
        if matched_genus_id:
            if db and SERVICE_AVAILABLE:
                try:
                    with create_unit_of_work() as uow:
                        # Find the genus by ID
                        for genus in uow.genera.list_genera():
                            if genus.id == matched_genus_id:
                                print(
                                    f"\n✓ Fuzzy match found: {genus.id} - {genus.variety_name}"
                                )
                                print(f"  Latin name: {genus.latin_name}")
                                confirm = input("Use this genus? (Y/n): ").strip().lower()
                                if confirm != "n":
                                    plant_data["latin_name"] = genus.latin_name
                                    plant_data["genus_id"] = genus.id
                                    print("  Latin name auto-resolved from genus database.")
                                break
                except Exception:
                    pass
            elif db:
                # Fallback to original models
                from .models import Genus

                all_genera = Genus.list_all()
                matched_genus = next(
                    (g for g in all_genera if g.id == matched_genus_id), None
                )
                if matched_genus:
                    print(
                        f"\n✓ Fuzzy match found: {matched_genus.id} - {matched_genus.variety_name}"
                    )
                    print(f"  Latin name: {matched_genus.latin_name}")
                    confirm = input("Use this genus? (Y/n): ").strip().lower()
                    if confirm != "n":
                        plant_data["latin_name"] = matched_genus.latin_name
                        plant_data["genus_id"] = matched_genus.id
                        print("  Latin name auto-resolved from genus database.")
            else:
                # Markdown fallback
                all_genera = markdown_list_all()
                matched_genus = next(
                    (g for g in all_genera if g.data["id"] == matched_genus_id), None
                )
                if matched_genus:
                    print(
                        f"\n✓ Fuzzy match found: {matched_genus.data['id']} - {matched_genus.data['variety_name']}"
                    )
                    print(f"  Latin name: {matched_genus.data['latin_name']}")
                    confirm = input("Use this genus? (Y/n): ").strip().lower()
                    if confirm != "n":
                        plant_data["latin_name"] = matched_genus.data["latin_name"]
                        plant_data["genus_id"] = matched_genus.data["id"]
                        print("  Latin name auto-resolved from genus database.")

        # If still no match, ask for Latin name
        if "latin_name" not in plant_data:
            _prompt_field(
                "latin_name", "Latin name (e.g., Capsicum chinense)", plant_data
            )

            # Offer to create new genus entry
            create_genus = (
                input("Create a new genus entry for this variety? (y/N): ")
                .strip()
                .lower()
            )
            if create_genus == "y":
                if db and SERVICE_AVAILABLE:
                    try:
                        genus_data = {
                            "variety_name": plant_data["variety_name"],
                            "latin_name": plant_data["latin_name"],
                        }
                        with create_unit_of_work() as uow:
                            genus = uow.genera.create_genus(genus_data)
                            plant_data["genus_id"] = genus.id
                            print(f"\n✓ Genus created: {genus.id}")
                    except Exception as e:
                        print(f"Error creating genus: {e}")
                        plant_data["genus_id"] = "unknown"
                elif db:
                    # Fallback to original models
                    from .models import Genus

                    genus_data = {
                        "variety_name": plant_data["variety_name"],
                        "latin_name": plant_data["latin_name"],
                    }
                    genus = Genus.create_from_dict(genus_data)
                    with db.get_db() as session:
                        session.add(genus)
                        session.commit()
                    plant_data["genus_id"] = genus.id
                    # Markdown backup
                    from .genus_model import Genus as MarkdownGenus
                    backup_data = genus_data.copy()
                    backup_data["id"] = genus.id
                    markdown_genus = MarkdownGenus(backup_data)
                    filepath = genera_dir / f"{genus.id}.md"
                    _write_markdown_backup(filepath, markdown_genus)
                else:
                    # Markdown fallback
                    from .genus_model import Genus

                    genus_data = {
                        "variety_name": plant_data["variety_name"],
                        "latin_name": plant_data["latin_name"],
                    }
                    genus = Genus(genus_data)
                    genera_dir.mkdir(parents=True, exist_ok=True)
                    filepath = genera_dir / f"{genus.data['id']}.md"
                    _write_markdown_backup(filepath, genus)
                    plant_data["genus_id"] = genus.data["id"]
            else:
                plant_data["genus_id"] = "unknown"

    # Phase 2: Seed packet handling
    print()
    print("--- Seed packet ---")
    packet_matched = False

    if db and SERVICE_AVAILABLE:
        try:
            with create_unit_of_work() as uow:
                # Find matching seed packet
                for packet in uow.seed_packets.list_seed_packets():
                    if (
                        packet.variety_name == plant_data["variety_name"]
                        and packet.latin_name == plant_data["latin_name"]
                    ):
                        print(
                            f"\n✓ Found seed packet: {packet.id} - {packet.variety_name}"
                        )
                        plant_data["seed_packet_id"] = packet.id
                        packet_matched = True
                        break
        except Exception:
            pass
    elif db:
        # Fallback to original models
        from .models import SeedPacket

        spkt = SeedPacket.find_matching(
            plant_data["variety_name"], plant_data["latin_name"]
        )
        if spkt:
            print(
                f"\n✓ Found seed packet: {spkt.id} - {spkt.variety_name}"
            )
            plant_data["seed_packet_id"] = spkt.id
            packet_matched = True
    else:
        # Markdown fallback
        spkt = markdown_find_matching(
            plant_data["variety_name"], plant_data["latin_name"]
        )
        if spkt:
            print(
                f"\n✓ Found seed packet: {spkt.data['id']} - {spkt.data['variety_name']}"
            )
            plant_data["seed_packet_id"] = spkt.data["id"]
            packet_matched = True

    if not packet_matched:
        choice = _prompt_packet_choice(plant_data)
        if choice == "create":
            if db and SERVICE_AVAILABLE:
                try:
                    packet_id = _create_packet_inline(plant_data, db, packets_dir)
                    plant_data["seed_packet_id"] = packet_id
                except Exception as e:
                    print(f"Error creating seed packet: {e}")
                    plant_data["seed_packet_id"] = "unknown"
            elif db:
                # Fallback to original models
                packet_id = _create_packet_inline(plant_data, db, packets_dir)
                plant_data["seed_packet_id"] = packet_id
            else:
                # Markdown fallback
                _prompt_record_fields(plant_data)
                plant_data["seed_packet_id"] = "unknown"
        elif choice == "select":
            if db and SERVICE_AVAILABLE:
                try:
                    selected = _select_existing_packet(db)
                    plant_data["seed_packet_id"] = selected if selected else "unknown"
                except Exception:
                    plant_data["seed_packet_id"] = "unknown"
            elif db:
                # Fallback to original models
                selected = _select_existing_packet(db)
                plant_data["seed_packet_id"] = selected if selected else "unknown"
            else:
                # Markdown fallback
                selected = _select_existing_packet(db)
                plant_data["seed_packet_id"] = selected if selected else "unknown"
        else:
            _prompt_record_fields(plant_data)
            plant_data["seed_packet_id"] = "unknown"

    # Phase 3: Plant-specific required field (always asked)
    print()
    print("--- Plant-specific field ---")
    _prompt_field("planting_date", "Planting date (YYYY-MM-DD)", plant_data)

    try:
        plant_id = None
        if db and SERVICE_AVAILABLE:
            try:
                with create_unit_of_work() as uow:
                    plant = uow.plants.create_plant(plant_data)
                    plant_id = plant.id
            except ValidationException as e:
                print(f"\n✗ Validation error: {e}")
                sys.exit(1)
            except PlantTrackingServiceException as e:
                print(f"\n✗ Service error: {e}")
                sys.exit(1)
            except Exception as e:
                print(f"\n✗ Error creating plant record: {e}")
                sys.exit(1)
        elif db:
            # Fallback to original models
            from .models import Plant

            plant = Plant.create_from_dict(plant_data)
            with db.get_db() as session:
                session.add(plant)
                session.commit()

            plant_id = plant.id

            # Markdown backup
            backup_data = {
                "id": plant.id,
                "variety_name": plant.variety_name,
                "latin_name": plant.latin_name,
                "planting_date": plant.planting_date,
                "brand": plant.brand or "unknown",
                "days_to_maturity": plant.days_to_maturity or "unknown",
                "germination_time": plant.germination_time or "unknown",
                "planting_depth": plant.planting_depth or "unknown",
                "spacing": plant.spacing or "unknown",
                "sun_requirements": plant.sun_requirements or "unknown",
                "indoor_start_time": plant.indoor_start_time or "unknown",
                "seed_packet_id": plant.seed_packet_id or "unknown",
                "genus_id": plant.genus_id or "unknown",
            }
            markdown_plant = MarkdownPlant(backup_data)
            filepath = database_dir / f"{plant.id}.md"
            _write_markdown_backup(filepath, markdown_plant)
        else:
            # Fallback to Markdown-only mode
            plant = MarkdownPlant(plant_data)
            filepath = database_dir / f"{plant.data['id']}.md"
            _write_markdown_backup(filepath, plant)
            plant_id = plant.data["id"]

        genus_id = plant_data.get("genus_id", "unknown")
        if not db:
            plant_id = plant.data["id"]
            genus_id = plant.data.get("genus_id", "unknown")

        print("\n✓ Plant record created successfully!")
        print(f"ID: {plant_id}")
        if genus_id and genus_id != "unknown":
            print(f"Genus: {genus_id}")
        print(f"Saved to: {filepath}")
        print("\nNext steps:")
        print(
            f"  1. Generate/print label: plant-tracking print-label {plant_id}"
        )
        print(
            f"  2. Generate image only: plant-tracking print-label {plant_id} --no-print"
        )
        print(
            f"  3. Use 50x70mm format: plant-tracking print-label {plant_id} --format 50x70mm"
        )

    except Exception as e:
        print(f"\n✗ Error creating plant record: {e}")
        sys.exit(1)
+ # Consider refactoring into smaller functions like:
# def _resolve_genus(plant_data, db):
#     # Handle genus lookup/fuzzy search/creation
#     pass
# 
# def _handle_seed_packet(plant_data, db, packets_dir):
#     # Handle seed packet matching/creation/selection
#     pass
# 
# def _collect_plant_data(plant_data):
#     # Handle interactive prompts for plant data
#     pass
# 
# def _persist_plant(plant_data, db, database_dir, packets_dir, genera_dir):
#     # Handle saving to appropriate backend
#     pass

```

---

## `commands/printer.py`

**Lines 5-12**

Remove unused imports 'glob' and 'os'. Add import for typing utilities (Dict, List, Any, Optional) for type hints.

**Suggested fix:**
```diff
- import glob
import os
import subprocess
import sys
import time
from pathlib import Path
from .label_generator import create_label
from .label_format import LabelFormatEnum, is_format_supported, get_label_format
+ import subprocess
import sys
from typing import Any, Dict, List, Optional
import time
from pathlib import Path
from .label_generator import create_label
from .label_format import LabelFormatEnum, is_format_supported, get_label_format
```

---

**Lines 45-50**

Replace bare 'except Exception:' with specific exception handling for USB errors. Add logging of the exception for debugging purposes.

**Suggested fix:**
```diff
-                 # Try to get serial number (may fail due to permissions)
                serial = ""
                try:
                    serial = usb.util.get_string(dev, dev.iSerialNumber) or ""
                except Exception:
                    pass
+                 # Try to get serial number (may fail due to permissions)
                serial = ""
                try:
                    serial = usb.util.get_string(dev, dev.iSerialNumber) or ""
                except usb.core.USBError as e:
                    # Log USB errors for debugging but continue
                    pass  # Could log: logger.debug(f"Could not get serial number: {e}")
                except Exception as e:
                    # Handle other unexpected exceptions
                    pass
```

---

**Lines 0-0**

Replace default media option with explicit check for supported print formats. Raise an error if the format is not supported for printing.

**Suggested fix:**
```diff
- # Map format to CUPS media option
format_to_media = {"40x30mm": "w40h30", "50x70mm": "w50h70"}

media_option = format_to_media.get(format_str, "w40h30")  # default to 40x30mm
+ # Map format to CUPS media option
format_to_media = {
    "40x30mm": "w40h30",
    "50x70mm": "w50h70",
}

if format_str not in format_to_media:
    print(f"Error: Printing not supported for format '{format_str}'. Supported formats: {list(format_to_media.keys())}")
    return False

media_option = format_to_media[format_str]
```

---

**Lines 161-167**

Add comment clarifying that the queue name is assumed to match the printer model and may need adjustment.

**Suggested fix:**
```diff
- # Use lp command with appropriate media option based on format
# Extract model from selected description, default to M120
model = selected.get("model", "M120")
# Normalize model name to queue name (e.g., "M120/M220" -> "M120")
if "/" in model:
    model = model.split("/")[0]
queue_name = model  # assuming queue name matches model; adjust if needed
+ # Use lp command with appropriate media option based on format
# Extract model from selected description, default to M120
model = selected.get("model", "M120")
# Normalize model name to queue name (e.g., "M120/M220" -> "M120")
if "/" in model:
    model = model.split("/")[0]
queue_name = model  # Note: This assumes the CUPS queue name matches the printer model (e.g., "M120").
                    # If your queue name is different, you may need to adjust this code or set up an alias in CUPS.
```

---

**Lines 0-0**

Add type hints to public functions for better code clarity and adherence to PEP 484. For example: _find_usb_phomemo_devices() -> List[Dict[str, Any]], _select_printer(devices: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]. Also consider adding type hints to main() -> int.

**Suggested fix:**
```diff
- def _find_usb_phomemo_devices():
    """Find Phomemo USB printers using pyusb.

    Returns a list of dicts with keys: model, bus, address, product_id, description
    """
+ def _find_usb_phomemo_devices() -> List[Dict[str, Any]]:
    """Find Phomemo USB printers using pyusb.

    Returns a list of dicts with keys: model, bus, address, product_id, description
    """
    try:
        import usb.core
        import usb.util
    except ModuleNotFoundError:
        print("Error: python3-usb (pyusb) is not installed.")
        print("Install with: pip install pyusb")
        return []

    devices: List[Dict[str, Any]] = []
    try:
        for vendor_id in PHOMEMO_VENDOR_IDS:
            for dev in usb.core.find(find_all=True, idVendor=vendor_id):
                # Get model from product ID
                product_id = dev.idProduct
                if product_id == 0xB002:
                    model = "M02"
                elif product_id == 0x8760:
                    model = "M110"
                elif product_id == 0x5740:
                    model = "M120/M220"
                else:
                    model = f"Unknown (0x{product_id:04x}"

                # Try to get serial number (may fail due to permissions)
                serial = ""
                try:
                    serial = usb.util.get_string(dev, dev.iSerialNumber) or ""
                except usb.core.USBError as e:
                    # Log USB errors for debugging but continue
                    pass  # Could log: logger.debug(f"Could not get serial number: {e}")
                except Exception as e:
                    # Handle other unexpected exceptions
                    pass

                description = (
                    f"Phomemo {model} (bus {dev.bus:03d}, dev {dev.address:03d})"
                )
                if serial:
                    description += f" serial={serial}"

                devices.append(
                    {
                        "model": model,
                        "bus": dev.bus,
                        "address": dev.address,
                        "product_id": product_id,
                        "serial": serial,
                        "description": description,
                    }
                )
    except Exception as e:
        print(f"Error scanning USB devices: {e}")
        print("You may need to run this command with appropriate USB permissions.")
        print("Run: newgrp lp   (or log out and back in)")

    return devices
```

---

**Lines 0-0**

Add type hints to _select_printer function.

**Suggested fix:**
```diff
- def _select_printer(devices):
    """Present available printers to the user and return the selected one."""
    print(f"\nFound {len(devices)} Phomemo USB printer(s):\n")
    for i, dev in enumerate(devices, 1):
        print(f"  {i}. {dev['description']}")
    print()

    choice = input("Select printer (1-{}): ".format(len(devices))).strip()
    if not choice:
        if len(devices) == 1:
            return devices[0]
        return None

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(devices):
            return devices[idx]
    except ValueError:
        pass

    print("Invalid selection.")
    return None
+ def _select_printer(devices: List[Dict[str, Any]]) -> Optional[Dict[str, Any]]:
    """Present available printers to the user and return the selected one."""
    print(f"\nFound {len(devices)} Phomemo USB printer(s):\n")
    for i, dev in enumerate(devices, 1):
        print(f"  {i}. {dev['description']}")
    print()

    choice = input("Select printer (1-{}): ".format(len(devices))).strip()
    if not choice:
        if len(devices) == 1:
            return devices[0]
        return None

    try:
        idx = int(choice) - 1
        if 0 <= idx < len(devices):
            return devices[idx]
    except ValueError:
        pass

    print("Invalid selection.")
    return None
```

---

**Lines 100-104**

Add type hints to print_label function.

**Suggested fix:**
```diff
- def print_label(
    plant_id_or_path: str,
    format_str: str = LabelFormatEnum.FORMAT_40X30MM.value,
    no_print: bool = False,
) -> bool:
+ def print_label(
    plant_id_or_path: str,
    format_str: str = LabelFormatEnum.FORMAT_40X30MM.value,
    no_print: bool = False,
) -> bool:
    """
    Print a label for a plant

    Args:
        plant_id_or_path: Plant ID or path to label PNG file
        format_str: Label format identifier (e.g., "40x30mm", "50x70mm")
        no_print: If True, only generate label image without printing

    Returns:
        True if operation was successful, False otherwise
    """
    # Determine if input is a plant ID or file path
    input_path: Path = Path(plant_id_or_path)

    if input_path.exists() and input_path.is_file():
        # Direct file path provided
        label_path: Path = input_path
        # Extract plant ID from filename if possible (for logging)
        plant_id: str = input_path.stem.replace("_label", "")
    else:
        # Treat as plant ID, generate label first
        plant_id = plant_id_or_path

        # Validate format
        if not is_format_supported(format_str):
            print(f"Error: Unsupported label format '{format_str}'")
            print(f"Supported formats: {[f.value for f in LabelFormatEnum]}")
            return False

        try:
            label_path = create_label(plant_id, format_str=format_str)
        except Exception as e:
            print(f"Error generating label for printing: {e}")
            return False

    if not label_path or not label_path.exists():
        print(f"Label file not found: {label_path}")
        return False

    # If no_print flag is set, we're done after generating the label
    if no_print:
        print(f"Label generated (no print): {label_path}")
        return True

    # Discover and select USB printer (only needed when actually printing)
    devices: List[Dict[str, Any]] = _find_usb_phomemo_devices()
    if not devices:
        print("Error: No Phomemo USB printer found.")
        print("Connect the printer via USB and ensure it is powered on.")
        return False

    selected: Optional[Dict[str, Any]] = _select_printer(devices)
    if selected is None:
        print("No printer selected. Aborting.")
        return False

    # Use lp command with appropriate media option based on format
    # Extract model from selected description, default to M120
    model: str = selected.get("model", "M120")
    # Normalize model name to queue name (e.g., "M120/M220" -> "M120")
    if "/" in model:
        model = model.split("/")[0]
    queue_name: str = model  # Note: This assumes the CUPS queue name matches the printer model (e.g., "M120").
                    # If your queue name is different, you may need to adjust this code or set up an alias in CUPS.

    # Map format to CUPS media option
    format_to_media: Dict[str, str] = {
        "40x30mm": "w40h30",
        "50x70mm": "w50h70",
    }

    if format_str not in format_to_media:
        print(f"Error: Printing not supported for format '{format_str}'. Supported formats: {list(format_to_media.keys())}")
        return False

    media_option: str = format_to_media[format_str]

    try:
        # Print using lp with media option based on format
        result = subprocess.run(
            ["lp", "-d", queue_name, "-o", f"media={media_option}", str(label_path)],
            capture_output=True,
            text=False,
        )

        if result.returncode != 0:
            stderr = (
                result.stderr.decode("utf-8", errors="replace")
                if result.stderr
                else "Unknown error"
            )
            print(f"Printing failed: {stderr}")
            return False

        print(f"\u2713 Label printed via lp: {label_path}")
        return True

    except FileNotFoundError:
        print(f"Error: lp command not found. Ensure CUPS is installed.")
        return False
    except Exception as e:
        print(f"Error during printing: {e}")
        return False
```

---

## `commands/seed_packet_model.py`

**Lines 13-23**

Unused constant SEED_PACKET_FIELDS. Consider removing it if not used elsewhere, or use it for validation.

---

**Lines 36-40**

Missing docstring for __init__ method. Add a docstring describing the parameters and behavior.

---

**Lines 0-0**

Missing return type annotation for validate method. Add -> None.

---

**Lines 71-71**

Pattern r"SPKT-(\d{3})" only matches exactly three digits, which will fail for sequences >= 1000. Consider using r"SPKT-(\d+)" to match one or more digits, or enforce a limit.

---

**Lines 90-91**

Broad exception handling (Exception) may hide unexpected errors. Catch specific exceptions like ValueError, yaml.YAMLError, and OSError instead.

---

**Lines 90-91**

Broad exception handling (Exception) may hide unexpected errors. Catch specific exceptions like ValueError, yaml.YAMLError, and OSError instead.

---

**Lines 147-149**

Loaded YAML data may not be a dictionary (e.g., empty file yields None). Add a check to ensure data is a dict before passing to SeedPacket constructor.

---

## `frontend/src/api/plantTrackingAPI.ts`

**Lines 0-0**

There is an extra semicolon after the closing brace of the intersection type. This causes a TypeScript syntax error and will prevent compilation. Remove the semicolon on the line after '};'.

**Suggested fix:**
```diff
- export type healthCheckHealthGetResponseSuccess = (healthCheckHealthGetResponse200) & {
  headers: Headers;
};

export type healthCheckHealthGetResponse = (healthCheckHealthGetResponseSuccess)
+ export type healthCheckHealthGetResponseSuccess = (healthCheckHealthGetResponse200) & {
  headers: Headers;
};

export type healthCheckHealthGetResponse = (healthCheckHealthGetResponseSuccess)
```

---

**Lines 40-42**

There is an extra semicolon after the closing brace of the intersection type. This causes a TypeScript syntax error and will prevent compilation. Remove the semicolon on the line after '};'.

**Suggested fix:**
```diff
- export type healthCheckHealthGetResponseSuccess = (healthCheckHealthGetResponse200) & {
  headers: Headers;
};
+ export type healthCheckHealthGetResponseSuccess = (healthCheckHealthGetResponse200) & {
  headers: Headers;
};
```

---

**Lines 0-0**

The async API functions (e.g., healthCheckHealthGet, rootGet, createMediaAttachmentApiMediaMediaAttachmentsPost) lack error handling for network errors or non-JSON responses. If fetch fails or res.text() throws, the promise will reject without being caught, potentially causing uncaught promise rejections. Consider wrapping the fetch call in a try/catch block and handling errors appropriately.

**Suggested fix:**
```diff
- export const healthCheckHealthGet = async ( options?: RequestInit): Promise<healthCheckHealthGetResponse> => {

  const res = await fetch(getHealthCheckHealthGetUrl(),
  {
    ...options,
    method: 'GET'


  })


  const body = [204, 205, 304].includes(res.status) ? null : await res.text();

  const data: healthCheckHealthGetResponse['data'] = body ? JSON.parse(body) : {}
  return { data, status: res.status, headers: res.headers } as healthCheckHealthGetResponse
}
+ export const healthCheckHealthGet = async ( options?: RequestInit): Promise<healthCheckHealthGetResponse> => {
  try {
    const res = await fetch(getHealthCheckHealthGetUrl(), {
      ...options,
      method: 'GET'
    })

    const body = [204, 205, 304].includes(res.status) ? null : await res.text();

    const data: healthCheckHealthGetResponse['data'] = body ? JSON.parse(body) : {}
    return { data, status: res.status, headers: res.headers } as healthCheckHealthGetResponse
  } catch (error) {
    // Handle network errors or JSON parsing errors
    console.error('API call failed:', error)
    throw new Error(`Failed to fetch health check: ${error instanceof Error ? error.message : String(error)}`)
  }
}
```

---

**Lines 84-86**

Remove the extra semicolon on the line after the closing brace of the intersection type. This invalid TypeScript syntax will cause a compilation error. This occurs multiple times in the file for each response type definition (e.g., rootGetResponseSuccess, getPlantsNeedingCareApiPlantsCareNeededGetResponseSuccess, etc.).

**Suggested fix:**
```diff
- export type rootGetResponseSuccess = (rootGetResponse200) & {
  headers: Headers;
};
+ export type rootGetResponseSuccess = (rootGetResponse200) & {
  headers: Headers;
};
```

---

**Lines 43-43**

Remove the line containing only a semicolon. This invalid TypeScript syntax will cause a compilation error. This same error occurs multiple times in the file after each intersection type definition.

**Suggested fix:**
```diff
- ;
+ };


export type healthCheckHealthGetResponse = (healthCheckHealthGetResponseSuccess)
```

---

**Lines 0-0**

Remove the line containing only a semicolon after the intersection type definition. This invalid TypeScript syntax will cause compilation errors.

**Suggested fix:**
```diff
- };
;

export type healthCheckHealthGetResponse = (healthCheckHealthGetResponseSuccess)
+ };


export type healthCheckHealthGetResponse = (healthCheckHealthGetResponseSuccess)
```

---

**Lines 43-43**

Remove the line containing only a semicolon after the intersection type definition. This invalid TypeScript syntax will cause a compilation error. This same error occurs multiple times in the file after each intersection type definition.

**Suggested fix:**
```diff
- ;
+ };


export type healthCheckHealthGetResponse = (healthCheckHealthGetResponseSuccess)
```

---

**Lines 52-52**

Hardcoded relative URL without base URL configuration. This assumes the frontend and backend are on the same origin and port, which may not be true in all deployment environments. Consider using a configurable base URL (e.g., from environment variables) to make the API client more flexible. The same issue exists in all URL functions in this file.

**Suggested fix:**
```diff
- return `/health`
+ return `${import.meta.env.VITE_API_BASE_URL || ''}/health`
```

---

**Lines 0-0**

All async API functions in this file lack error handling for network errors or non-JSON responses. If fetch fails or res.text()/JSON.parse() throws, the promise will reject without being caught, potentially causing uncaught promise rejections. Consider creating a wrapper function for API calls that handles errors consistently, or add try/catch blocks to each function.

**Suggested fix:**
```diff
- export const healthCheckHealthGet = async ( options?: RequestInit): Promise<healthCheckHealthGetResponse> => {

  const res = await fetch(getHealthCheckHealthGetUrl(),
  {
    ...options,
    method: 'GET'


  })


  const body = [204, 205, 304].includes(res.status) ? null : await res.text();

  const data: healthCheckHealthGetResponse['data'] = body ? JSON.parse(body) : {}
  return { data, status: res.status, headers: res.headers } as healthCheckHealthGetResponse
}
+ export const healthCheckHealthGet = async ( options?: RequestInit): Promise<healthCheckHealthGetResponse> => {
  try {
    const res = await fetch(getHealthCheckHealthGetUrl(), {
      ...options,
      method: 'GET'
    })

    if (!res.ok) {
      // Handle HTTP error statuses (4xx, 5xx)
      const errorBody = await res.text();
      throw new Error(`HTTP ${res.status}: ${errorBody || res.statusText}`)
    }

    const body = [204, 205, 304].includes(res.status) ? null : await res.text();

    const data: healthCheckHealthGetResponse['data'] = body ? JSON.parse(body) : {}
    return { data, status: res.status, headers: res.headers } as healthCheckHealthGetResponse
  } catch (error) {
    // Handle network errors, HTTP errors, or JSON parsing errors
    console.error('API call failed:', error)
    throw new Error(`Failed to fetch health check: ${error instanceof Error ? error.message : String(error)}`)
  }
}
```

---

## `knowledge/ui-design/ui-static-mocks/plant-tracking-app.html`

**Lines 1269-1274**

The saveEntry function relies on the global 'event' variable without explicitly declaring it as a parameter. This creates an implicit dependency on the event context and will cause a ReferenceError if the function is ever called outside of an inline onclick handler (e.g., via addEventListener). The function should accept the event as an explicit parameter to make the dependency clear and ensure proper functionality in all contexts.

**Suggested fix:**
```diff
- function saveEntry(summary) {
    showToast('✓ ' + summary);
    const formEl = event.target.closest('.expand-form');
    const type = formEl.id.replace('form-', '');
    toggleForm(type);
}
+ function saveEntry(event, summary) {
    showToast('✓ ' + summary);
    const formEl = event.target.closest('.expand-form');
    const type = formEl.id.replace('form-', '');
    toggleForm(type);
}
```

---

**Lines 243-243**

Button contains only an emoji (⚙️) without accessible text or ARIA label, making it inaccessible to screen reader users. Consider adding an aria-label or visually hidden text to describe the button's purpose (e.g., 'Settings').

**Suggested fix:**
```diff
- <button style="font-size:20px;color:var(--n-500);background:none;border:none;cursor:pointer;">⚙️</button>
+ <button style="font-size:20px;color:var(--n-500);background:none;border:none;cursor:pointer;" aria-label="Settings">⚙️</button>
```

---

**Lines 620-620**

Button contains only a left arrow (←) without accessible text or ARIA label, making it inaccessible to screen reader users. Consider adding an aria-label or visually hidden text to describe the button's purpose (e.g., 'Go back').

**Suggested fix:**
```diff
- <button onclick="goBackFrom('more','home')" style="color:var(--n-500);font-size:18px;background:none;border:none;cursor:pointer;">←</button>
+ <button onclick="goBackFrom('more','home')" style="color:var(--n-500);font-size:18px;background:none;border:none;cursor:pointer;" aria-label="Go back">←</button>
```

---

**Lines 8-8**

The HTML file embeds CSS and JavaScript directly, which mixes concerns and may reduce maintainability as the mockup grows. Consider extracting CSS to an external file (e.g., styles.css) and JavaScript to an external file (e.g., script.js) for better separation of concerns and easier collaboration.

**Suggested fix:**
```diff
-     <style>
+     <!-- Consider moving CSS to an external file (e.g., styles.css) and JavaScript to an external file (e.g., script.js) -->
    <style>
```

---

**Lines 367-371**

Form labels are not explicitly associated with their corresponding input controls via 'for' and 'id' attributes. This reduces accessibility for screen reader users who may not understand which label corresponds to which input. Consider adding explicit id attributes to inputs and using the 'for' attribute on labels to create proper associations.

**Suggested fix:**
```diff
- <label class="form-label">Amount</label>
                                <div style="display:flex;align-items:center;">
                                    <input type="number" class="form-input" placeholder="8" value="8" style="margin-right:4px;">
                                    <select class="form-input" style="width:50px;padding:6px 2px;font-size:11px;"><option>oz</option><option>mL</option><option>L</option></select>
                                </div>
+ <label class="form-label" for="water-amount">Amount</label>
                                <div style="display:flex;align-items:center;">
                                    <input type="number" class="form-input" id="water-amount" placeholder="8" value="8" style="margin-right:4px;">
                                    <select class="form-input" style="width:50px;padding:6px 2px;font-size:11px;"><option>oz</option><option>mL</option><option>L</option></select>
                                </div>
```

---

## `packages/plant_service/src/plant_service/adapters/repository/base.py`

**Lines 49-53**

The method get_all_ids assumes the model has an attribute named 'id'. This will fail if the primary key is named differently (e.g., 'plant_id'). To make the repository truly generic, use SQLAlchemy's inspection to get the primary key column(s). For example, use `inspect(self.model_type).primary_key` to get the primary key column(s) and then build the select statement accordingly.

**Suggested fix:**
```diff
- +    def get_all_ids(self) -> list[str]:
+        """Get all entity IDs for sequence generation"""
+        stmt = select(self.model_type.id)
+        results = self.session.execute(stmt).scalars().all()
+        return [str(r) for r in results]
+ +    def get_all_ids(self) -> list[str]:
+        """Get all entity IDs for sequence generation"""
+        from sqlalchemy import inspect
+        mapper = inspect(self.model_type)
+        if len(mapper.primary_key) != 1:
+            raise NotImplementedError("Composite primary keys are not supported by get_all_ids")
+        pk_column = mapper.primary_key[0]
+        stmt = select(pk_column)
+        results = self.session.execute(stmt).scalars().all()
+        return [str(r) for r in results]
```

---

**Lines 34-38**

The update method uses session.add() which will insert a new entity if the entity is transient (not yet persisted). This contradicts the method name and docstring which imply updating an existing entity. Consider renaming the method to save_or_update or clarify in the docstring that it may insert new entities.

**Suggested fix:**
```diff
- +    def update(self, entity: T) -> T:
+        """Update existing entity"""
+        self.session.add(entity)
+        self.session.flush()
+        return entity
+ +    def update(self, entity: T) -> T:
+        """Update existing entity. If the entity is transient, it will be added as a new entity."""
+        self.session.add(entity)
+        self.session.flush()
+        return entity
```

---

**Lines 22-26**

The returned iterator holds an implicit reference to the session. If the session is closed before the iterator is fully consumed, it will result in an error. Callers must ensure the session remains open during iteration.

**Suggested fix:**
```diff
- +    def list_all(self) -> Iterator[T]:
+        """List all entities (returns iterator for streaming)"""
+        stmt = select(self.model_type)
+        for obj in self.session.execute(stmt).scalars().yield_per(100):
+            yield obj
+ +    def list_all(self) -> Iterator[T]:
+        """List all entities (returns iterator for streaming). Note: The session must remain open during iteration."""
+        stmt = select(self.model_type)
+        for obj in self.session.execute(stmt).scalars().yield_per(100):
+            yield obj
```

---

## `packages/plant_service/src/plant_service/adapters/repository/genus_repository.py`

**Lines 0-0**

Race condition in ID generation: Fetching all existing IDs and computing next sequence concurrently may lead to duplicate IDs when multiple processes create genera simultaneously. This compromises data integrity. Consider using database sequences, UUIDs, or database-level locking mechanisms for ID generation instead of application-level sequencing.

**Suggested fix:**
```diff
-     def create_genus(self, genus_data: dict) -> GenusDomain:
        """Create a new genus record"""
        # Generate ID with sequence
        existing_ids = self.get_all_ids()
        seq = GenusDomain.find_next_sequence(existing_ids)
        genus_data["id"] = GenusDomain().generate_id(seq)

        domain_obj = GenusDomain.create_from_dict(genus_data)
        orm_obj = Genus(
            id=domain_obj.id,
            variety_name=domain_obj.variety_name,
            latin_name=domain_obj.latin_name,
        )
        self.add(orm_obj)
        return domain_obj
+     def create_genus(self, genus_data: dict) -> GenusDomain:
        """Create a new genus record"""
        # TODO: Replace with database sequence or UUID to avoid race conditions
        # Generate ID with sequence
        existing_ids = self.get_all_ids()
        seq = GenusDomain.find_next_sequence(existing_ids)
        genus_data["id"] = GenusDomain().generate_id(seq)

        domain_obj = GenusDomain.create_from_dict(genus_data)
        orm_obj = Genus(
            id=domain_obj.id,
            variety_name=domain_obj.variety_name,
            latin_name=domain_obj.latin_name,
        )
        self.add(orm_obj)
        return domain_obj
```

---

**Lines 27-34**

Missing input validation: the method assumes genus_data contains required keys (variety_name, latin_name) without validation in the repository layer. While GenusDomain.create_from_dict performs validation, adding explicit validation here could provide clearer error messages and prevent unnecessary processing (like ID generation) on invalid input.

**Suggested fix:**
```diff
-         domain_obj = GenusDomain.create_from_dict(genus_data)
        orm_obj = Genus(
            id=domain_obj.id,
            variety_name=domain_obj.variety_name,
            latin_name=domain_obj.latin_name,
        )
        self.add(orm_obj)
        return domain_obj
+         # Validate input early
        if 'variety_name' not in genus_data or not genus_data['variety_name']:
            raise ValueError("variety_name is required")
        if 'latin_name' not in genus_data or not genus_data['latin_name']:
            raise ValueError("latin_name is required")
        
        domain_obj = GenusDomain.create_from_dict(genus_data)
        orm_obj = Genus(
            id=domain_obj.id,
            variety_name=domain_obj.variety_name,
            latin_name=domain_obj.latin_name,
        )
        self.add(orm_obj)
        return domain_obj
```

---

**Lines 0-0**

Inefficient ID retrieval for large tables: calling self.get_all_ids() fetches all genus IDs which may cause performance degradation as the table grows. While the base repository efficiently selects only the ID column, consider using a database sequence or UUID for ID generation to avoid this scalability issue.

**Suggested fix:**
```diff
-     def create_genus(self, genus_data: dict) -> GenusDomain:
        """Create a new genus record"""
        # Generate ID with sequence
        existing_ids = self.get_all_ids()
        seq = GenusDomain.find_next_sequence(existing_ids)
        genus_data["id"] = GenusDomain().generate_id(seq)

        domain_obj = GenusDomain.create_from_dict(genus_data)
        orm_obj = Genus(
            id=domain_obj.id,
            variety_name=domain_obj.variety_name,
            latin_name=domain_obj.latin_name,
        )
        self.add(orm_obj)
        return domain_obj
+     def create_genus(self, genus_data: dict) -> GenusDomain:
        """Create a new genus record"""
        # TODO: Replace with database sequence or UUID to avoid race conditions and inefficient ID retrieval
        # Generate ID with sequence
        existing_ids = self.get_all_ids()
        seq = GenusDomain.find_next_sequence(existing_ids)
        genus_data["id"] = GenusDomain().generate_id(seq)

        domain_obj = GenusDomain.create_from_dict(genus_data)
        orm_obj = Genus(
            id=domain_obj.id,
            variety_name=domain_obj.variety_name,
            latin_name=domain_obj.latin_name,
        )
        self.add(orm_obj)
        return domain_obj
```

---

## `packages/plant_service/src/plant_service/adapters/repository/log_repository.py`

**Lines 54-54**

The list_entries method orders log entries by timestamp in ascending order (oldest first). In most logging applications, users expect to see the most recent entries first (newest first) for better usability. Consider changing the order to descending (newest first) or adding a comment to clarify if ascending order is intentional for a specific reason.

**Suggested fix:**
```diff
- stmt = stmt.order_by(PlantLogEntry.timestamp)
+     def list_entries(
        self,
        plant_id: str | None = None,
        event_type: str | None = None,
    ) -> Iterator[PlantLogEntryDomain]:
        """List log entries (returns iterator for streaming)"""
        stmt = select(PlantLogEntry)
        if plant_id:
            stmt = stmt.where(PlantLogEntry.plant_id == plant_id)
        if event_type:
            stmt = stmt.where(PlantLogEntry.event_type == event_type)
        stmt = stmt.order_by(PlantLogEntry.timestamp.desc())  # Most recent first

        for orm_entry in self.session.execute(stmt).scalars().yield_per(100):
            yield orm_entry.to_domain()
```

---

## `packages/plant_service/src/plant_service/adapters/repository/media_attachment_repository.py`

**Lines 26-36**

Direct access to media_data keys ('plant_id', 'media_type', 's3_key') could raise KeyError if these keys are missing. Consider using .get() with appropriate validation or raising a more descriptive error.

**Suggested fix:**
```diff
- +        orm_media = MediaAttachmentORM(
+            plant_id=media_data["plant_id"],
+            media_type=media_data["media_type"],
+            s3_key=media_data["s3_key"],
+            timestamp=media_data.get(
+                "timestamp",
+                MediaAttachmentDomain().timestamp,
+            ),
+            label=media_data.get("label"),
+            tags=media_data.get("tags"),
+        )
+ +        orm_media = MediaAttachmentORM(
+            plant_id=media_data.get("plant_id"),
+            media_type=media_data.get("media_type"),
+            s3_key=media_data.get("s3_key"),
+            timestamp=media_data.get(
+                "timestamp",
+                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
+            ),
+            label=media_data.get("label"),
+            tags=media_data.get("tags"),
+        )
+
+        # Validate required fields
+        if orm_media.plant_id is None:
+            raise ValueError("plant_id is required")
+        if orm_media.media_type is None:
+            raise ValueError("media_type is required")
+        if orm_media.s3_key is None:
+            raise ValueError("s3_key is required")
```

---

**Lines 30-33**

Creating a MediaAttachmentDomain instance solely to obtain its default timestamp is inefficient. Instead, replicate the default timestamp logic directly to avoid unnecessary object instantiation.

**Suggested fix:**
```diff
- +            timestamp=media_data.get(
+                "timestamp",
+                MediaAttachmentDomain().timestamp,
+            ),
+ +            timestamp=media_data.get(
+                "timestamp",
+                datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")
+            ),
```

---

## `packages/plant_service/src/plant_service/adapters/repository/models/media_attachment_model.py`

**Lines 24-24**

The s3_key column is limited to String(500), but AWS S3 object keys can be up to 1024 bytes. While 500 characters may be sufficient for typical use cases, this arbitrary limit could cause insertion failures if longer keys are needed (especially with UTF-8 multi-byte characters). Consider increasing the limit to 1024 to match AWS S3 constraints, or if a shorter limit is intentional, add a comment explaining the reasoning.

**Suggested fix:**
```diff
- s3_key: Mapped[str] = mapped_column(String(500), nullable=False)
+ s3_key: Mapped[str] = mapped_column(String(1024), nullable=False)
```

---

## `packages/plant_service/src/plant_service/adapters/repository/plant_repository.py`

**Lines 0-0**

In create_plant method, direct access to plant_data['variety_name'] without validation can cause KeyError if the field is missing. Additionally, planting_date parsing with datetime.strptime() is not protected against ValueError if the date format is invalid. While PlantDomain.create_from_dict() does validate these fields, the validation occurs after we've already accessed variety_name and attempted to parse planting_date. Move the validation earlier or handle these exceptions appropriately.

**Suggested fix:**
```diff
-     def create_plant(self, plant_data: dict) -> PlantDomain:
        """Create a new plant record"""
        # Generate ID with sequence from existing records
        abbrev = PlantDomain.make_abbrev(plant_data["variety_name"])
        from datetime import datetime

        planting_date = plant_data.get("planting_date", datetime.now().strftime("%Y-%m-%d"))
        year = datetime.strptime(planting_date, "%Y-%m-%d").year

        existing_ids = self.get_all_ids()
        seq = PlantDomain.find_next_sequence(abbrev, year, existing_ids)

        plant_data["id"] = PlantDomain().generate_id(
            plant_data["variety_name"], planting_date, seq
        )
+     def create_plant(self, plant_data: dict) -> PlantDomain:
        """Create a new plant record"""
        # Validate required fields and date format early
        if "variety_name" not in plant_data:
            raise ValueError("Missing required field: variety_name")
        
        planting_date = plant_data.get("planting_date")
        if planting_date is not None:
            try:
                datetime.strptime(planting_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("planting_date must be in YYYY-MM-DD format")
        
        # Generate ID with sequence from existing records
        abbrev = PlantDomain.make_abbrev(plant_data["variety_name"])
        from datetime import datetime

        planting_date = planting_date or datetime.now().strftime("%Y-%m-%d")
        year = datetime.strptime(planting_date, "%Y-%m-%d").year

        existing_ids = self.get_all_ids()
        seq = PlantDomain.find_next_sequence(abbrev, year, existing_ids)

        plant_data["id"] = PlantDomain().generate_id(
            plant_data["variety_name"], planting_date, seq

        )
        domain_obj = PlantDomain.create_from_dict(plant_data)
```

---

**Lines 29-29**

The create_plant method calls self.get_all_ids() to fetch all plant IDs for sequence generation, which may cause performance degradation and high memory usage with large datasets. Consider optimizing by adding a database query that filters by abbreviation and year to only fetch relevant IDs, or implementing a dedicated sequence table.

**Suggested fix:**
```diff
- existing_ids = self.get_all_ids()
+     def create_plant(self, plant_data: dict) -> PlantDomain:
        """Create a new plant record"""
        # Validate required fields and date format early
        if "variety_name" not in plant_data:
            raise ValueError("Missing required field: variety_name")
        
        planting_date = plant_data.get("planting_date")
        if planting_date is not None:
            try:
                datetime.strptime(planting_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("planting_date must be in YYYY-MM-DD format")
        
        # Generate ID with sequence from existing records
        abbrev = PlantDomain.make_abbrev(plant_data["variety_name"])
        from datetime import datetime

        planting_date = planting_date or datetime.now().strftime("%Y-%m-%d")
        year = datetime.strptime(planting_date, "%Y-%m-%d").year

        # Optimize: Only fetch IDs matching abbreviation and year pattern
        stmt = select(Plant.id).where(Plant.id.like(f"{abbrev}-{year}-%"))
        existing_ids = [str(r[0]) for r in self.session.execute(stmt).all()]
        seq = PlantDomain.find_next_sequence(abbrev, year, existing_ids)

        plant_data["id"] = PlantDomain().generate_id(
            plant_data["variety_name"], planting_date, seq
        )
        domain_obj = PlantDomain.create_from_dict(plant_data)
        orm_obj = Plant(
            id=domain_obj.id,
            variety_name=domain_obj.variety_name,
            latin_name=domain_obj.latin_name,
            brand=domain_obj.brand,
            days_to_maturity=domain_obj.days_to_maturity,
            germination_time=domain_obj.germination_time,
            planting_depth=domain_obj.planting_depth,
            spacing=domain_obj.spacing,
            sun_requirements=domain_obj.sun_requirements,
            indoor_start_time=domain_obj.indoor_start_time,
            planting_date=domain_obj.planting_date,
            seed_packet_id=domain_obj.seed_packet_id,
            genus_id=domain_obj.genus_id,
        )
        self.add(orm_obj)
        return domain_obj
```

---

**Lines 0-0**

The update_plant method updates any attribute from plant_data on the ORM object (except 'id') without validating if the attribute is safe to update. This risks unintended modification of fields like timestamps (created_at, updated_at) or foreign keys that should not be changed directly. Consider implementing a whitelist of allowed fields for update or explicitly protecting sensitive fields.

**Suggested fix:**
```diff
-     def update_plant(self, plant_id: str, plant_data: dict) -> PlantDomain | None:
        """Update an existing plant"""
        orm_obj = self.get(plant_id)
        if not orm_obj:
            return None

        for key, value in plant_data.items():
            if hasattr(orm_obj, key) and key not in ("id",):
                setattr(orm_obj, key, value)

        self.update(orm_obj)
        return orm_obj.to_domain()
+     def update_plant(self, plant_id: str, plant_data: dict) -> PlantDomain | None:
        """Update an existing plant"""
        orm_obj = self.get(plant_id)
        if not orm_obj:
            return None

        # Define fields that should not be updated via this method
        protected_fields = {"id", "created_at", "updated_at"}
        
        for key, value in plant_data.items():
            if hasattr(orm_obj, key) and key not in protected_fields:
                setattr(orm_obj, key, value)

        self.update(orm_obj)
        return orm_obj.to_domain()
```

---

**Lines 32-34**

In create_plant, an unnecessary PlantDomain instance is created solely to call its generate_id method. Since make_abbrev and find_next_sequence are static methods, and generate_id only uses its parameters (and calls the static make_abbrev), consider making generate_id a static method as well to avoid object instantiation overhead.

**Suggested fix:**
```diff
- plant_data["id"] = PlantDomain().generate_id(
            plant_data["variety_name"], planting_date, seq
        )
+     def create_plant(self, plant_data: dict) -> PlantDomain:
        """Create a new plant record"""
        # Validate required fields and date format early
        if "variety_name" not in plant_data:
            raise ValueError("Missing required field: variety_name")
        
        planting_date = plant_data.get("planting_date")
        if planting_date is not None:
            try:
                datetime.strptime(planting_date, "%Y-%m-%d")
            except ValueError:
                raise ValueError("planting_date must be in YYYY-MM-DD format")
        
        # Generate ID with sequence from existing records
        abbrev = PlantDomain.make_abbrev(plant_data["variety_name"])
        from datetime import datetime

        planting_date = planting_date or datetime.now().strftime("%Y-%m-%d")
        year = datetime.strptime(planting_date, "%Y-%m-%d").year

        # Optimize: Only fetch IDs matching abbreviation and year pattern
        stmt = select(Plant.id).where(Plant.id.like(f"{abbrev}-{year}-%"))
        existing_ids = [str(r[0]) for r in self.session.execute(stmt).all()]
        seq = PlantDomain.find_next_sequence(abbrev, year, existing_ids)

        plant_data["id"] = PlantDomain.generate_id(
            plant_data["variety_name"], planting_date, seq
        )
        domain_obj = PlantDomain.create_from_dict(plant_data)
        orm_obj = Plant(
            id=domain_obj.id,
            variety_name=domain_obj.variety_name,
            latin_name=domain_obj.latin_name,
            brand=domain_obj.brand,
            days_to_maturity=domain_obj.days_to_maturity,
            germination_time=domain_obj.germination_time,
            planting_depth=domain_obj.planting_depth,
            spacing=domain_obj.spacing,
            sun_requirements=domain_obj.sun_requirements,
            indoor_start_time=domain_obj.indoor_start_time,
            planting_date=domain_obj.planting_date,
            seed_packet_id=domain_obj.seed_packet_id,
            genus_id=domain_obj.genus_id,
        )
        self.add(orm_obj)
        return domain_obj
```

---

## `packages/plant_service/src/plant_service/adapters/repository/seed_packet_repository.py`

**Lines 14-14**

Missing class docstring. Please add a docstring describing the purpose of this class.

---

**Lines 22-25**

The ID generation method retrieves all existing IDs from the database (O(n) complexity) which may cause performance issues as the dataset grows. Furthermore, this approach is not transaction-safe, leading to potential duplicate ID generation in concurrent environments. Consider using a database sequence or letting the database generate the ID (e.g., with an auto-increment) and then formatting it to the required SPKT-NNN pattern.

---

**Lines 20-21**

This method lacks error handling for potential database exceptions (e.g., integrity constraints, connection failures). Consider wrapping the database operations in a try-except block to catch specific SQLAlchemy exceptions and either re-raise them as domain-specific exceptions or handle them appropriately.

---

## `packages/plant_service/src/plant_service/adapters/repository/uow.py`

**Lines 78-85**

In the __exit__ method, if session.commit() or session.rollback() raises an exception, the session may not be closed due to the session.close() call being placed after the commit/rollback without exception handling, potentially causing resource leaks (unclosed database sessions). Suggested fix: wrap the commit/rollback in a try block and close the session in a finally block.

---

**Lines 27-34**

Missing docstring for the __init__ method. Adding a docstring would improve clarity about its parameters and purpose.

---

**Lines 0-0**

Missing docstrings for the public properties (plants, genera, seed_packets, logs, media_attachments). Adding docstrings would improve maintainability and clarity regarding their usage and return types. Example shown for plants and genera properties; the same issue applies to seed_packets, logs, and media_attachments properties.

---

## `packages/plant_service/src/plant_service/bootstrap.py`

**Lines 53-57**

Resource leak: Unit of Work entered but never exited.

---

**Lines 14-27**

Inefficient engine creation: The function creates a new SQLAlchemy engine on every call, which is expensive. Consider caching the engine and session factory for the default database URL (when database_url is None) to reuse the same engine across calls.

**Suggested fix:**
```diff
- def get_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    """Create session factory configured with database URL"""
    url = database_url or get_database_url()
    engine = create_engine(
        url,
        pool_pre_ping=True,
        echo=False,
    )
    return sessionmaker(
        autocommit=False,
        autoflush=False,
        bind=engine,
        expire_on_commit=False,
    )
+ # Cache the default engine and session factory to avoid repeated creation
_from typing import Any

_engine: Any = None
_session_factory: Any = None

def get_session_factory(database_url: str | None = None) -> sessionmaker[Session]:
    """Create session factory configured with database URL"""
    global _engine, _session_factory
    if database_url is None:
        if _session_factory is None:
            url = get_database_url()
            _engine = create_engine(
                url,
                pool_pre_ping=True,
                echo=False,
            )
            _session_factory = sessionmaker(
                autocommit=False,
                autoflush=False,
                bind=_engine,
                expire_on_commit=False,
            )
        return _session_factory
    else:
        engine = create_engine(
            database_url,
            pool_pre_ping=True,
            echo=False,
        )
        return sessionmaker(
            autocommit=False,
            autoflush=False,
            bind=engine,
            expire_on_commit=False,
        )
```

---

## `packages/plant_service/src/plant_service/config.py`

**Lines 7-7**

The path for loading the .env file assumes it is located in the 'packages' directory (three levels up). Given the project structure, the .env file might be expected at the repository root (four levels up). Please verify the location of the .env file and adjust the path if necessary.

---

## `packages/plant_service/src/plant_service/domain/genus.py`

**Lines 0-0**

Consider moving the regex pattern to a class-level constant to avoid recompilation on every call. This improves performance if the method is called frequently.

**Suggested fix:**
```diff
- class Genus:
    """Genus entity matching existing SQLAlchemy model"""

    REQUIRED_FIELDS: ClassVar[list[str]] = ["variety_name", "latin_name"]
+ class Genus:
    """Genus entity matching existing SQLAlchemy model"""

    _ID_REGEX = re.compile(r"^GENUS-(\d{3})$")
    REQUIRED_FIELDS: ClassVar[list[str]] = ["variety_name", "latin_name"]
```

---

**Lines 24-29**

Consider making generate_id a static method since it doesn't use any instance state. This improves clarity that the method is independent of instance attributes.

**Suggested fix:**
```diff
-     def generate_id(self, seq: int = 1) -> str:
        """
        Generate genus ID in GENUS-NNN format.
        Note: seq is passed in from the service layer which queries existing records.
        """
        return f"GENUS-{seq:03d}"
+     @staticmethod
    def generate_id(seq: int = 1) -> str:
        """
        Generate genus ID in GENUS-NNN format.
        Note: seq is passed in from the service layer which queries existing records.
        """
        return f"GENUS-{seq:03d}"
```

---

**Lines 48-51**

The docstring claims to preserve the logic from commands/models/genus.py:64-77, but the ID generation part is missing. Consider updating the docstring to reflect that only the validation logic is preserved, and that ID generation is handled by the service layer.

**Suggested fix:**
```diff
-         """
        Create Genus instance from dictionary data.
        Preserves validation logic from commands/models/genus.py:64-77
        """
+         """
        Create Genus instance from dictionary data.
        Preserves validation logic for required fields from commands/models/genus.py:64-77.
        ID generation is delegated to the service layer.
        """
```

---

## `packages/plant_service/src/plant_service/domain/plant.py`

**Lines 84-87**

The `create_from_dict` method checks for the presence of required fields but does not validate that they are non-empty strings. This could allow invalid plants with empty variety_name or latin_name to be created. Consider adding a check for non-empty values.

---

## `packages/plant_service/src/plant_service/domain/seed_packet.py`

**Lines 59-61**

The create_from_dict method validates required fields by checking truthiness, but does not validate field types. This could allow non-string values (e.g., integers, booleans) for variety_name and latin_name to pass validation, which may cause runtime errors later when these fields are used as strings. Consider adding type validation or converting values to strings.

**Suggested fix:**
```diff
- for fld in cls.REQUIRED_FIELDS:
    if fld not in data or not data[fld]:
        raise ValueError(f"Missing required field: {fld}")
+     @classmethod
+    def create_from_dict(cls, data: dict) -> "SeedPacket":
+        """
+        Create SeedPacket instance from dictionary data.
+        Preserves validation logic from commands/models/seed_packet.py:71-84
+        """
+        for fld in cls.REQUIRED_FIELDS:
+            if fld not in data or not isinstance(data[fld], str) or not data[fld].strip():
+                raise ValueError(f"Missing required field: {fld}")
+
+        return cls(**data)
```

---

**Lines 0-0**

The regex pattern in find_next_sequence is compiled on every call. For better performance and following best practices, move the regex pattern to a module-level constant since it's reused.

**Suggested fix:**
```diff
-     @staticmethod
+    def find_next_sequence(existing_ids: list[str]) -> int:
+        """
+        Find next sequence number for seed packet ID.
+        Takes existing IDs from the repository layer - no DB access here.
+        """
+        regex_pattern = re.compile(r"^SPKT-(\d{3})$)")
+        max_seq = 0
+        for packet_id in existing_ids:
+            match = regex_pattern.match(packet_id)
+            if match:
+                seq = int(match.group(1))
+                max_seq = max(max_seq, seq)
+        return max_seq + 1
+ SPKT_ID_PATTERN = re.compile(r'^SPKT-(\d{3})$')

    @staticmethod
+    def find_next_sequence(existing_ids: list[str]) -> int:
+        """
+        Find next sequence number for seed packet ID.
+        Takes existing IDs from the repository layer - no DB access here.
+        """
+        max_seq = 0
+        for packet_id in existing_ids:
+            match = SPKT_ID_PATTERN.match(packet_id)
+            if match:
+                seq = int(match.group(1))
+                max_seq = max(max_seq, seq)
+        return max_seq + 1
```

---

**Lines 31-36**

The generate_id method uses format 'SPKT-{seq:03d}' which produces IDs with at least 3 digits (padded with zeros). However, if seq exceeds 999, the ID will have more than 3 digits (e.g., SPKT-1000), which violates the SPKT-NNN format expectation and will fail validation in plant.py that checks for exactly 3 digits. Consider adding a check to prevent seq from exceeding 999 or document this limitation.

**Suggested fix:**
```diff
-     def generate_id(self, seq: int = 1) -> str:
+        """
+        Generate seed packet ID in SPKT-NNN format.
+        Note: seq is passed in from the service layer which queries existing records.
+        """
+        return f"SPKT-{seq:03d}"
+     def generate_id(self, seq: int = 1) -> str:
+        """
+        Generate seed packet ID in SPKT-NNN format.
+        Note: seq is passed in from the service layer which queries existing records.
+        Limitation: seq must be < 1000 to maintain SPKT-NNN format.
+        """
+        if seq >= 1000:
+            raise ValueError(f"Sequence number {seq} exceeds maximum of 999 for SPKT-NNN format")
+        return f"SPKT-{seq:03d}"
```

---

## `packages/plant_service/src/plant_service/domain/utils.py`

**Lines 18-18**

The unit string may contain multiple spaces (e.g., 'fluid   ounce') which are not normalized, causing a ValueError for valid units with extra spaces. Consider normalizing the unit string by collapsing multiple whitespace characters to a single space.

**Suggested fix:**
```diff
-     unit = match.group(2).strip().lower()
+     unit = ' '.join(match.group(2).strip().split()).lower()
```

---

**Lines 18-18**

The unit string may contain multiple consecutive spaces (e.g., 'fluid   ounce') which are not normalized, causing a ValueError for valid units with extra whitespace. Consider normalizing internal whitespace by collapsing multiple spaces to a single space.

**Suggested fix:**
```diff
-     unit = match.group(2).strip().lower()
+     unit = ' '.join(match.group(2).strip().split()).lower()
```

---

## `packages/plant_service/src/plant_service/service_layer/export_service.py`

**Lines 18-42**

The batch_size parameter in all streaming export methods is accepted but not used. The methods iterate over records individually without applying the specified batch size. While the underlying repository methods do stream results (using yield_per(100) in base repository), the export service's batch_size parameter is misleading as it doesn't control the actual batch size used for iteration. Either remove the unused parameter or implement proper batching that respects the batch_size argument.

**Suggested fix:**
```diff
-     def export_plants_streaming(self, batch_size: int = 100) -> Iterator[Dict[str, Any]]:
        """
        Stream plant records in batches to avoid memory overload.
        Returns iterator that yields plant data one batch at a time.
        """
        try:
            with self.uow as uow:
                for plant in uow.plants.list_plants():
                    yield {
                        "id": plant.id,
                        "variety_name": plant.variety_name,
                        "latin_name": plant.latin_name,
                        "brand": plant.brand,
                        "days_to_maturity": plant.days_to_maturity,
                        "germination_time": plant.germination_time,
                        "planting_depth": plant.planting_depth,
                        "spacing": plant.spacing,
                        "sun_requirements": plant.sun_requirements,
                        "indoor_start_time": plant.indoor_start_time,
                        "planting_date": plant.planting_date,
                        "seed_packet_id": plant.seed_packet_id,
                        "genus_id": plant.genus_id,
                    }
        except Exception as e:
            raise ExportError(f"Failed to export plants: {str(e)}")
+     def export_plants_streaming(self, batch_size: int = 100) -> Iterator[Dict[str, Any]]:
        """
        Stream plant records in batches to avoid memory overload.
        Returns iterator that yields plant data one batch at a time.
        """
        try:
            with self.uow as uow:
                # TODO: Implement proper batching that respects batch_size parameter
                # Current implementation ignores batch_size and relies on repository's yield_per(100)
                for plant in uow.plants.list_plants():
                    yield {
                        "id": plant.id,
                        "variety_name": plant.variety_name,
                        "latin_name": plant.latin_name,
                        "brand": plant.brand,
                        "days_to_maturity": plant.days_to_maturity,
                        "germination_time": plant.germination_time,
                        "planting_depth": plant.planting_depth,
                        "spacing": plant.spacing,
                        "sun_requirements": plant.sun_requirements,
                        "indoor_start_time": plant.indoor_start_time,
                        "planting_date": plant.planting_date,
                        "seed_packet_id": plant.seed_packet_id,
                        "genus_id": plant.genus_id,
                    }
        except Exception as e:
            raise ExportError(f"Failed to export plants: {str(e)}")
```

---

**Lines 0-0**

The export_to_markdown method claims to export 'all data' but only exports seed packets and genera to Markdown files, omitting plants and logs entirely. This results in incomplete exports and contradicts the method's documented purpose.

**Suggested fix:**
```diff
-     def export_to_markdown(self, output_dir: str) -> Path:
        """
        Export all data to Markdown files using streaming.
        Returns the path to the export directory.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = Path(output_dir) / f"markdown_export_{timestamp}"

            (export_path / "seed_packets").mkdir(parents=True, exist_ok=True)
            (export_path / "genera").mkdir(parents=True, exist_ok=True)
            (export_path / "logs").mkdir(parents=True, exist_ok=True)

            # Export seed packets
            for packet_data in self.export_seed_packets_streaming():
                self._write_markdown_file(
                    export_path / "seed_packets" / f"{packet_data['id']}.md",
                    packet_data,
                )

            # Export genera
            for genus_data in self.export_genera_streaming():
                self._write_markdown_file(
                    export_path / "genera" / f"{genus_data['id']}.md",
                    genus_data,
                )

            return export_path

        except Exception as e:
            raise ExportError(f"Failed to export to markdown: {str(e)}")
+     def export_to_markdown(self, output_dir: str) -> Path:
        """
        Export all data to Markdown files using streaming.
        Returns the path to the export directory.
        """
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_path = Path(output_dir) / f"markdown_export_{timestamp}"

            (export_path / "seed_packets").mkdir(parents=True, exist_ok=True)
            (export_path / "genera").mkdir(parents=True, exist_ok=True)
            (export_path / "logs").mkdir(parents=True, exist_ok=True)
            (export_path / "plants").mkdir(parents=True, exist_ok=True)

            # Export seed packets
            for packet_data in self.export_seed_packets_streaming():
                self._write_markdown_file(
                    export_path / "seed_packets" / f"{packet_data['id']}.md",
                    packet_data,
                )

            # Export genera
            for genus_data in self.export_genera_streaming():
                self._write_markdown_file(
                    export_path / "genera" / f"{genus_data['id']}.md",
                    genus_data,
                )

            # Export plants
            for plant_data in self.export_plants_streaming():
                self._write_markdown_file(
                    export_path / "plants" / f"{plant_data['id']}.md",
                    plant_data,
                )

            # Export logs
            for log_data in self.export_logs_streaming():
                self._write_markdown_file(
                    export_path / "logs" / f"{log_data['id']}.md",
                    log_data,
                )

            return export_path

        except Exception as e:
            raise ExportError(f"Failed to export to markdown: {str(e)}")
```

---

**Lines 137-146**

The _write_markdown_file method writes field values directly without ensuring they are properly formatted for YAML. While integer fields are fine, string fields containing special YAML characters (like colons, quotes, etc.) or values that look like YAML literals (e.g., 'yes', 'no', 'true', 'false', numbers) may produce invalid YAML. Additionally, the PlantLogEntry model includes integer fields (id, level, amount_ml) that are written as unquoted integers, which is valid YAML but may be unexpected in Markdown frontmatter where string values are typical. Consider converting all values to strings and ensuring proper YAML escaping, or using a YAML library to generate the frontmatter.

**Suggested fix:**
```diff
-     @staticmethod
    def _write_markdown_file(filepath: Path, data: dict) -> None:
        """Write a single record as a Markdown file with YAML frontmatter."""
        lines = ["---"]
        for key, value in data.items():
            if value is not None:
                lines.append(f"{key}: {value}")
        lines.append("---")
        lines.append("")
        filepath.write_text("\n".join(lines))
+     @staticmethod
    def _write_markdown_file(filepath: Path, data: dict) -> None:
        """Write a single record as a Markdown file with YAML frontmatter."""
        import yaml
        lines = ["---"]
        # Convert all values to strings and handle None values
        cleaned_data = {}
        for key, value in data.items():
            if value is not None:
                # Convert to string for consistent YAML frontmatter
                cleaned_data[key] = str(value)
        # Use yaml.dump to ensure proper YAML formatting
        yaml_content = yaml.dump(cleaned_data, default_flow_style=False)
        lines.append(yaml_content)
        lines.append("---")
        lines.append("")
        filepath.write_text("\n".join(lines))
```

---

## `packages/plant_service/src/plant_service/service_layer/genus_service.py`

**Lines 1-1**

Add a brief description of what the genus service is responsible for.

---

**Lines 1-1**

Expand the module docstring to better describe the purpose of this service interface.

**Suggested fix:**
```diff
- """Genus service interface (port) defining genus-related use cases"""
+ """Interface defining the genus-related use cases (service layer) for the plant tracking application.

This protocol outlines the contracts for genus service implementations, specifying how to create, retrieve, list, and search for genus records.
"""}
```

---

## `packages/plant_service/src/plant_service/service_layer/s3_service.py`

**Lines 25-33**

The S3Service class directly instantiates a boto3 client in __init__ using configuration functions, creating tight coupling that makes unit testing difficult. Consider dependency injection by accepting the boto3 client or configuration parameters to improve testability and flexibility, similar to how S3Service is injected into MediaAttachmentServiceImpl.

**Suggested fix:**
```diff
-     def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=get_s3_endpoint_url(),
            aws_access_key_id=get_s3_access_key_id(),
            aws_secret_access_key=get_s3_secret_access_key(),
            region_name=get_s3_region(),
        )
        self.bucket = get_s3_bucket()
+     def __init__(self, endpoint_url: str, access_key_id: str, secret_access_key: str, region_name: str, bucket: str) -> None:
        self.client = boto3.client(
            "s3",
            endpoint_url=endpoint_url,
            aws_access_key_id=access_key_id,
            aws_secret_access_key=secret_access_key,
            region_name=region_name,
        )
        self.bucket = bucket
```

---

**Lines 25-33**

Missing return type annotation for __init__ method. Should be -> None for consistency with type hinting guidelines.

**Suggested fix:**
```diff
-     def __init__(self):
        self.client = boto3.client(
            "s3",
            endpoint_url=get_s3_endpoint_url(),
            aws_access_key_id=get_s3_access_key_id(),
            aws_secret_access_key=get_s3_secret_access_key(),
            region_name=get_s3_region(),
        )
        self.bucket = get_s3_bucket()
+     def __init__(self) -> None:
        self.client = boto3.client(
            "s3",
            endpoint_url=get_s3_endpoint_url(),
            aws_access_key_id=get_s3_access_key_id(),
            aws_secret_access_key=get_s3_secret_access_key(),
            region_name=get_s3_region(),
        )
        self.bucket = get_s3_bucket()
```

---

**Lines 44-51**

Missing type hint for fileobj parameter in upload_fileobj method. Should be typed as IO[bytes] or BinaryIO for clarity and static type checking.

**Suggested fix:**
```diff
-     def upload_fileobj(self, fileobj, s3_key: str) -> bool:
        """Upload a file-like object to S3."""
        try:
            self.client.upload_fileobj(fileobj, self.bucket, s3_key)
            return True
        except ClientError as e:
            logger.error("Error uploading fileobj to S3: %s", e)
            return False
+     def upload_fileobj(self, fileobj: IO[bytes], s3_key: str) -> bool:
        """Upload a file-like object to S3."""
        try:
            self.client.upload_fileobj(fileobj, self.bucket, s3_key)
            return True
        except ClientError as e:
            logger.error("Error uploading fileobj to S3: %s", e)
            return False
```

---

## `packages/plant_service/src/plant_service/service_layer/unit_of_work.py`

**Lines 24-26**

The `__exit__` method is missing type hints for its parameters. According to the guidelines, every public function and method must have type hints. Please add type hints for `exc_type`, `exc_val`, and `exc_tb`. To avoid adding an import for `types`, we can use string annotations (since we are using `from __future__ import annotations`).

**Suggested fix:**
```diff
-     def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit transaction context - commit if no exception, rollback otherwise"""
        ...
+     def __exit__(
        self,
        exc_type: "type[BaseException] | None",
        exc_val: "BaseException | None",
        exc_tb: "types.TracebackType | None",
    ) -> None:
        """Exit transaction context - commit if no exception, rollback otherwise"""
        ...
```

---

**Lines 24-26**

The `__exit__` method is missing type hints for its parameters. Please add type hints for `exc_type`, `exc_val`, and `exc_tb` to comply with the guideline that every public function and method must have type hints. Use string annotations to avoid importing the `types` module since we already have `from __future__ import annotations`.

**Suggested fix:**
```diff
-     def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Exit transaction context - commit if no exception, rollback otherwise"""
        ...
+     def __exit__(
        self,
        exc_type: "type[BaseException] | None",
        exc_val: "BaseException | None",
        exc_tb: "types.TracebackType | None",
    ) -> None:
        """Exit transaction context - commit if no exception, rollback otherwise"""
        ...
```

---

## `packages/plant_service/tests/integration/test_repository.py`

**Lines 133-141**

The test uses a hardcoded plant_id 'YEHA-2026-001' that is not created in the test, which may lead to foreign key constraint failures. Instead, create a plant first within a unit of work, obtain its generated ID, and use that ID for the log entry. This ensures the test is self-contained and reliable. The same issue exists in test_list_entries and test_list_entries_filter_by_test methods of TestLogRepository.

**Suggested fix:**
```diff
-     def test_create_log_entry(self, uow):
        with uow:
            entry = uow.logs.create_log_entry({
                "plant_id": "YEHA-2026-001",
                "event_type": "humidity",
                "level": 5,
            })
        assert entry.event_type == "humidity"
        assert entry.level == 5
+     def test_create_log_entry(self, uow):
        # First, create a plant to get a valid plant_id
        with uow:
            plant = uow.plants.create_plant({
                "variety_name": "Test Plant",
                "latin_name": "Test Latin",
                "planting_date": "2026-01-01",
            })
            plant_id = plant.id

        # Now create the log entry for that plant
        with uow:
            entry = uow.logs.create_log_entry({
                "plant_id": plant_id,
                "event_type": "humidity",
                "level": 5,
            })
        assert entry.event_type == "humidity"
        assert entry.level == 5
        assert entry.plant_id == plant_id
```

---

**Lines 0-0**

The test uses a hardcoded plant_id 'YEHA-2026-001' that is not created in the test, which may lead to foreign key constraint failures. Instead, create a plant first within a unit of work, obtain its generated ID, and use that ID for the log entries. This ensures the test is self-contained and reliable.

**Suggested fix:**
```diff
-     def test_list_entries(self, uow):
        with uow:
            uow.logs.create_log_entry({
                "plant_id": "YEHA-2026-001",
                "event_type": "humidity",
                "level": 5,
            })
            uow.logs.create_log_entry({
                "plant_id": "YEHA-2026-001",
                "event_type": "water",
                "amount_ml": 250,
            })

        with uow:
            entries = list(uow.logs.list_entries(plant_id="YEHA-2026-001"))
        assert len(entries) == 2
+     def test_list_entries(self, uow):
        # First, create a plant to get a valid plant_id
        with uow:
            plant = uow.plants.create_plant({
                "variety_name": "Test Plant",
                "latin_name": "Test Latin",
                "planting_date": "2026-01-01",
            })
            plant_id = plant.id

        with uow:
            uow.logs.create_log_entry({
                "plant_id": plant_id,
                "event_type": "humidity",
                "level": 5,
            })
            uow.logs.create_log_entry({
                "plant_id": plant_id,
                "event_type": "water",
                "amount_ml": 250,
            })

        with uow:
            entries = list(uow.logs.list_entries(plant_id=plant_id))
        assert len(entries) == 2
```

---

## `packages/plant_service/tests/unit/test_exceptions.py`

**Lines 15-15**

Missing docstring for the test class. Additionally, each test method should have a docstring describing what is being tested.

---

**Lines 15-15**

Missing docstring for the test class. Add a docstring describing the purpose of this test class.

**Suggested fix:**
```diff
- class TestExceptionHierarchy:
+ """Test hierarchy of domain exceptions."""
class TestExceptionHierarchy:
```

---

**Lines 16-19**

Missing docstring for this test method. Add a docstring describing what is being tested. The same issue exists for the other test methods in this class.

**Suggested fix:**
```diff
-     def test_base_exception(self):
        exc = PlantTrackingServiceException("test")
        assert isinstance(exc, Exception)
        assert str(exc) == "test"
+     def test_base_exception(self):
        """Test that PlantTrackingServiceException is correctly instantiated and inherits from Exception."""
        exc = PlantTrackingServiceException("test")
        assert isinstance(exc, Exception)
        assert str(exc) == "test"
```

---

**Lines 21-24**

Missing docstring for this test method. Add a docstring describing what is being tested.

**Suggested fix:**
```diff
-     def test_validation_exception(self):
        exc = ValidationException("invalid data")
        assert isinstance(exc, PlantTrackingServiceException)
        assert isinstance(exc, Exception)
+     def test_validation_exception(self):
        """Test that ValidationException inherits from PlantTrackingServiceException and Exception."""
        exc = ValidationException("invalid data")
        assert isinstance(exc, PlantTrackingServiceException)
        assert isinstance(exc, Exception)
```

---

**Lines 26-28**

Missing docstring for this test method. Additionally, all test methods in this class should have docstrings describing what is being tested.

**Suggested fix:**
```diff
-     def test_plant_not_found(self):
        exc = PlantNotFoundException("plant-001")
        assert isinstance(exc, PlantTrackingServiceException)
+     def test_plant_not_found(self):
        """Test that PlantNotFoundException inherits from PlantTrackingServiceException."""
        exc = PlantNotFoundException("plant-001")
        assert isinstance(exc, PlantTrackingServiceException)
```

---

## `packages/plant_service/tests/unit/test_genus_model.py`

**Lines 0-0**

Add class docstring and method docstrings with type hints (-> None) for test methods.

**Suggested fix:**
```diff
- class TestGenusGenerateId:
    def test_basic_format(self):
        genus = Genus(id="", variety_name="Pepper", latin_name="Capsicum")
        assert genus.generate_id(seq=1) == "GENUS-001"

    def test_sequence_padding(self):
        genus = Genus(id="", variety_name="Tomato", latin_name="Solanum")
        assert genus.generate_id(seq=99) == "GENUS-099"
+ class TestGenusGenerateId:
    """Tests for the Genus.generate_id method."""
    def test_basic_format(self) -> None:
        """Test that generate_id produces the correct format with sequence padding."""
        genus = Genus(id="", variety_name="Pepper", latin_name="Capsicum")
        assert genus.generate_id(seq=1) == "GENUS-001"

    def test_sequence_padding(self) -> None:
        """Test that the sequence is zero-padded to three digits."""
        genus = Genus(id="", variety_name="Tomato", latin_name="Solanum")
        assert genus.generate_id(seq=99) == "GENUS-099"}
```

---

## `packages/plant_service/tests/unit/test_plant_log_model.py`

**Lines 8-15**

The test_valid_humidity method creates a PlantLogEntry but fails to assert that the plant_id field is correctly set. This omission means bugs in plant_id assignment would not be caught, risking data integrity issues where logs could be associated with incorrect plants.\n\nAdd assertion: assert entry.plant_id == "YEHA-2026-001"

---

**Lines 8-15**

The test_valid_humidity method creates a PlantLogEntry but fails to assert that the plant_id field is correctly set. This omission means bugs in plant_id assignment would not be caught, risking data integrity issues where logs could be associated with incorrect plants.\n\nAdd assertion: assert entry.plant_id == "YEHA-2026-001"

---

**Lines 17-23**

The test_valid_water method creates a PlantLogEntry but fails to assert that the plant_id field is correctly set. This omission means bugs in plant_id assignment would not be caught, risking data integrity issues where logs could be associated with incorrect plants.\n\nAdd assertion: assert entry.plant_id == "YEHA-2026-001"

---

**Lines 25-32**

The test_valid_fertilizer method creates a PlantLogEntry but fails to assert that the plant_id field is correctly set. This omission means bugs in plant_id assignment would not be caught, risking data integrity issues where logs could be associated with incorrect plants.\n\nAdd assertion: assert entry.plant_id == "YEHA-2026-001"

---

## `packages/plant_service/tests/unit/test_plant_model.py`

**Lines 19-20**

The test is non-deterministic because it accepts two different outcomes ('123 ' or '123'). This reduces the test's effectiveness in verifying specific behavior. Please determine the expected behavior of `Plant.make_abbrev` for input '123 456' and assert exactly that value.

---

**Lines 36-38**

The test relies on datetime.now().year, making it dependent on the system clock and prone to failure when executed in a different year than expected. Consider mocking the current date to a fixed value for deterministic testing.

---

**Lines 78-79**

The test only validates one missing field scenario (variety_name provided) without checking each required field individually, limiting test coverage for validation logic. Consider adding separate tests for each required field (variety_name, latin_name, planting_date) being missing.

---

## `packages/plant_service/tests/unit/test_seed_packet_model.py`

**Lines 28-30**

In the test for valid data, we should also assert that the latin_name is set correctly to ensure all fields are properly initialized.

**Suggested fix:**
```diff
- data = {"variety_name": "Tomato", "latin_name": "Solanum lycopersicum"}
        sp = SeedPacket.create_from_dict(data)
        assert sp.variety_name == "Tomato"
+ data = {"variety_name": "Tomato", "latin_name": "Solanum lycopersicum"}
        sp = SeedPacket.create_from_dict(data)
        assert sp.variety_name == "Tomato"
        assert sp.latin_name == "Solanum lycopersicum"
```

---

**Lines 28-30**

In the test for valid data, we should also assert that the id is set to an empty string, as the SeedPacket model initializes the id to an empty string when not provided (consistent with the generate_id tests).

**Suggested fix:**
```diff
- data = {"variety_name": "Tomato", "latin_name": "Solanum lycopersicum"}
        sp = SeedPacket.create_from_dict(data)
        assert sp.variety_name == "Tomato"
+ data = {"variety_name": "Tomato", "latin_name": "Solanum lycopersicum"}
        sp = SeedPacket.create_from_dict(data)
        assert sp.variety_name == "Tomato"
        assert sp.id == ""}
```

---

**Lines 32-34**

We should also test that a missing 'variety_name' field raises a ValueError. Currently, only the absence of 'latin_name' is tested.

**Suggested fix:**
```diff
- def test_missing_required_field(self):
        with pytest.raises(ValueError, match="Missing required field"):
            SeedPacket.create_from_dict({"variety_name": "Tomato"})
+ def test_missing_required_field(self):
        with pytest.raises(ValueError, match="Missing required field"):
            SeedPacket.create_from_dict({"variety_name": "Tomato"})

    def test_missing_variety_name(self):
        with pytest.raises(ValueError, match="Missing required field"):
            SeedPacket.create_from_dict({"latin_name": "Solanum lycopersicum"})
```

---

## `packages/plant_service/tests/unit/test_utils.py`

**Lines 14-16**

The test for liters only checks the value_ml field. It should also verify the display_value and display_unit fields to ensure the function returns correct display information, similar to the milliliter test.

**Suggested fix:**
```diff
-     def test_liters(self):
        result = normalize_water_amount("1 L")
        assert result["value_ml"] == pytest.approx(1000.0)
+     def test_liters(self):
        result = normalize_water_amount("1 L")
        assert result["value_ml"] == pytest.approx(1000.0)
        assert result["display_value"] == 1.0
        assert result["display_unit"] == "L"
```

---

**Lines 14-16**

The test for liters only checks the value_ml field. It should also verify the display_value and display_unit fields to ensure the function returns correct display information, similar to the milliliter test.

**Suggested fix:**
```diff
-     def test_liters(self):
        result = normalize_water_amount("1 L")
        assert result["value_ml"] == pytest.approx(1000.0)
+     def test_liters(self):
        result = normalize_water_amount("1 L")
        assert result["value_ml"] == pytest.approx(1000.0)
        assert result["display_value"] == 1.0
        assert result["display_unit"] == "L"
```

---

**Lines 18-20**

The test for cups only checks the value_ml field. It should also verify the display_value and display_unit fields to ensure the function returns correct display information, similar to the milliliter test.

**Suggested fix:**
```diff
-     def test_cups(self):
        result = normalize_water_amount("2 cups")
        assert result["value_ml"] == pytest.approx(473.176)
+     def test_cups(self):
        result = normalize_water_amount("2 cups")
        assert result["value_ml"] == pytest.approx(473.176)
        assert result["display_value"] == 2.0
        assert result["display_unit"] == "cups"}
```

---

## `phomemo-tools/.copr/Makefile`

**Lines 1-1**

The target 'srpm' should be marked as phony by adding '.PHONY: srpm' to avoid potential conflicts with files named 'srpm'.

---

**Lines 5-5**

The tarball name is hardcoded to a specific version (2.3). This makes the Makefile inflexible when the version changes. Consider using a variable that can be set via an environment variable or derived from the project (e.g., by parsing the spec file).

---

**Lines 5-5**

The variable 'outdir' is used but not defined in this Makefile. Either define it with a default value or document that it must be set in the environment.

---

**Lines 1-1**

The target 'srpm' should be marked as phony by adding '.PHONY: srpm' to avoid potential conflicts with files named 'srpm'.

---

**Lines 5-5**

The tarball name is hardcoded to a specific version (2.3). This makes the Makefile inflexible when the version changes. Consider using a variable that can be set via an environment variable or derived from the project (e.g., by parsing the spec file).

---

**Lines 5-5**

The variable 'outdir' is used but not defined in this Makefile. Either define it with a default value or document that it must be set in the environment.

---

## `phomemo-tools/cups/Makefile`

**Lines 4-4**

The ppds target generates PPD files in the current directory, but the install target expects them in the ppd/ directory. This will cause the install target to fail because it cannot find the ppd files. Consider modifying the ppds target to output the generated files to the ppd/ directory, for example by adding 'mkdir -p ppd && mv *.ppd.gz ppd/' after the ppdc command, or check if ppdc supports an output directory option.

**Suggested fix:**
```diff
- 	LC_ALL=C ppdc -z drv/*
+ 	LC_ALL=C ppdc -z drv/*
	mkdir -p ppd
	mv *.ppd.gz ppd/
```

---

## `phomemo-tools/cups/filter/rastertopd30.py`

**Lines 30-30**

This function lacks type hints and a docstring. Please add type hints for the parameter and return type, and a docstring explaining what the function does, its parameters, and what it returns.

---

**Lines 30-30**

This function lacks type hints and a docstring. Please add type hints for the parameter and return type, and a docstring explaining what the function does, its parameters, and what it returns.

---

## `phomemo-tools/glabels/Makefile`

**Lines 8-9**

The 'install' target does not depend on the XML file being built. If the XML file is not present (e.g., if 'make all' has not been run), this target will fail. It should depend on the XML file to ensure it is built before installation.

**Suggested fix:**
```diff
- install:
	install -Dm 0644 $(XML) -t $(DESTDIR)/usr/share/phomemo/
+ install: $(XML)
	install -Dm 0644 $(XML) -t $(DESTDIR)/usr/share/phomemo/
```

---

**Lines 8-9**

The 'install' target does not depend on the XML file being built. If the XML file is not present (e.g., if 'make all' has not been run), this target will fail. It should depend on the XML file to ensure it is built before installation.

**Suggested fix:**
```diff
- install:
	install -Dm 0644 $(XML) -t $(DESTDIR)/usr/share/phomemo/
+ install: $(XML)
	install -Dm 0644 $(XML) -t $(DESTDIR)/usr/share/phomemo/
```

---

**Lines 11-12**

The 'user-install' target does not depend on the XML file being built. If the XML file is not present (e.g., if 'make all' has not been run), this target will fail. It should depend on the XML file to ensure it is built before installation.

**Suggested fix:**
```diff
- user-install:
	install -Dm 0644 $(XML) ~/.config/libglabels/templates/phomemo-q22.template
+ user-install: $(XML)
	install -Dm 0644 $(XML) ~/.config/libglabels/templates/phomemo-q22.template
```

---

## `phomemo-tools/glabels/generate.sh`

**Lines 6-8**

The script does not check for the existence of the template file 'Phomemo_Q22.template'. If the file is missing, the sed command will fail and the script will continue, potentially producing invalid output. Consider adding a check at the beginning of the script.

**Suggested fix:**
```diff
- for height in 10 20 25 30 50 60 70 75 80 90 100 110 120 125 130 140 150; do
    sed "s/@@HEIGHT@@/$height/g" Phomemo_Q22.template
done
+ if [ ! -f "Phomemo_Q22.template" ]; then
    echo "Error: Template file 'Phomemo_Q22.template' not found." >&2
    exit 1
fi

for height in 10 20 25 30 50 60 70 75 80 90 100 110 120 125 130 140 150; do
    sed "s/@@HEIGHT@@/$height/g" Phomemo_Q22.template
done
```

---

**Lines 6-8**

The script does not check for the existence of the template file 'Phomemo_Q22.template'. If the file is missing, sed will fail and the script will continue, potentially producing invalid output. Consider adding a check at the beginning of the script.

**Suggested fix:**
```diff
- for height in 10 20 25 30 50 60 70 75 80 90 100 110 120 125 130 140 150; do
    sed "s/@@HEIGHT@@/$height/g" Phomemo_Q22.template
done
+ if [ ! -f "Phomemo_Q22.template" ]; then
    echo "Error: Template file 'Phomemo_Q22.template' not found." >&2
    exit 1
fi

for height in 10 20 25 30 50 60 70 75 80 90 100 110 120 125 130 140 150; do
    sed "s/@@HEIGHT@@/$height/g" Phomemo_Q22.template
done
```

---

## `phomemo-tools/images/LICENSE`

**Lines 0-0**

The license notice is non-standard and may create legal uncertainty. Consider using a well-known permissive license (such as MIT, Apache 2.0) or a public domain dedication (CC0) for clarity and to ensure compatibility with common open-source practices.

---

## `phomemo-tools/tools/Makefile`

**Lines 0-0**

The targets 'all' and 'install' are not marked as phony. It is recommended to declare them as phony to avoid potential conflicts with files named 'all' or 'install' in the directory.

**Suggested fix:**
```diff
- all:

install:
+ .PHONY: all install

all:

install:
```

---

## `phomemo-tools/tools/format-checker.py`

**Lines 38-39**

The image is created in mode '1' (1-bit) which only accepts pixel values 0 or 1, but the code attempts to set pixels to 0 or 255 via multiplication. This will raise a ValueError when the script runs. Change the pixel value to 0 or 1 by removing the multiplication by 255, or change the image mode to 'L' (grayscale) if 0-255 is intended.

**Suggested fix:**
```diff
-                     value = (1 - (byte >> (7 - bit) & 1)) * 255
                    image.putpixel((bytes * 8 + bit, line), value)
+                     value = 1 - (byte >> (7 - bit) & 1)
                    image.putpixel((bytes * 8 + bit, line), value)
```

---

**Lines 10-18**

The script uses assert statements for validating the printer format protocol. Assertions can be disabled when running Python with the -O optimization flag, potentially allowing the tool to skip critical format checks and produce incorrect output on malformed input. Replace assert statements with proper error handling (e.g., raising ValueError) for critical validation checks.

**Suggested fix:**
```diff
- assert stdin.read(1) == b'\x1b'
assert stdin.read(1) == b'\x40'
assert stdin.read(1) == b'\x1b'
assert stdin.read(1) == b'\x61'
assert stdin.read(1) == b'\x01'
assert stdin.read(1) == b'\x1f'
assert stdin.read(1) == b'\x11'
assert stdin.read(1) == b'\x02'
assert stdin.read(1) == b'\x04'
+     if stdin.read(1) != b'\x1b':
        raise ValueError('Expected ESC byte')
    if stdin.read(1) != b'\x40':
        raise ValueError('Expected @ byte')
    if stdin.read(1) != b'\x1b':
        raise ValueError('Expected ESC byte')
    if stdin.read(1) != b'\x61':
        raise ValueError('Expected a byte')
    if stdin.read(1) != b'\x01':
        raise ValueError('Expected 0x01 byte')
    if stdin.read(1) != b'\x1f':
        raise ValueError('Expected US byte')
    if stdin.read(1) != b'\x11':
        raise ValueError('Expected DC1 byte')
    if stdin.read(1) != b'\x02':
        raise ValueError('Expected STX byte')
    if stdin.read(1) != b'\x04':
        raise ValueError('Expected EOT byte')
```

---

**Lines 0-0**

The script lacks a module docstring. Add a docstring at the top of the file (after the shebang) explaining the purpose, usage, and behavior of the script.

**Suggested fix:**
```diff
- #! /usr/bin/python3

import sys, os
from PIL import Image

image = Image.new('1', (384, 2048))
+ #! /usr/bin/python3
"""
Format checker for Phomemo printer output.
Reads printer format data from stdin, processes it to generate a binary image,
and saves/displays the image for visual verification.
"""
import sys, os
from PIL import Image

image = Image.new('1', (384, 2048))
```

---

**Lines 0-0**

The script lacks a `if __name__ == '__main__':` guard, causing the main logic to execute when the module is imported. This could lead to unintended behavior if the module is imported elsewhere, as it will attempt to read from stdin and process data. Wrap the main logic in a function or use the `if __name__ == '__main__':` guard.

**Suggested fix:**
```diff
- #! /usr/bin/python3

import sys, os
from PIL import Image

image = Image.new('1', (384, 2048))

with os.fdopen(sys.stdin.fileno(), "rb", closefd=False) as stdin:
    # HEADER
    assert stdin.read(1) == b'\x1b'
    assert stdin.read(1) == b'@'
    assert stdin.read(1) == b'\x1b'
    assert stdin.read(1) == b'a'
    assert stdin.read(1) == b'\x01'
    assert stdin.read(1) == b'\x1f'
    assert stdin.read(1) == b'\x11'
    assert stdin.read(1) == b'\x02'
    assert stdin.read(1) == b'\x04'

    block = 0
    line=0
    while 1:
        tag = stdin.read(1)
        if tag == b'\x1b' or tag == b'':
            break
        assert tag == b'\x1d'
        assert stdin.read(1) == b'v'
        assert int.from_bytes(stdin.read(2), "little") == 0x0030
        assert int.from_bytes(stdin.read(2), "little") == 0x0030
        lines = int.from_bytes(stdin.read(2), "little") + 1
        assert lines != 0
        print("Block %d has %d lines" %(block, lines))
        while lines:
            for bytes in range(48):
                byte = int.from_bytes(stdin.read(1), 'little');
                assert byte != 0x0a
                for bit in range(8):
                    value = (1 - (byte >> (7 - bit) & 1)) * 255
                    image.putpixel((bytes * 8 + bit, line), value)
            lines -= 1
            line += 1
            if line >= image.height:
                break;
        if line >= image.height:
            break;
        block += 1
    
    # footer
    if tag == b'\x1b':
        assert stdin.read(1) == b'd'
        assert stdin.read(1) == b'\x02'

        assert stdin.read(1) == b'\x1b'
        assert stdin.read(1) == b'd'
        assert stdin.read(1) == b'\x02'

        assert stdin.read(1) == b'\x1f'
        assert stdin.read(1) == b'\x11'
        assert stdin.read(1) == b'\x08'

        assert stdin.read(1) == b'\x1f'
        assert stdin.read(1) == b'\x11'
        assert stdin.read(1) == b'\x0e'

        assert stdin.read(1) == b'\x1f'
        assert stdin.read(1) == b'\x11'
        assert stdin.read(1) == b'\x07'

        assert stdin.read(1) == b'\x1f'
        assert stdin.read(1) == b'\x11'
        assert stdin.read(1) == b'\x09'

image = image.crop((0, 0, image.width, line))
image.save('image-checker.png')
image.show()
+ #! /usr/bin/python3
"""
Format checker for Phomemo printer output.
Reads printer format data from stdin, processes it to generate a binary image,
and saves/displays the image for visual verification.
"""
import sys, os
from PIL import Image

def main():
    image = Image.new('1', (384, 2048))

    with os.fdopen(sys.stdin.fileno(), "rb", closefd=False) as stdin:
        # HEADER
        if stdin.read(1) != b'\x1b':
            raise ValueError('Expected ESC byte')
        if stdin.read(1) != b'\x40':
            raise ValueError('Expected @ byte')
        if stdin.read(1) != b'\x1b':
            raise ValueError('Expected ESC byte')
        if stdin.read(1) != b'\x61':
            raise ValueError('Expected a byte')
        if stdin.read(1) != b'\x01':
            raise ValueError('Expected 0x01 byte')
        if stdin.read(1) != b'\x1f':
            raise ValueError('Expected US byte')
        if stdin.read(1) != b'\x11':
            raise ValueError('Expected DC1 byte')
        if stdin.read(1) != b'\x02':
            raise ValueError('Expected STX byte')
        if stdin.read(1) != b'\x04':
            raise ValueError('Expected EOT byte')

        block = 0
        line = 0
        while True:
            tag = stdin.read(1)
            if tag == b'\x1b' or tag == b'':
                break
            if tag != b'\x1d':
                raise ValueError('Expected GS byte')
            if stdin.read(1) != b'v':
                raise ValueError('Expected v byte')
            if int.from_bytes(stdin.read(2), "little") != 0x0030:
                raise ValueError('Expected x offset 0x0030')
            if int.from_bytes(stdin.read(2), "little") != 0x0030:
                raise ValueError('Expected y offset 0x0030')
            lines = int.from_bytes(stdin.read(2), "little") + 1
            if lines == 0:
                raise ValueError('Lines cannot be zero')
            print(f"Block {block} has {lines} lines")
            while lines:
                for bytes in range(48):
                    byte = int.from_bytes(stdin.read(1), 'little')
                    if byte == 0x0a:
                        raise ValueError('Unexpected LF byte')
                    for bit in range(8):
                        value = 1 - (byte >> (7 - bit) & 1)
                        image.putpixel((bytes * 8 + bit, line), value)
                lines -= 1
                line += 1
                if line >= image.height:
                    break
            if line >= image.height:
                break
            block += 1
    
    # footer
    if tag == b'\x1b':
        if stdin.read(1) != b'd':
            raise ValueError('Expected d byte')
        if stdin.read(1) != b'\x02':
            raise ValueError('Expected 0x02 byte')

        if stdin.read(1) != b'\x1b':
            raise ValueError('Expected ESC byte')
        if stdin.read(1) != b'd':
            raise ValueError('Expected d byte')
        if stdin.read(1) != b'\x02':
            raise ValueError('Expected 0x02 byte')

        if stdin.read(1) != b'\x1f':
            raise ValueError('Expected US byte')
        if stdin.read(1) != b'\x11':
            raise ValueError('Expected DC1 byte')
        if stdin.read(1) != b'\x08':
            raise ValueError('Expected 0x08 byte')

        if stdin.read(1) != b'\x1f':
            raise ValueError('Expected US byte')
        if stdin.read(1) != b'\x11':
            raise ValueError('Expected DC1 byte')
        if stdin.read(1) != b'\x0e':
            raise ValueError('Expected 0x0e byte')

        if stdin.read(1) != b'\x1f':
            raise ValueError('Expected US byte')
        if stdin.read(1) != b'\x11':
            raise ValueError('Expected DC1 byte')
        if stdin.read(1) != b'\x07':
            raise ValueError('Expected 0x07 byte')

        if stdin.read(1) != b'\x1f':
            raise ValueError('Expected US byte')
        if stdin.read(1) != b'\x11':
            raise ValueError('Expected DC1 byte')
        if stdin.read(1) != b'\x09':
            raise ValueError('Expected 0x09 byte')

    image = image.crop((0, 0, image.width, line))
    image.save('image-checker.png')
    image.show()

if __name__ == '__main__':
    main()
```

---

## `phomemo-tools/tools/phomemo-filter.py`

**Lines 57-62**

Bare except clause catches all exceptions, including KeyboardInterrupt and SystemExit, which can interfere with proper error handling and debugging. Replace with `except Exception as e:` to catch only expected exceptions, and consider printing the exception details for better debugging. Also, note that `parser.print_usage()` is not appropriate for file opening errors; consider removing it or using it only for argument parsing errors.

**Suggested fix:**
```diff
- try:
    image = Image.open(args.file)
except:
    print("Cannot open file", args.file)
    parser.print_usage()
    sys.exit(2)
+ try:
    image = Image.open(args.file)
except Exception as e:
    print(f"Cannot open file {args.file}: {e}")
    sys.exit(2)
```

---

**Lines 0-0**

Missing `if __name__ == '__main__':` guard. The script's main execution block runs at module level, which causes the script to execute its main logic when imported, leading to unintended side effects and potential failures due to missing command-line arguments. Wrap the main execution block in a `if __name__ == '__main__':` guard.

**Suggested fix:**
```diff
- parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument("--no-rotate", action="store_true", help="Disable auto-rotation of the image")
parser.add_argument("file")

args = parser.parse_args()

try:
    image = Image.open(args.file)
except:
    print("Cannot open file", args.file)
    parser.print_usage()
    sys.exit(2)

if not args.no_rotate:
    if image.width > image.height:
        image = image.transpose(Image.ROTATE_90)

# width 384 dots
image = image.resize(size=(384, int(image.height * 384 / image.width)))

# black&white printer: dithering
image = image.convert(mode='1')

remaining = image.height
line=0
print_header()
while remaining > 0:
    lines = remaining
    if lines > 256:
        lines = 256
    print_marker(lines)
    remaining -= lines
    while lines > 0:
        print_line(image, line)
        lines -= 1
        line += 1
print_footer()
+ if __name__ == '__main__':
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--no-rotate", action="store_true", help="Disable auto-rotation of the image")
    parser.add_argument("file")

    args = parser.parse_args()

    try:
        image = Image.open(args.file)
    except Exception as e:
        print(f"Cannot open file {args.file}: {e}")
        sys.exit(2)

    if not args.no_rotate:
        if image.width > image.height:
            image = image.transpose(Image.ROTATE_90)

    # width 384 dots
    image = image.resize(size=(384, int(image.height * 384 / image.width)))

    # black&white printer: dithering
    image = image.convert(mode='1')

    remaining = image.height
    line = 0
    print_header()
    while remaining > 0:
        lines = remaining
        if lines > 256:
            lines = 256
        print_marker(lines)
        remaining -= lines
        while lines > 0:
            print_line(image, line)
            lines -= 1
            line += 1
    print_footer()
```

---

**Lines 0-0**

Inefficient resource management: print_header, print_marker, print_footer, and print_line functions reopen sys.stdout in binary mode for every call, causing unnecessary overhead and potential issues in non-seekable streams. Consider opening sys.stdout.buffer once at the beginning and reusing it, or passing it as a parameter to these functions.

**Suggested fix:**
```diff
- def print_header():
    with os.fdopen(sys.stdout.fileno(), "wb", closefd=False) as stdout:
        stdout.write(b'\x1b\x40\x1b\x61\x01\xf\x11\x02\x04')
    return
+ def print_header():
    stdout = sys.stdout.buffer
    stdout.write(b'\x1b\x40\x1b\x61\x01\xf\x11\x02\x04')
    return
```

---

**Lines 18-24**

Inefficient resource management: print_header, print_marker, print_footer, and print_line functions reopen sys.stdout in binary mode for every call, causing unnecessary overhead and potential issues in non-seekable streams. Consider opening sys.stdout.buffer once at the beginning and reusing it, or passing it as a parameter to these functions.

**Suggested fix:**
```diff
- def print_marker(lines=0x100):
    with os.fdopen(sys.stdout.fileno(), "wb", closefd=False) as stdout:
        stdout.write(0x761d.to_bytes(2, 'little'))
        stdout.write(0x0030.to_bytes(2, 'little'))
        stdout.write(0x0030.to_bytes(2, 'little'))
        stdout.write((lines - 1).to_bytes(2, 'little'))
    return
+ def print_marker(lines=0x100):
    stdout = sys.stdout.buffer
    stdout.write(0x761d.to_bytes(2, 'little'))
    stdout.write(0x0030.to_bytes(2, 'little'))
    stdout.write(0x0030.to_bytes(2, 'little'))
    stdout.write((lines - 1).to_bytes(2, 'little'))
    return
```

---

**Lines 13-16**

Function lacks type hints and docstring, and inefficiently reopens sys.stdout buffer on each call. Add type hints (-> None) and a docstring describing the function's purpose. Open sys.stdout.buffer once and reuse it for efficiency.

**Suggested fix:**
```diff
- def print_header():
    with os.fdopen(sys.stdout.fileno(), "wb", closefd=False) as stdout:
        stdout.write(b'\x1b\x40\x1b\x61\x01\x1f\x11\x02\x04')
    return
+ def print_header() -> None:
    """Print header to initialize the printer."""
    stdout = sys.stdout.buffer
    stdout.write(b'\x1b\x40\x1b\x61\x01\x1f\x11\x02\x04')

```

---

**Lines 18-24**

Function lacks type hints and docstring, and inefficiently reopens sys.stdout buffer on each call. Add type hints (-> None) and a docstring describing the function's purpose. Open sys.stdout.buffer once and reuse it for efficiency.

**Suggested fix:**
```diff
- def print_marker(lines=0x100):
    with os.fdopen(sys.stdout.fileno(), "wb", closefd=False) as stdout:
        stdout.write(0x761d.to_bytes(2, 'little'))
        stdout.write(0x0030.to_bytes(2, 'little'))
        stdout.write(0x0030.to_bytes(2, 'little'))
        stdout.write((lines - 1).to_bytes(2, 'little'))
    return
+ def print_marker(lines=0x100) -> None:
    """Print a marker for the given number of lines."""
    stdout = sys.stdout.buffer
    stdout.write(0x761d.to_bytes(2, 'little'))
    stdout.write(0x0030.to_bytes(2, 'little'))
    stdout.write(0x0030.to_bytes(2, 'little'))
    stdout.write((lines - 1).to_bytes(2, 'little'))
```

---

**Lines 26-34**

Function lacks type hints and docstring, and inefficiently reopens sys.stdout buffer on each call. Add type hints (-> None) and a docstring describing the function's purpose. Open sys.stdout.buffer once and reuse it for efficiency.

**Suggested fix:**
```diff
- def print_footer():
    with os.fdopen(sys.stdout.fileno(), "wb", closefd=False) as stdout:
        stdout.write(b'\x1b\x64\x02')
        stdout.write(b'\x1b\x64\x02')
        stdout.write(b'\x1f\x11\x08')
        stdout.write(b'\x1f\x11\x0e')
        stdout.write(b'\x1f\x11\x07')
        stdout.write(b'\x1f\x11\x09')
    return
+ def print_footer() -> None:
    """Print footer to finalize printing."""
    stdout = sys.stdout.buffer
    stdout.write(b'\x1b\x64\x02')
    stdout.write(b'\x1b\x64\x02')
    stdout.write(b'\x1f\x11\x08')
    stdout.write(b'\x1f\x11\x0e')
    stdout.write(b'\x1f\x11\x07')
    stdout.write(b'\x1f\x11\x09')
```

---

**Lines 36-48**

Function lacks type hints and docstring, and inefficiently reopens sys.stdout buffer on each call. Also, the logic for handling byte == 0x0a is unclear and could be improved. Add type hints (-> None) and a docstring describing the function's purpose. Open sys.stdout.buffer once and reuse it for efficiency.

**Suggested fix:**
```diff
- def print_line(image, line):
    with os.fdopen(sys.stdout.fileno(), "wb", closefd=False) as stdout:
        for x in range(int(image.width / 8)):
            byte = 0
            for bit in range(8):
                if image.getpixel((x * 8 + bit, line)) == 0:
                    byte |= 1 << (7 - bit)
            # 0x0a breaks the rendering
            # 0x0a alone is processed like LineFeed by the printe
            if byte == 0x0a:
                byte = 0x14
            stdout.write(byte.to_bytes(1, 'little'))
    return
+ def print_line(image, line) -> None:
    """Print a single line of the image to the printer."""
    stdout = sys.stdout.buffer
    for x in range(int(image.width / 8)):
        byte = 0
        for bit in range(8):
            if image.getpixel((x * 8 + bit, line)) == 0:
                byte |= 1 << (7 - bit)
        # 0x0a breaks the rendering
        # 0x0a alone is processed like LineFeed by the printer
        if byte == 0x0a:
            byte = 0x14
        stdout.write(byte.to_bytes(1, 'little'))
```

---

## `pyproject.toml`

**Lines 25-26**

The wheel configuration currently only includes the 'commands' package. If the CLI depends on other local packages (such as the plant_service package), they will not be included in the built wheel. Please verify that all necessary packages are included or listed as dependencies.

---

## `scripts/migrate_genera.py`

**Lines 25-25**

The return type annotation is too vague. Should specify the type of elements in the list for better type safety and readability. Use string annotation to avoid importing Plant class in this module.

**Suggested fix:**
```diff
- def load_all_plants(database_dir: Path) -> list:
+ def load_all_plants(database_dir: Path) -> 'list[Plant]':
```

---

**Lines 36-36**

Parameter and return type annotations are too vague. Should specify the element types for better type safety. Use string annotations to avoid importing Plant class in this module.

**Suggested fix:**
```diff
- def group_plants(plants: list) -> dict:
+ def group_plants(plants: 'list[Plant]') -> dict[tuple[str, str], 'list[Plant]']:
```

---

**Lines 48-48**

Missing return type annotation. Should indicate that the function may return a Genus instance or None.

**Suggested fix:**
```diff
- def find_existing_genus(variety_name: str, latin_name: str, genera_dir: Path):
+ def find_existing_genus(variety_name: str, latin_name: str, genera_dir: Path) -> 'Optional[Genus]':
```

---

**Lines 85-85**

Parameter 'plant' lacks type annotation. Should be annotated as Plant instance for better type safety. Use string annotation to avoid importing Plant class in this module.

**Suggested fix:**
```diff
- def update_plant_file(plant, filepath: Path, genus_id: str, dry_run: bool) -> bool:
+ def update_plant_file(plant: 'Plant', filepath: Path, genus_id: str, dry_run: bool) -> bool:
```

---

**Lines 0-0**

Missing explicit return type annotation. Should be annotated as -> None for clarity.

**Suggested fix:**
```diff
- def migrate(database_dir: Path, genera_dir: Path, dry_run: bool = False):
+ def migrate(database_dir: Path, genera_dir: Path, dry_run: bool = False) -> None:
```

---

**Lines 197-197**

Missing return type annotation. Should be annotated as -> None for clarity.

**Suggested fix:**
```diff
- def main():
+ def main() -> None:
```

---

## `scripts/migrate_planting_date.py`

**Lines 21-25**

Add a docstring to the migrate function explaining its purpose, arguments, and behavior.

**Suggested fix:**
```diff
- def migrate(database_dir: Path, dry_run: bool = False) -> None:
    print("=" * 60)
    print("Planting Date Field Migration")
    print("=" * 60)
    print()
+ def migrate(database_dir: Path, dry_run: bool = False) -> None:
    """
    Migrate plant records by renaming planned_planting_date to planting_date in markdown files.

    Args:
        database_dir: Path to directory containing plant markdown files.
        dry_run: If True, only show what would be changed without applying.
    """
    print("=" * 60)
    print("Planting Date Field Migration")
    print("=" * 60)
    print()
```

---

**Lines 0-0**

Add a docstring to the main function explaining its purpose and arguments.

**Suggested fix:**
```diff
- def main():
    parser = argparse.ArgumentParser(description="Migrate planned_planting_date -> planting_date")
    parser.add_argument('--dry-run', action='store_true', help='Show what would change without applying')
    args = parser.parse_args()

    database_dir = get_database_dir()

    if not database_dir.exists():
        print(f"Error: Database directory not found: {database_dir}")
        sys.exit(1)

    migrate(database_dir, args.dry_run)
+ def main():
    """
    Parse command line arguments and run the migration.

    Args:
        None
    """
    parser = argparse.ArgumentParser(description="Migrate planned_planting_date -> planting_date")
    parser.add_argument('--dry-run', action='store_true', help='Show what would change without applying')
    args = parser.parse_args()

    database_dir = get_database_dir()

    if not database_dir.exists():
        print(f"Error: Database directory not found: {database_dir}")
        sys.exit(1)

    migrate(database_dir, args.dry_run)
```

---

## `scripts/migrate_seed_packets.py`

**Lines 136-136**

High severity: The script checks only the first plant in a group (plant_list[0]) to determine if the group has any seed packet data. If the first plant lacks packet data but other plants in the group have it, the group will be incorrectly marked as having no packet data, leading to missing seed packet creation and incorrect 'unknown' assignments. This could result in data loss where valid seed packet information is not preserved.\n\nFix: Change the condition to check if any plant in the group has packet data using `any(has_packet_data(plant) for plant in plant_list)`.

**Suggested fix:**
```diff
-         packet_data = has_packet_data(plant_list[0])
+         packet_data = any(has_packet_data(plant) for plant in plant_list)
```

---

**Lines 162-168**

High severity: The script does not validate that plant records contain an 'id' field before using it to construct file paths. If a plant record is missing the 'id' field (e.g., due to corrupted data), a KeyError will be raised when accessing plant.data['id'], potentially crashing the migration and leaving the database in an inconsistent state.\n\nFix: Add a check for the 'id' field before using it. If missing, skip the plant and log a warning.

**Suggested fix:**
```diff
-     for plant in plants:
            group_key = (plant.data.get('variety_name', ''), plant.data.get('latin_name', ''))
            packet_id = packet_map[group_key]
            filepath = database_dir / f"{plant.data['id']}.md"
            if update_plant_file(plant, filepath, packet_id):
                updated_count += 1
                changes.append((plant.data['id'], packet_id))
+     for plant in plants:
            plant_id = plant.data.get('id')
            if plant_id is None:
                print(f"  ⚠ Skipping plant {plant.data.get('variety_name', 'unknown')}: missing 'id' field")
                continue
            group_key = (plant.data.get('variety_name', ''), plant.data.get('latin_name', ''))
            packet_id = packet_map[group_key]
            filepath = database_dir / f"{plant_id}.md"
            if update_plant_file(plant, filepath, packet_id):
                updated_count += 1
                changes.append((plant_id, packet_id))
```

---

**Lines 11-11**

Medium severity: The script contains unused imports: 'copy' and 'yaml'. The 'copy' module is imported but never used, and 'yaml' is imported but not referenced anywhere in the provided code. These unused imports reduce code clarity and may indicate dead code or incomplete implementation.

**Suggested fix:**
```diff
- import copy
+ # Removed unused imports: copy and yaml
# import copy
# import yaml
```

---

**Lines 189-189**

Test comment

---

**Lines 142-145**

Low severity: In the migrate function, when printing representative data for a group during dry run, the script builds a dictionary `rep_display` from the representative data. If the representative is empty (all packet fields are empty), it will print an empty dict ({}), which may be confusing to users. Consider adding a conditional message to clarify when no packet data is available for the group.

**Suggested fix:**
```diff
-             if dry_run:
                print(f"  Would create seed packet with: {rep_display}")
                print(f"  Would assign ID: SPKT-??? (auto-generated)")
                packet_id = "SPKT-???"
+             if dry_run:
                if rep_display:
                    print(f"  Would create seed packet with: {rep_display}")
                else:
                    print(f"  Would create seed packet with: (no packet data)")
                print(f"  Would assign ID: SPKT-??? (auto-generated)")
                packet_id = "SPKT-???"
```

---

**Lines 0-0**

Medium severity: Several functions are missing type hints for parameters and/or return values. Adding type hints would improve code readability, maintainability, and help catch type-related errors early.\n\nFunctions needing type hints: has_packet_data, pick_representative, create_packet_from_group, update_plant_file, migrate (return type), main.

**Suggested fix:**
```diff
- def has_packet_data(plant):
    """Check if a plant has any seed packet fields beyond required fields."""
    for field in PACKET_FIELDS:
        if plant.data.get(field):
            return True
    return False

def pick_representative(plant_list: list) -> dict:
    """Pick representative values for a group of plants. 
    
    For each packet field, picks the most common non-empty value."""
    rep = {}
    for field in PACKET_FIELDS:
        values = [p.data.get(field) for p in plant_list if p.data.get(field)]
        if values:
            counts = defaultdict(int)
            for v in values:
                counts[v] += 1
            rep[field] = max(counts, key=counts.get)
    return rep

def create_packet_from_group(group_key, representative: dict, packets_dir: Path) -> SeedPacket:
    """Create a SeedPacket record from a group's representative data."""
    packet_data = {
        'variety_name': group_key[0],
        'latin_name': group_key[1],
    }
    packet_data.update(representative)
    packet = SeedPacket(packet_data)
    filepath = packets_dir / f"{packet.data['id']}.md"
    with open(filepath, 'w') as f:
        f.write(packet.to_markdown())
    return packet

def update_plant_file(plant, filepath: Path, packet_id: str) -> bool:
    """Add seed_packet_id to a plant's frontmatter and save. 
    
    Returns True if file was changed."""
    if plant.data.get('seed_packet_id'):
        return False

    plant.data['seed_packet_id'] = packet_id
    plant.data['updated_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    md_content = plant.to_markdown()
    with open(filepath, 'w') as f:
        f.write(md_content)
    return True

def migrate(database_dir: Path, packets_dir: Path, dry_run: bool = False) -> None:
    """Run the migration."""
    # ... function body
+ def has_packet_data(plant) -> bool:
    """Check if a plant has any seed packet fields beyond required fields."""
    for field in PACKET_FIELDS:
        if plant.data.get(field):
            return True
    return False

def pick_representative(plant_list: list) -> dict:
    """Pick representative values for a group of plants. 
    
    For each packet field, picks the most common non-empty value."""
    rep = {}
    for field in PACKET_FIELDS:
        values = [p.data.get(field) for p in plant_list if p.data.get(field)]
        if values:
            counts = defaultdict(int)
            for v in values:
                counts[v] += 1
            rep[field] = max(counts, key=counts.get)
    return rep

def create_packet_from_group(group_key: tuple, representative: dict, packets_dir: Path) -> SeedPacket:
    """Create a SeedPacket record from a group's representative data."""
    packet_data = {
        'variety_name': group_key[0],
        'latin_name': group_key[1],
    }
    packet_data.update(representative)
    packet = SeedPacket(packet_data)
    filepath = packets_dir / f"{packet.data['id']}.md"
    with open(filepath, 'w') as f:
        f.write(packet.to_markdown())
    return packet

def update_plant_file(plant, filepath: Path, packet_id: str) -> bool:
    """Add seed_packet_id to a plant's frontmatter and save. 
    
    Returns True if file was changed."""
    if plant.data.get('seed_packet_id'):
        return False

    plant.data['seed_packet_id'] = packet_id
    plant.data['updated_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    md_content = plant.to_markdown()
    with open(filepath, 'w') as f:
        f.write(md_content)
    return True

def migrate(database_dir: Path, packets_dir: Path, dry_run: bool = False) -> None:
    """Run the migration."""
    # ... function body
```

---

**Lines 0-0**

Medium severity: The script lacks docstrings for several functions. Adding docstrings would improve maintainability and help users understand the purpose, parameters, return values, and side effects of each function.\n\nFunctions missing docstrings: group_plants, pick_representative, create_packet_from_group, update_plant_file, migrate.

**Suggested fix:**
```diff
- def group_plants(plants: list) -> dict:
    """Group plants by (variety_name, latin_name). 
    
    Returns dict of (variety_name, latin_name) -> [plants]."""
    groups = defaultdict(list)
    for plant in plants:
        key = (plant.data.get('variety_name', ''), plant.data.get('latin_name', ''))
        groups[key].append(plant)
    return dict(groups)

def pick_representative(plant_list: list) -> dict:
    """Pick representative values for a group of plants. 
    
    For each packet field, picks the most common non-empty value."""
    rep = {}
    for field in PACKET_FIELDS:
        values = [p.data.get(field) for p in plant_list if p.data.get(field)]
        if values:
            counts = defaultdict(int)
            for v in values:
                counts[v] += 1
            rep[field] = max(counts, key=counts.get)
    return rep

def create_packet_from_group(group_key, representative: dict, packets_dir: Path) -> SeedPacket:
    """Create a SeedPacket record from a group's representative data."""
    packet_data = {
        'variety_name': group_key[0],
        'latin_name': group_key[1],
    }
    packet_data.update(representative)
    packet = SeedPacket(packet_data)
    filepath = packets_dir / f"{packet.data['id']}.md"
    with open(filepath, 'w') as f:
        f.write(packet.to_markdown())
    return packet

def update_plant_file(plant, filepath: Path, packet_id: str) -> bool:
    """Add seed_packet_id to a plant's frontmatter and save. 
    
    Returns True if file was changed."""
    if plant.data.get('seed_packet_id'):
        return False

    plant.data['seed_packet_id'] = packet_id
    plant.data['updated_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    md_content = plant.to_markdown()
    with open(filepath, 'w') as f:
        f.write(md_content)
    return True

def migrate(database_dir: Path, packets_dir: Path, dry_run: bool = False) -> None:
    """Run the migration."""
    # ... function body
+ def group_plants(plants: list) -> dict:
    """Group plants by (variety_name, latin_name). 
    
    Args:
        plants: List of plant objects to group.
        
    Returns:
        dict: Mapping of (variety_name, latin_name) tuples to lists of plant objects."""
    groups = defaultdict(list)
    for plant in plants:
        key = (plant.data.get('variety_name', ''), plant.data.get('latin_name', ''))
        groups[key].append(plant)
    return dict(groups)

def pick_representative(plant_list: list) -> dict:
    """Pick representative values for a group of plants. 
    
    For each packet field, picks the most common non-empty value.
    
    Args:
        plant_list: List of plant objects in the same variety group.
        
    Returns:
        dict: Dictionary mapping packet field names to their most common non-empty values."""
    rep = {}
    for field in PACKET_FIELDS:
        values = [p.data.get(field) for p in plant_list if p.data.get(field)]
        if values:
            counts = defaultdict(int)
            for v in values:
                counts[v] += 1
            rep[field] = max(counts, key=counts.get)
    return rep

def create_packet_from_group(group_key: tuple, representative: dict, packets_dir: Path) -> SeedPacket:
    """Create a SeedPacket record from a group's representative data.
    
    Args:
        group_key: Tuple of (variety_name, latin_name) for the group.
        representative: Dictionary of packet field values to use for the seed packet.
        packets_dir: Directory where seed packet files should be saved.
        
    Returns:
        SeedPacket: The created seed packet object."""
    packet_data = {
        'variety_name': group_key[0],
        'latin_name': group_key[1],
    }
    packet_data.update(representative)
    packet = SeedPacket(packet_data)
    filepath = packets_dir / f"{packet.data['id']}.md"
    with open(filepath, 'w') as f:
        f.write(packet.to_markdown())
    return packet

def update_plant_file(plant, filepath: Path, packet_id: str) -> bool:
    """Add seed_packet_id to a plant's frontmatter and save. 
    
    Args:
        plant: Plant object to update.
        filepath: Path to the plant's markdown file.
        packet_id: ID of the seed packet to associate with the plant.
        
    Returns:
        bool: True if the file was modified, False if it already had a seed_packet_id."""
    if plant.data.get('seed_packet_id'):
        return False

    plant.data['seed_packet_id'] = packet_id
    plant.data['updated_at'] = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%SZ')

    md_content = plant.to_markdown()
    with open(filepath, 'w') as f:
        f.write(md_content)
    return True

def migrate(database_dir: Path, packets_dir: Path, dry_run: bool = False) -> None:
    """Run the migration to extract unique seed packets from plants and backfill seed_packet_id.
    
    Args:
        database_dir: Directory containing plant markdown files.
        packets_dir: Directory where seed packet markdown files will be created.
        dry_run: If True, only show what would be changed without making changes."""
    # ... function body
```

---

## `scripts/migrate_to_postgres.py`

**Lines 239-247**

The migrate_log_entries function only maps specific known fields for each event type (water: amount_ml; fertilizer: fertilizer_type/strength; humidity: level; note: text). Any additional fields in the markdown log data for these event types will be lost during migration, as the PlantLogEntry model doesn't have generic storage for extra fields. Consider either: 1) Adding a mechanism to preserve extra fields (e.g., a JSON column for custom data), 2) Logging a warning when extra fields are encountered, or 3) Validating that no extra fields exist beyond the expected ones.

**Suggested fix:**
```diff
-                 if entry_data["event_type"] == "water" and "amount_ml" in entry_data:
                    orm_data["amount_ml"] = int(entry_data["amount_ml"])
                elif entry_data["event_type"] == "fertilizer":
                    orm_data["fertilizer_type"] = entry_data.get("type")
                    orm_data["fertilizer_strength"] = entry_data.get("strength")
                elif entry_data["event_type"] == "humidity":
                    orm_data["level"] = entry_data.get("level")
                elif entry_data["event_type"] == "note":
                    orm_data["text"] = entry_data.get("text")
+                 # Handle event-type specific fields
                extra_fields = set(entry_data.keys()) - {"plant_id", "event_type", "timestamp"}
                if entry_data["event_type"] == "water" and "amount_ml" in entry_data:
                    orm_data["amount_ml"] = int(entry_data["amount_ml"])
                    extra_fields.discard("amount_ml")
                elif entry_data["event_type"] == "fertilizer":
                    if "type" in entry_data:
                        orm_data["fertilizer_type"] = entry_data.get("type")
                        extra_fields.discard("type")
                    if "strength" in entry_data:
                        orm_data["fertilizer_strength"] = entry_data.get("strength")
                        extra_fields.discard("strength")
                elif entry_data["event_type"] == "humidity" and "level" in entry_data:
                    orm_data["level"] = entry_data.get("level")
                    extra_fields.discard("level")
                elif entry_data["event_type"] == "note" and "text" in entry_data:
                    orm_data["text"] = entry_data.get("text")
                    extra_fields.discard("text")
                
                # Warn about any remaining extra fields that weren't mapped
                if extra_fields:
                    print(f"Warning: Ignoring extra fields for {entry_data['event_type']} event: {extra_fields}")
```

---

**Lines 83-85**

Broad Exception handling in migrate_seed_packets, migrate_genera, migrate_plants, and migrate_log_entries catches all exceptions, potentially hiding programming errors (e.g., AttributeError, KeyError) and leading to silent failures where records are skipped without clear diagnostics. The load_*_from_file functions can raise ValueError, FileNotFoundError, yaml.YAMLError, and database operations can raise SQLAlchemy errors. Consider catching more specific exceptions and re-raising or logging with traceback for unexpected errors.

**Suggested fix:**
```diff
-             except Exception as e:
                print(f"Error migrating seed packet {packet_file}: {e}")
                continue
+             except (ValueError, FileNotFoundError, yaml.YAMLError) as e:
                print(f"Error loading seed packet {packet_file}: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error migrating seed packet {packet_file}: {e}")
                # Consider re-raising or logging with traceback for debugging
                # raise  # Uncomment for debugging during development
                continue
```

---

**Lines 130-132**

Broad Exception handling in migrate_seed_packets, migrate_genera, migrate_plants, and migrate_log_entries catches all exceptions, potentially hiding programming errors (e.g., AttributeError, KeyError) and leading to silent failures where records are skipped without clear diagnostics. The load_*_from_file functions can raise ValueError, FileNotFoundError, yaml.YAMLError, and database operations can raise SQLAlchemy errors. Consider catching more specific exceptions and re-raising or logging with traceback for unexpected errors.

**Suggested fix:**
```diff
-             except Exception as e:
                print(f"Error migrating genus {genus_file}: {e}")
                continue
+             except (ValueError, FileNotFoundError, yaml.YAMLError) as e:
                print(f"Error loading genus {genus_file}: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error migrating genus {genus_file}: {e}")
                # Consider re-raising or logging with traceback for debugging
                # raise  # Uncomment for debugging during development
                continue
```

---

**Lines 191-193**

Broad Exception handling in migrate_seed_packets, migrate_genera, migrate_plants, and migrate_log_entries catches all exceptions, potentially hiding programming errors (e.g., AttributeError, KeyError) and leading to silent failures where records are skipped without clear diagnostics. The load_*_from_file functions can raise ValueError, FileNotFoundError, yaml.YAMLError, and database operations can raise SQLAlchemy errors. Consider catching more specific exceptions and re-raising or logging with traceback for unexpected errors.

**Suggested fix:**
```diff
-             except Exception as e:
                print(f"Error migrating plant {plant_file}: {e}")
                continue
+             except (ValueError, FileNotFoundError, yaml.YAMLError) as e:
                print(f"Error loading plant {plant_file}: {e}")
                continue
            except Exception as e:
                print(f"Unexpected error migrating plant {plant_file}: {e}")
                # Consider re-raising or logging with traceback for debugging
                # raise  # Uncomment for debugging during development
                continue
```

---

**Lines 37-38**

The backup function uses a timestamp with second granularity, risking failure if two backups are initiated within the same second due to the destination directory already existing. Consider adding microseconds or a random string to ensure uniqueness.

**Suggested fix:**
```diff
-     timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_dir = database_dir.parent / f"database_backup_{timestamp}"
+     # Use microseconds for higher precision to avoid conflicts
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
    backup_dir = database_dir.parent / f"database_backup_{timestamp}"
```

---

## `tests/test_plant_tracking.py`

**Lines 0-0**

In TestLabelGeneration.test_label_qr_code, the test checks for black pixel count (>100) to verify QR code rendering. This approach is fragile as it depends on arbitrary pixel thresholds and may break with minor changes to label layout, QR code size, or image processing. A more robust approach would be to decode the QR code or check for specific patterns.

**Suggested fix:**
```diff
-     def test_label_qr_code(self):
    """Test that QR code is rendered on the label"""
    from commands.label_generator import create_label
    from PIL import Image

    label_path = self.test_dir / "test_qr_label.png"
    create_label(self.test_plant_id, label_path)

    img = Image.open(label_path).convert("RGB")
    pixels = list(img.getdata())

    # Count black pixels in the image (QR code area is on the right side)
    black_count = sum(1 for r, g, b in pixels if r < 100 and g < 100 and b < 100)
    total = len(pixels)

    # Labels are mostly white; check for presence of rendered content
    self.assertGreater(
        black_count, 100, "Expected rendered QR code and text content"
    )
+     def test_label_qr_code(self):
    """Test that QR code is rendered on the label"""
    from commands.label_generator import create_label
    from PIL import Image

    label_path = self.test_dir / "test_qr_label.png"
    create_label(self.test_plant_id, label_path)

    img = Image.open(label_path).convert("RGB")
    
    # Focus on QR code region (right side of label)
    width, height = img.size
    # QR code starts at approximately 60% of width based on label generation
    qr_region_left = int(width * 0.6)
    qr_region = img.crop((qr_region_left, 0, width, height))
    qr_pixels = list(qr_region.getdata())
    
    # Count black and white pixels in QR region
    black_count = sum(1 for r, g, b in qr_pixels if r < 100 and g < 100 and b < 100)
    white_count = sum(1 for r, g, b in qr_pixels if r > 200 and g > 200 and b > 200)
    total = len(qr_pixels)
    
    # QR code should have roughly equal black/white pixels (40-60% black)
    black_ratio = black_count / total
    self.assertGreaterEqual(black_ratio, 0.35, "QR code region too dark")
    self.assertLessEqual(black_ratio, 0.65, "QR code region too light")
    # Ensure there's both black and white content (not uniform)
    self.assertGreater(black_count, 20, "QR code region appears uniform")
    self.assertGreater(white_count, 20, "QR code region appears uniform")
```

---

## `tests/test_seed_packet.py`

**Lines 12-12**

Missing docstring for test class TestSeedPacketModel. Add a docstring describing what this test suite covers.

---

**Lines 145-145**

Missing docstring for test class TestFindMatching. Add a docstring describing what this test suite covers.

---

**Lines 207-207**

Missing docstring for test class TestListAll. Add a docstring describing what this test suite covers.

---

**Lines 12-12**

Test comment

---

**Lines 12-12**

Missing docstring for test class TestSeedPacketModel. Add a docstring describing what this test suite covers.

**Suggested fix:**
```diff
- class TestSeedPacketModel(unittest.TestCase):
+ class TestSeedPacketModel(unittest.TestCase):
    """Test suite for seed packet model."""
```

---

**Lines 145-145**

Missing docstring for test class TestFindMatching. Add a docstring describing what this test suite covers.

**Suggested fix:**
```diff
- class TestFindMatching(unittest.TestCase):
+ class TestFindMatching(unittest.TestCase):
    """Test suite for find_matching function in seed packet model."""
```

---

**Lines 207-207**

Missing docstring for test class TestListAll. Add a docstring describing what this test suite covers.

**Suggested fix:**
```diff
- class TestListAll(unittest.TestCase):
+ class TestListAll(unittest.TestCase):
    """Test suite for list_all function in seed packet model."""
```

---

**Lines 112-115**

In test_markdown_roundtrip, add assertions for all fields to ensure complete validation after roundtrip.

---

