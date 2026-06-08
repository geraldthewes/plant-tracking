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