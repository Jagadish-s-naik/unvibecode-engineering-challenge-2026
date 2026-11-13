# [Bug] CLI Presentation — Interleaved stream events desynchronize CustomerDashboardRenderer relative cursor, erasing interim report announcements and orphaning duplicate dashboard headers

## 1. Problem summary
During an interactive `unvibecode review` on any terminal where VT processing is active (`can_redraw is True`), the arrival of interim analysis results permanently corrupts the terminal display. The CLI prints non-dashboard status lines (the interim report announcement and HTML file path) directly to standard output while a live dashboard is active. Because `cli.py` writes these lines via `print()` rather than routing them through `CustomerDashboardRenderer`, the physical terminal cursor advances down by 3 or more lines without updating `renderer.rendered_line_count`.

When the next dashboard refresh event arrives, `renderer.clear()` emits an ANSI Cursor Up command (`\x1b[{rendered_line_count - 1}A`) calculated from the stale row count. Because the cursor was pushed down by the interleaved print statements, the cursor moves up 3+ rows too few, landing in the middle of the screen. The subsequent ANSI Erase Down command (`\x1b[J`) completely erases the interim report announcement while leaving the upper lines of the prior dashboard permanently frozen in the terminal scrollback.

## 2. Test environment
- **UnvibeCode version:** 0.4.0 (installed from PyPI)
- **Operating system and Python version:** Windows 11 Home 10.0.26100 AMD64, Python 3.14.2 (also verified on standard xterm / ANSI VT100 terminal emulation)
- **Analyzed public repository URL and pinned commit SHA:**
  - Repository: `https://github.com/pytest-dev/pluggy`
  - Commit SHA: `f8aa4a009716a7994f2f6c1947d9fa69feccbdd5`
  - (Also verified across `pallets/flask` @ `ab81496`, `marshmallow-code/marshmallow` @ `1b1250d`, `chardet/chardet` @ `fa905b3`, and `fastapi/full-stack-fastapi-template` @ `aabb901`)
- **Exact command run:**
  ```bash
  python -m unvibecode review --repository repos/pluggy
  ```

## 3. Steps to reproduce
This bug can be reproduced deterministically in under 5 seconds using either the live CLI or a self-contained test script executing the exact client presentation loop:

### Option A: Standalone 20-line reproduction script (requires no network credentials)
```python
from unvibecode.presentation import CustomerDashboardRenderer
import sys

# Instantiate renderer with active redraw enabled (simulating interactive terminal)
renderer = CustomerDashboardRenderer(stream=sys.stdout)
renderer.can_redraw = True

# Step 1: Render initial live dashboard (Event 3 from server)
dash1 = "\n● Code understanding\n  Creating the interactive code map\n\n● Business analysis\n  Preparing repository context"
renderer.render(dash1)

# Step 2: Interleaved interim results announcement printed via cli.py:render()
sys.stdout.write("\nInterim results available here:\nC:\\repo\\results\\interim.html\n")
sys.stdout.flush()

# Step 3: Render next live dashboard poll (Event 7 from server)
dash2 = "\n✓ Code understanding\n  Ready\n  Connected Code Map\n\n● Business analysis\n  Building map"
renderer.render(dash2)
```

### Option B: Using the CLI on a public repository
1. Open Windows Terminal, PowerShell, or any ANSI-compatible terminal.
2. Run `python -m unvibecode review --repository repos/pluggy`.
3. Observe the terminal when the "Interim results available here:" notification arrives (~5–10s into analysis).

## 4. Expected behavior
According to the docstring and comments in `unvibecode/presentation.py:lines 42–54`:
> `"Keep one live dashboard on screen instead of appending every refresh."`
> `"Move to column one of the dashboard's first line and erase everything below it. The command and repository summary above remain visible."`

When interim results arrive:
1. The interim results path should remain visible on the screen so the developer can see and open their interim report.
2. The live dashboard should clear only its own previous content and redraw smoothly without leaving orphaned duplicate headers or overwriting interleaved announcements.

