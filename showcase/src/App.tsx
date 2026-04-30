import { Header, WebVMTerminal, MetadataFooter, CodeBlock } from 'showcase-kit';

// [LAW:one-source-of-truth] Disk image URL is the single canonical reference
// to where the project's WebVM rootfs lives. The image itself lives on a
// GitHub Release; the webvm.tinkerpad.ai Cloudflare Worker re-fronts it with
// the CORS+CORP headers required in a cross-origin-isolated page.
// Update this in lockstep with the upload-image.sh tag.
const PTYDRIVER_DISK_IMAGE_URL =
  'https://webvm.tinkerpad.ai/brandon-fryslie/ptydriver/releases/download/webvm-image-v1/ptydriver.ext2';

export function App() {
  return (
    <div className="pd-page">
      <Header
        eyebrow="an experiment by brandon-fryslie"
        name="ptydriver"
        tagline={
          <>
            Drive interactive terminal applications programmatically through a real
            PTY. Below: a real Linux shell in your browser, with ptydriver
            preinstalled. Run the demo scripts to see ptydriver controlling vim,
            fzf, and a Python REPL — your inputs, real syscalls, real output.
          </>
        }
        badges={['Python', 'PTY', 'pyte', 'TUI testing']}
        actions={
          <>
            <a
              className="sk-meta-link sk-meta-link-primary"
              href="https://github.com/brandon-fryslie/ptydriver"
              rel="noopener noreferrer"
            >
              View on GitHub
            </a>
            <a
              className="sk-meta-link"
              href="https://github.com/brandon-fryslie/ptydriver#readme"
              rel="noopener noreferrer"
            >
              README
            </a>
          </>
        }
      />

      <section className="pd-stage">
        <WebVMTerminal
          diskImage={{
            url: PTYDRIVER_DISK_IMAGE_URL,
            type: 'cloud',
            label: 'Debian + ptydriver',
          }}
          bootCommand="/bin/bash"
          bootArgs={['--login']}
          cwd="/home/user"
          banner={
            <>
              You're talking to a real Linux kernel running in your browser via{' '}
              <a href="https://cheerpx.io" target="_blank" rel="noopener noreferrer">CheerpX</a>.
              ptydriver is installed at <code>/home/user/.venv/bin/ptydriver</code>.
              Demos are in <code>~/demos/</code>.
            </>
          }
          suggestedCommands={[
            {
              label: 'List demo scripts',
              cmd: 'ls demos/',
              description: 'See what ptydriver demos ship with this image.',
            },
            {
              label: 'Drive vim and quit it',
              cmd: 'python3 demos/01_drive_vim.py',
              description: 'Spawn vim, send keystrokes, assert what landed on the screen.',
            },
            {
              label: 'Drive fzf and pick an item',
              cmd: 'python3 demos/02_drive_fzf.py',
              description: 'Filter a list interactively from Python.',
            },
            {
              label: 'Drive a Python REPL',
              cmd: 'python3 demos/03_drive_repl.py',
              description: 'Send statements, wait for prompts, read results.',
            },
            {
              label: 'See the demo source',
              cmd: 'cat demos/01_drive_vim.py',
              description: 'It is real ptydriver code — nothing mocked.',
            },
            {
              label: 'Open an interactive Python shell',
              cmd: 'python3',
              description: 'Try `from ptydriver import PtyProcess` yourself.',
            },
          ]}
        />
      </section>

      <section className="pd-howitworks">
        <h2>How it works</h2>
        <p>
          ptydriver wraps any interactive command in a pseudo-terminal, feeds it
          to a virtual screen (<code>pyte</code>), and gives you a tiny API to
          send keystrokes and assert what's on the screen. Above is the actual
          library running on a real Linux kernel — not a JavaScript reimplementation,
          not a recording.
        </p>

        <h3>Minimal example</h3>
        <CodeBlock
          language="Python"
          code={`from ptydriver import PtyProcess, Keys

with PtyProcess(["python3"]) as proc:
    proc.send("print('hello')")
    proc.wait_for("hello")
    # The virtual screen reflects everything python3 has printed:
    print(proc.get_content())`}
        />

        <h3>What's running in the terminal above</h3>
        <p>
          A Debian rootfs with Python and ptydriver installed, packaged as an
          ext2 image and streamed to your browser by{' '}
          <a href="https://cheerpx.io" target="_blank" rel="noopener noreferrer">CheerpX</a>{' '}
          (an x86-to-WebAssembly JIT). The kernel, your shell, vim, fzf, Python,
          the PTY layer ptydriver talks to — all real, all running locally in
          your tab. Cross-origin isolation comes from{' '}
          <a href="https://github.com/gzuidhof/coi-serviceworker" target="_blank" rel="noopener noreferrer">coi-serviceworker</a>.
        </p>
      </section>

      <MetadataFooter
        github="https://github.com/brandon-fryslie/ptydriver"
        license="MIT"
        language="Python"
        install="pip install ptydriver"
        links={[
          { label: 'Source on GitHub', href: 'https://github.com/brandon-fryslie/ptydriver' },
          { label: 'CheerpX', href: 'https://cheerpx.io' },
          { label: 'pyte (the screen-state engine)', href: 'https://github.com/selectel/pyte' },
        ]}
      />
    </div>
  );
}
