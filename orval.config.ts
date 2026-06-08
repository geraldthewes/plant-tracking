import { defineConfig } from 'orval';

export default defineConfig({
  api: {
    input: {
      target: './backend/fastapi/openapi.json',
    },
    output: {
      target: './frontend/src/api/',
      clean: true,
      preset: 'react-query',
      client: 'fetch',
    },
  },
});