## 5. Actual behavior
1. **Interim URL Erased:** The lines `"Interim results available here:"` and the file path `".../pluggy-unvibecode-interim.html"` are wiped out by the subsequent dashboard `clear()` call. The developer cannot see or copy the interim report URL.
2. **Ghost Lines Orphaned:** The top lines of Dashboard 1 (`● Code understanding\n  Creating the interactive code map`) are never cleared and remain permanently stuck in the terminal scrollback directly above Dashboard 2.
3. Visual representation of the corrupted screen:
   ```text
   ● Code understanding
     Creating the interactive code map

   ✓ Code understanding
     Ready
     Connected Code Map

   ● Business analysis
     Building map
   ```
   (Notice Dashboard 1's header is still present, while the interim announcement was completely destroyed).

## 6. Evidence
### Relevant file and function names with line numbers
1. `unvibecode/cli.py`, lines 65–70 (`render(event)`):
   ```python
   def render(event):
       text = local_text(event.get('text', ''))
       if event['kind'] == 'dashboard': dashboard.render(text)
       elif event['kind'] == 'clear': dashboard.clear()
       else: print(text, flush=True)  # <-- Bypasses dashboard renderer and advances cursor!
   ```
2. `unvibecode/presentation.py`, lines 50–74 (`CustomerDashboardRenderer.clear` and `render`):
   ```python
   def clear(self) -> None:
       if not self.can_redraw or not self.rendered_line_count:
           return
       self.stream.write(f"\r\x1b[{self.rendered_line_count - 1}A\x1b[J")
       self.stream.flush()
       self.rendered_line_count = 0
   ```

### Raw Stream Byte Trace
Tracing the exact escape sequences emitted to standard output:
```text
1. [write] '\n● Code understanding\n  Creating the interactive code map\n\n● Business analysis\n  Preparing repository context\n'
   --> Cursor advances: 6 rows. rendered_line_count set to 7.
2. [write] '\nInterim results available here:\nC:\\repo\\results\\interim.html\n'
   --> Cursor advances: 3 rows (now at row 9). rendered_line_count remains stale at 7!
3. [write] '\r\x1b[6A\x1b[J'
   --> Cursor moves up 6 rows: 9 - 6 = row 3!
   --> \x1b[J erases from row 3 downwards (erasing interim announcement, but leaving rows 0-2 untouched).
4. [write] '\n✓ Code understanding\n  Ready\n  Connected Code Map\n\n● Business analysis\n  Building map\n'
   --> Dashboard 2 is drawn starting at row 3, right beneath the orphaned rows 0-2.
```

### Hit Rate
Tested across 3 automated reproduction trials: **3/3 hits (100% deterministic)**. Saved to `evidence/terminal_cursor_desync_repro.txt`.

## 7. Impact and scope
- **Who is affected:** Every developer using `unvibecode` in an interactive terminal (Windows Terminal, PowerShell, macOS Terminal, Linux xterm).
- **Usability impact:**
  - **Critical loss of interim results:** The interim report URL is destroyed on screen, negating the value of interim results streaming.
  - **Terminal corruption:** Produces duplicated progress indicators, broken layout, and scrollback pollution that worsens with every review.
- **Occurrence:** Occurs on **100% of reviewed repositories** where the server emits interim presentation events (verified across all 5 test repositories: Flask, Pluggy, Marshmallow, Chardet, and FastAPI).

## 8. Suspected cause / suggested fix
### Root Cause
`CustomerDashboardRenderer` assumes exclusive control of the terminal cursor, calculating cursor displacement solely from its own internal `rendered_line_count`. When `cli.py:render()` receives events of `kind != 'dashboard'` (e.g. `kind == 'line'`), it calls `print(text, flush=True)` without clearing the currently active live dashboard first. This desynchronizes the renderer's cursor state from the physical cursor position.

### Suggested Fix
In `unvibecode/cli.py`, clear the active dashboard before printing permanent interleaved log lines:
```python
def render(event):
    text = local_text(event.get('text', ''))
    if event['kind'] == 'dashboard':
        dashboard.render(text)
    elif event['kind'] == 'clear':
        dashboard.clear()
    else:
        dashboard.clear()  # Clear active dashboard before emitting permanent line events
        print(text, flush=True)
```
When `dashboard.clear()` runs before `print()`, the old dashboard is wiped from its valid cursor position, the permanent announcement lines are printed, and subsequent dashboard updates render cleanly below them without ghost lines or missing text.

## 9. Duplicate check
We performed an exhaustive keyword and semantic search against all 737 issues and pull requests (open and closed) in `FinanceFlash/unvibecode` (`notes/existing_issues.json`). The closest existing issues are:

- **Issue #463, #335, #299, #314:** Deal exclusively with `UnicodeEncodeError` on Windows consoles with `cp1252` encoding when attempting to output the Unicode bullet `●` character. None of these address cursor arithmetic, ANSI displacement, or interleaved event rendering.
- **Issue #680:** Deals with unescaped filenames in `--dry-run` that can forge status lines and ANSI terminal codes. It does not touch `CustomerDashboardRenderer`, `clear()`, or cursor movement.
- **Issue #729:** Addresses error recovery advice and recursive CLI resume loops upon terminal failure.
- **Issue #667:** Addresses disk-level overwriting where the interim HTML file is placed in the same folder as the final report. It does not touch terminal presentation or the visual erasure of the interim announcement URL.

This issue is entirely distinct: it is a deterministic relative ANSI cursor desynchronization bug between `cli.py:render()` and `CustomerDashboardRenderer`, causing physical screen corruption and the visual destruction of the interim results link.

