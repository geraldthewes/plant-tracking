# Plan for Creating Orval Stubs for FastAPI Server

## Overview
This plan outlines the steps to implement Orval-generated TypeScript API stubs for the FastAPI backend in the plant-tracking project.

## Steps

### 1. Export OpenAPI Spec from FastAPI
- Create a Python script to generate OpenAPI JSON from the FastAPI app
- Script will run without requiring the backend server to be running
- Output to `backend/fastapi/openapi.json`

### 2. Set Up Orval Configuration
- Install Orval as a dev dependency
- Create `orval.config.ts` configuration file
- Configure Orval to use the exported OpenAPI spec
- Set output directory to `frontend/src/api/`
- Choose appropriate preset (likely React Query or types-only initially)

### 3. Generate TypeScript Stubs
- Run Orval to generate API client code
- Generated files will include:
  - Type definitions for all request/response models
  - API hook functions (if using React Query preset)
  - HTTP client functions

### 4. Add npm Scripts
- Add `generate:api` script to run the OpenAPI export and Orval generation
- Ensure script works with fresh `npm install`

### 5. Handle Generated Files in Git
- Determine whether to commit generated files or add to .gitignore
- Based on team preference mentioned in ticket

## Detailed Implementation

### Step 1: OpenAPI Export Script
Create `backend/fastapi/scripts/export_openapi.py`:
```python
#!/usr/bin/env python3
"""
Script to export OpenAPI specification from FastAPI app.
"""
import json
import sys
import os

# Add the src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from plant_tracking_api.main import app

if __name__ == "__main__":
    openapi_json = app.openapi()
    output_path = os.path.join(os.path.dirname(__file__), '..', 'openapi.json')
    
    with open(output_path, 'w') as f:
        json.dump(openapi_json, f, indent=2)
    
    print(f"OpenAPI spec exported to {output_path}")
```

### Step 2: Orval Configuration
Create `orval.config.ts` in project root:
```typescript
import { defineConfig } from 'orval';

export default defineConfig({
  api: {
    input: {
      // Path to the exported OpenAPI spec
      target: './backend/fastapi/openapi.json',
    },
    output: {
      // Where to generate the TypeScript stubs
      target: './frontend/src/api/',
      // Clean output directory before generation
      clean: true,
      // Use React Query preset for hooks
      preset: 'react-query',
      // Optional: specify client (fetch, axios, etc.)
      client: 'fetch',
      // Optional: override default names
      // override: {
      //   mutator: {
      //     path: './src/api/orval/mutator.ts',
      //     name: 'orvalMutator',
      //   },
      //   schemas: {
      //     // Custom schema handling
      //   },
      // },
    },
  },
});
```

### Step 3: Update package.json
Add Orval as dev dependency and create scripts:
```json
{
  "devDependencies": {
    "orval": "^6.27.0"
  },
  "scripts": {
    "generate:api": "node backend/fastapi/scripts/export_openapi.js && orval",
    "generate:api:watch": "orval watch"
  }
}
```

### Step 4: Create Frontend Directory Structure
Ensure `frontend/src/api/` exists for output.

### Step 5: Update .gitignore
Add generated files to .gitignore (or commit them based on team preference):
```
# Orval-generated API stubs
frontend/src/api/
```

## Verification Steps
1. Run `npm run generate:api` - should complete without errors
2. Check that `frontend/src/api/` contains generated TypeScript files
3. Verify generated files have no TypeScript errors (once TS config exists)
4. Confirm OpenAPI export script produces valid `backend/fastapi/openapi.json`
5. Verify generated stubs contain type definitions for health, plants, and media endpoints

## Dependencies
- Orval (latest stable)
- TypeScript (will be needed in frontend)
- Existing FastAPI backend

## Notes
- The media attachments endpoint uses multipart/form-data - need to verify Orval handles this correctly
- If frontend framework is undecided, starting with types-only or fetch client is safe
- Generation must work without running backend server