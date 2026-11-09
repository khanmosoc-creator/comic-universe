import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Static build only: everything the reader needs ends up in dist/.
// No dev-server proxies, no environment secrets, no runtime API calls.
export default defineConfig({
  plugins: [react()],
  build: {
    outDir: 'dist',
    target: 'es2020',
    sourcemap: false,
  },
});
