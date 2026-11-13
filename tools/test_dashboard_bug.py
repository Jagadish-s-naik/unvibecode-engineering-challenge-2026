import io
import math
import shutil
from unvibecode.presentation import CustomerDashboardRenderer

class TracedStream:
    def __init__(self):
        self.buffer = []
        self.cursor_row = 0
        self.cursor_col = 0
        self.screen = {} # (row, col) -> char

    def write(self, s):
        self.buffer.append(s)
        # trace cursor movement
        i = 0
        while i < len(s):
            if s[i:i+2] == '\r\x1b':
                # Parse ANSI sequence \r\x1b[<N>A\x1b[J
                # \r sets col to 0
                self.cursor_col = 0
                end_a = s.find('A', i)
                if end_a != -1:
                    n_str = s[i+4:end_a]
                    n = int(n_str) if n_str else 1
                    self.cursor_row -= n
                    i = end_a + 1
                    if s[i:i+3] == '\x1b[J':
                        # erase below
                        i += 3
                    continue
            elif s[i] == '\n':
                self.cursor_row += 1
                self.cursor_col = 0
                i += 1
            elif s[i] == '\r':
                self.cursor_col = 0
                i += 1
            else:
                self.cursor_col += 1
                i += 1

    def flush(self):
        pass

ts = TracedStream()
renderer = CustomerDashboardRenderer(stream=ts)
renderer.can_redraw = True

text1 = "\n● Code understanding\n  Creating the interactive code map\n\n● Business analysis\n  Preparing repository context"
print("Initial cursor:", ts.cursor_row, ts.cursor_col)
renderer.render(text1)
print("After render 1, cursor row:", ts.cursor_row, "rendered_line_count:", renderer.rendered_line_count)

# Now simulate Event 4, 5, 6 printed via cli.py render(event) -> print(text)
ts.write("\n")
ts.write("Interim results available here:\n")
ts.write("C:\\repo\\results\\interim.html\n")
print("After interim lines printed, cursor row:", ts.cursor_row)

text2 = "\n✓ Code understanding\n  Ready\n  Connected Code Map\n\n● Business analysis\n  Building map"
renderer.render(text2)
print("After render 2, cursor row:", ts.cursor_row, "rendered_line_count:", renderer.rendered_line_count)

print("\n--- RAW BUFFER LOG ---")
for chunk in ts.buffer:
    print(repr(chunk))

