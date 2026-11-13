import io
import math
import shutil
from unvibecode.presentation import CustomerDashboardRenderer

class ScreenBuffer:
    def __init__(self, width=80):
        self.width = width
        self.rows = [[]]
        self.cursor_r = 0
        self.cursor_c = 0

    def write(self, s):
        i = 0
        while i < len(s):
            if s[i:i+2] == '\r\x1b':
                self.cursor_c = 0
                end_a = s.find('A', i)
                if end_a != -1:
                    n_str = s[i+3:end_a]
                    n = int(n_str) if n_str else 1
                    self.cursor_r = max(0, self.cursor_r - n)
                    i = end_a + 1
                    if s[i:i+3] == '\x1b[J':
                        # Erase from cursor to bottom
                        del self.rows[self.cursor_r + 1:]
                        if self.cursor_r < len(self.rows):
                            self.rows[self.cursor_r] = self.rows[self.cursor_r][:self.cursor_c]
                        i += 3
                    continue
            elif s[i] == '\n':
                self.cursor_r += 1
                self.cursor_c = 0
                while len(self.rows) <= self.cursor_r:
                    self.rows.append([])
                i += 1
            elif s[i] == '\r':
                self.cursor_c = 0
                i += 1
            else:
                while len(self.rows) <= self.cursor_r:
                    self.rows.append([])
                row = self.rows[self.cursor_r]
                while len(row) < self.cursor_c:
                    row.append(' ')
                if self.cursor_c < len(row):
                    row[self.cursor_c] = s[i]
                else:
                    row.append(s[i])
                self.cursor_c += 1
                if self.cursor_c >= self.width:
                    self.cursor_r += 1
                    self.cursor_c = 0
                    while len(self.rows) <= self.cursor_r:
                        self.rows.append([])
                i += 1

    def flush(self):
        pass

    def render_to_text(self):
        return "\n".join("".join(r).rstrip() for r in self.rows)

# Test UNFIXED behavior
sb_buggy = ScreenBuffer(width=100)
renderer_buggy = CustomerDashboardRenderer(stream=sb_buggy)
renderer_buggy.can_redraw = True

# 1. Event 3: Dashboard 1
ev3_text = "\n● Code understanding\n  Creating the interactive code map\n\n● Business analysis\n  Preparing repository context"
renderer_buggy.render(ev3_text)

# 2. Events 4, 5, 6: Interleaved lines printed directly via print()
sb_buggy.write("\n")
sb_buggy.write("Interim results available here:\n")
sb_buggy.write("C:\\repo\\results\\interim.html\n")

# 3. Event 7: Dashboard 2
ev7_text = "\n✓ Code understanding\n  Ready\n  Connected Code Map\n\n● Business analysis\n  Building map"
renderer_buggy.render(ev7_text)

print("=== BUGGY OUTPUT ON SCREEN ===")
print(sb_buggy.render_to_text())
print("==============================\n")

# Test FIXED behavior (clearing dashboard before interleaved line prints)
sb_fixed = ScreenBuffer(width=100)
renderer_fixed = CustomerDashboardRenderer(stream=sb_fixed)
renderer_fixed.can_redraw = True

# 1. Event 3: Dashboard 1
renderer_fixed.render(ev3_text)

# 2. Events 4, 5, 6 with fix: clear dashboard before printing permanent line
renderer_fixed.clear()
sb_fixed.write("\n")
sb_fixed.write("Interim results available here:\n")
sb_fixed.write("C:\\repo\\results\\interim.html\n")

# 3. Event 7: Dashboard 2
renderer_fixed.render(ev7_text)

print("=== FIXED OUTPUT ON SCREEN ===")
print(sb_fixed.render_to_text())
print("==============================")
