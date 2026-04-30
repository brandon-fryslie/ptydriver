import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

// Base URL is set per deploy via VITE_BASE so asset paths line up under
// brandon-fryslie.github.io/ptydriver/. Locally `npm run dev` defaults to '/'.
export default defineConfig({
  plugins: [react()],
  base: process.env.VITE_BASE ?? '/',
  build: {
    outDir: 'dist',
    sourcemap: true,
    // CheerpX uses top-level await; the default Vite target (es2020) refuses it.
    // CheerpX itself only loads in browsers that support SharedArrayBuffer + WASM
    // JIT, which all support top-level await — so esnext is safe here.
    target: 'esnext',
    chunkSizeWarningLimit: 4096,
  },
  optimizeDeps: {
    // CheerpX uses dynamic patterns Vite's pre-bundler chokes on; let it
    // resolve at runtime against the consumer's node_modules.
    exclude: ['@leaningtech/cheerpx'],
  },
});
