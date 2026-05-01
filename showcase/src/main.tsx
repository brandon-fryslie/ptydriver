import { StrictMode } from 'react';
import { createRoot } from 'react-dom/client';
import { bootstrapCoi } from 'showcase-kit';
import { App } from './App.tsx';
import 'showcase-kit/styles.css';
import '@xterm/xterm/css/xterm.css';
import './app.css';

// [LAW:single-enforcer] Run before mount so a stale coi-serviceworker.js from
// a sibling version subdir (e.g. /ptydriver/pr-7/) gets unregistered + reload
// before any CheerpX-touching component tries to read SharedArrayBuffer.
await bootstrapCoi();

createRoot(document.getElementById('root')!).render(
  <StrictMode>
    <App />
  </StrictMode>,
);
