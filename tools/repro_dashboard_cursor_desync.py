"""Minimal deterministic reproduction of CLI relative cursor desynchronization bug."""
import io
import sys
from unvibecode.presentation import CustomerDashboardRenderer

class TerminalSpy:
    def __init__(self):
        self.log = []
        self.cursor_row = 0
        self.cursor_col = 0
        self.screen_lines = []

    def write(self, s):
        self.log.append(s)
        i = 0
        while i < len(s):
            if s[i:i+2] == '\r\x1b':
                self.cursor_col = 0
                end_a = s.find('A', i)
                if end_a != -1:
                    n_str = s[i+3:end_a]
                    n = int(n_str) if n_str else 1
                    self.cursor_row = max(0, self.cursor_row - n)
                    i = end_a + 1
                    if s[i:i+3] == '\x1b[J':
                        # ANSI ED: erase from cursor to bottom of screen
                        del self.screen_lines[self.cursor_row + 1:]
                        if self.cursor_row < len(self.screen_lines):
                            self.screen_lines[self.cursor_row] = self.screen_lines[self.cursor_row][:self.cursor_col]
                        i += 3
                    continue
            elif s[i] == '\n':
                self.cursor_row += 1
                self.cursor_col = 0
                while len(self.screen_lines) <= self.cursor_row:
                    self.screen_lines.append("")
                i += 1
            elif s[i] == '\r':
                self.cursor_col = 0
                i += 1
            else:
                while len(self.screen_lines) <= self.cursor_row:
                    self.screen_lines.append("")
                line = self.screen_lines[self.cursor_row]
                if self.cursor_col < len(line):
                    line = line[:self.cursor_col] + s[i] + line[self.cursor_col+1:]
                else:
                    line = line + " " * (self.cursor_col - len(line)) + s[i]
                self.screen_lines[self.cursor_row] = line
                self.cursor_col += 1
                i += 1

    def flush(self):
        pass

def run_repro():
    spy = TerminalSpy()
    renderer = CustomerDashboardRenderer(stream=spy)
    renderer.can_redraw = True

    # Step 1: Initial Dashboard event
    dash_1 = "\n● Code understanding\n  Creating the interactive code map\n\n● Business analysis\n  Preparing repository context"
    renderer.render(dash_1)

    # Step 2: Asynchronous interim results notification printed directly via cli.py render(event)
    spy.write("\nInterim results available here:\nC:\\repo\\results\\interim.html\n")

    # Step 3: Next polling dashboard event
    dash_2 = "\n✓ Code understanding\n  Ready\n  Connected Code Map\n\n● Business analysis\n  Building map"
    renderer.render(dash_2)

    screen_output = "\n".join(spy.screen_lines)
    
    # Check 1: Did the interim results announcement get wiped by the desynced clear()?
    interim_wiped = "C:\\repo\\results\\interim.html" not in screen_output
    # Check 2: Did the first dashboard leave orphaned ghost lines behind?
    ghost_orphaned = "Creating the interactive code map" in screen_output and "✓ Code understanding" in screen_output

    success = interim_wiped and ghost_orphaned
    return success, screen_output

if __name__ == "__main__":
    trials = 3
    hits = 0
    print(f"Running {trials} reproduction trials...")
    for t in range(1, trials + 1):
        ok, out = run_repro()
        if ok:
            hits += 1
            print(f"Trial {t}: SUCCESS (Corrupted screen state reproduced: Interim URL wiped & ghost lines orphaned)")
        else:
            print(f"Trial {t}: FAILED")
    print(f"\nReproduction hit rate: {hits}/{trials} ({hits/trials*100:.1f}%)")

