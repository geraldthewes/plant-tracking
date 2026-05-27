# Export Domain — Ontology

> Data export, streaming, and persistence format migration.

---

## export.data-export

- id: export.data-export
- status: active
- owner: core-team

The process of extracting plant data from the database into portable Markdown files with YAML frontmatter. Uses streaming pattern to avoid memory overload. Not the same as `export.export-service` — the export is the data output artifact; the export service is the component that generates it.

**Used by:** ExportService.export_to_markdown(), CLI export commands.

---

## export.export-service

- id: export.export-service
- status: active
- owner: core-team

Service class implementing iterator/streaming pattern for exporting data. Provides batched streaming for plants, genera, seed packets, and logs. Not the same as `export.data-export` — the service is the component; the export is the output.

**Used by:** ExportService class, export CLI commands.

---

## export.streaming-pattern

- id: export.streaming-pattern
- status: active
- owner: core-team

Iterator-based data export pattern that yields records in batches to avoid loading all data into memory. Not the same as `export.export-service` — the pattern is the architectural approach; the service is the concrete implementation.

**Used by:** ExportService export_*_streaming() methods.

---

## export.markdown-record

- id: export.markdown-record
- status: active
- owner: core-team

A single database record serialized as a Markdown file with YAML frontmatter. Used for both original file-based storage and export format. Not the same as `export.data-export` — the markdown record is a single file; the data export is the complete set of exported files.

**Used by:** ExportService._write_markdown_file(), Plant storage (original system).
