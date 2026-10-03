#!/usr/bin/env python3
"""Builds longest_free_slot.mp4 (+ .srt and transcript.md) explaining solution.cpp.

Needs: Pillow, ffmpeg, espeak-ng (mb-us2 MBROLA voice if installed).
Usage: python3 make_video.py [output_dir]
"""
import os, re, subprocess, sys, tempfile, wave
from PIL import Image, ImageDraw, ImageFont

W, H = 1280, 720
CAP_Y = 600                       # caption band starts here
BG, PANEL, FG, DIM = "#0f172a", "#1e293b", "#e2e8f0", "#94a3b8"
ACCENT, GREEN, RED, AMBER, BLUE, PURPLE = "#38bdf8", "#4ade80", "#f87171", "#fbbf24", "#60a5fa", "#c084fc"
SANS = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
MONO = "/usr/share/fonts/truetype/dejavu/DejaVuSansMono.ttf"
_fonts = {}


def font(path, size):
    if (path, size) not in _fonts:
        _fonts[(path, size)] = ImageFont.truetype(path, size)
    return _fonts[(path, size)]


HERE = os.path.dirname(os.path.abspath(__file__))
CODE = open(os.path.join(HERE, "solution.cpp")).read().splitlines()


def code_range(first, last):
    """1-based inclusive line range of solution.cpp."""
    return [(i, CODE[i - 1]) for i in range(first, last + 1)]


# ---------- drawing primitives ----------

def canvas(title=None, step=None):
    img = Image.new("RGB", (W, H), BG)
    d = ImageDraw.Draw(img)
    if title:
        d.text((48, 28), title, font=font(BOLD, 36), fill=FG)
        d.line((48, 80, W - 48, 80), fill=ACCENT, width=3)
    if step:
        d.text((W - 48, 36), step, font=font(SANS, 20), fill=DIM, anchor="ra")
    return img, d


KW = r"\b(int|string|const|char|static|bool|if|for|auto|return|long|map|pair|vector|istream|sizeof|continue|using|namespace|std|include)\b"
TOKEN = re.compile(r"(//.*$)|(\"[^\"]*\"|'[^']*')|" + KW + r"|(\b\d+\b)")


def draw_code(d, lines, x, y, size=17, highlight=(), width=None, dim_others=False):
    f = font(MONO, size)
    lh = int(size * 1.45)
    width = width or (W - x - 40)
    d.rounded_rectangle((x - 16, y - 12, x + width, y + lh * len(lines) + 8), 10, fill=PANEL)
    cw = f.getlength("M")
    for row, (no, text) in enumerate(lines):
        yy = y + row * lh
        lit = no in highlight
        if lit:
            d.rectangle((x - 16, yy - 2, x + width, yy + lh - 3), fill="#334155")
            d.rectangle((x - 16, yy - 2, x - 11, yy + lh - 3), fill=AMBER)
        faded = dim_others and highlight and not lit
        d.text((x, yy), f"{no:>2}", font=f, fill="#475569")
        cx = x + cw * 3.5
        pos = 0
        for m in TOKEN.finditer(text):
            if m.start() > pos:
                d.text((cx + cw * pos, yy), text[pos:m.start()], font=f, fill=DIM if faded else FG)
            colour = "#64748b" if m.group(1) else GREEN if m.group(2) else PURPLE if m.group(3) else AMBER
            if faded:
                colour = "#475569"
            d.text((cx + cw * m.start(), yy), m.group(0), font=f, fill=colour)
            pos = m.end()
        if pos < len(text):
            d.text((cx + cw * pos, yy), text[pos:], font=f, fill=DIM if faded else FG)


def wrap(d, text, f, maxw):
    words, lines, cur = text.split(), [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if d.textlength(trial, font=f) <= maxw:
            cur = trial
        else:
            lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def bullets(d, items, x, y, size=26, gap=18, maxw=1100):
    f = font(SANS, size)
    for item in items:
        colour = FG
        if isinstance(item, tuple):
            item, colour = item
        lines = wrap(d, item, f, maxw - 30)
        d.ellipse((x, y + size * 0.35, x + 12, y + size * 0.35 + 12), fill=ACCENT)
        for ln in lines:
            d.text((x + 30, y), ln, font=f, fill=colour)
            y += int(size * 1.35)
        y += gap
    return y


def mm(m):
    return f"{m // 60:02d}:{m % 60:02d}"


def timeline(d, x, y, w, lo, hi, bars=(), gaps=(), cursor=None, business=None, label=None, ticks=60, days=None):
    """bars: (start, end, colour, text, row); gaps: (start, end, colour, text). Returns the axis y."""
    sx = lambda m: x + (m - lo) * w / (hi - lo)
    rows = max([b[4] for b in bars] + [0]) + 1
    ax = y + rows * 38 + 34
    if label:
        d.text((x, y - 44), label, font=font(BOLD, 22), fill=FG)
    for b in ([business] if isinstance(business, tuple) else business or []):
        d.rectangle((sx(b[0]), y - 8, sx(b[1]), ax + 26), fill="#132a3e")
        d.text((sx(b[0]) + 4, ax + 6), "business hours", font=font(SANS, 15), fill=ACCENT)
    d.line((x, ax, x + w, ax), fill=DIM, width=2)
    for m in range(lo, hi + 1, ticks):
        d.line((sx(m), ax - 5, sx(m), ax + 5), fill=DIM, width=2)
        d.text((sx(m), ax + 32), mm(m % 1440), font=font(SANS, 15), fill=DIM, anchor="ma")
    for m, left, right in days or []:
        d.line((sx(m), y - 14, sx(m), ax + 50), fill=AMBER, width=2)
        d.text((sx(m) - 8, ax + 58), left, font=font(BOLD, 16), fill=FG, anchor="ra")
        d.text((sx(m) + 8, ax + 58), right, font=font(BOLD, 16), fill=FG, anchor="la")
    for s, t, colour, text, row in bars:
        top = y + row * 38
        d.rounded_rectangle((sx(s), top, sx(t), top + 30), 6, fill=colour)
        if text:
            d.text(((sx(s) + sx(t)) / 2, top + 15), text, font=font(BOLD, 15), fill="#0f172a", anchor="mm")
    for s, t, colour, text in gaps:
        d.rectangle((sx(s), ax - 14, sx(t), ax - 2), fill=colour)
        if text:
            d.text(((sx(s) + sx(t)) / 2, ax - 18), text, font=font(BOLD, 16), fill=colour, anchor="mb")
    if cursor is not None:
        cx = sx(cursor)
        d.line((cx, y - 14, cx, ax + 12), fill=AMBER, width=3)
        d.polygon([(cx - 8, y - 22), (cx + 8, y - 22), (cx, y - 10)], fill=AMBER)
        d.text((cx, y - 26), f"cursor {mm(cursor)}", font=font(BOLD, 15), fill=AMBER, anchor="mb")
    return ax


def caption(img, text):
    img = img.copy()
    d = ImageDraw.Draw(img)
    d.rectangle((0, CAP_Y, W, H), fill="#020617")
    d.line((0, CAP_Y, W, CAP_Y), fill="#1e293b", width=2)
    f = font(SANS, 25)
    lines = wrap(d, text, f, W - 120)[:3]
    lh = 34
    y0 = CAP_Y + (H - CAP_Y - lh * len(lines)) // 2
    for i, ln in enumerate(lines):
        d.text((W // 2, y0 + i * lh), ln, font=f, fill=FG, anchor="ma")
    return img


# ---------- scenes ----------
# Each scene: (image, [narration]) where narration is "caption" or ("caption", "spoken text").

def scenes():
    out = []

    img, d = canvas()
    d.text((W // 2, 210), "Longest Free Slot", font=font(BOLD, 64), fill=FG, anchor="mm")
    d.text((W // 2, 285), "per employee, per day, inside business hours", font=font(SANS, 30), fill=ACCENT, anchor="mm")
    d.text((W // 2, 360), "C++ walkthrough  ·  map + midnight split + sort & sweep", font=font(SANS, 22), fill=DIM, anchor="mm")
    timeline(d, 240, 420, 800, 540, 1020, ticks=120,
             bars=[(570, 660, RED, "", 0), (780, 840, RED, "", 0)], gaps=[(840, 1020, GREEN, "free")])
    out.append((img, [
        ("In this video, we walk through a C++ solution to the longest free slot problem.",
         "In this video, we walk through a C plus plus solution to the longest free slot problem."),
        "For every employee and every day, we find the longest stretch of free time inside business hours.",
    ]))

    img, d = canvas("The problem", "1 / 9")
    d.text((48, 104), "Input", font=font(BOLD, 24), fill=ACCENT)
    sample = open(os.path.join(HERE, "sample_input.txt")).read().splitlines()
    draw_code(d, [(i + 1, s) for i, s in enumerate(sample)], 64, 150, size=17, width=640)
    d.text((48, 330), "Output  (one line per employee + date)", font=font(BOLD, 24), fill=ACCENT)
    draw_code(d, [(1, "employee,date,freeStart,freeEnd,minutes")], 64, 376, size=17, width=640)
    bullets(d, [
        "Line 1: business start, business end, record count",
        "Record: employee, meeting, join, leave",
        "Find the longest free gap per employee per date",
        ("Ties → earliest gap", AMBER),
    ], 760, 120, size=21, gap=14, maxw=480)
    out.append((img, [
        "The first line gives the business hours start, the business hours end, and the number of meeting records.",
        ("Each record has an employee ID, a meeting name, a join time, and a leave time.",
         "Each record has an employee I D, a meeting name, a join time, and a leave time."),
        "For each employee and date, we print the start, the end, and the length in minutes of the longest free gap. Ties go to the earliest gap.",
    ]))

    img, d = canvas("The plan", "2 / 9")
    steps = [("1", "Parse", "split CSV,\ntimes → minutes"), ("2", "Split", "meetings that\ncross midnight"),
             ("3", "Clip", "keep only the part\nin business hours"), ("4", "Sweep", "sort, merge,\ntrack biggest gap")]
    bw, gap = 250, 40
    x0 = (W - (4 * bw + 3 * gap)) // 2
    for i, (n, head, body) in enumerate(steps):
        x = x0 + i * (bw + gap)
        d.rounded_rectangle((x, 200, x + bw, 440), 16, fill=PANEL, outline=ACCENT, width=2)
        d.ellipse((x + bw // 2 - 26, 222, x + bw // 2 + 26, 274), fill=ACCENT)
        d.text((x + bw // 2, 248), n, font=font(BOLD, 28), fill=BG, anchor="mm")
        d.text((x + bw // 2, 310), head, font=font(BOLD, 30), fill=FG, anchor="mm")
        d.multiline_text((x + bw // 2, 375), body, font=font(SANS, 19), fill=DIM, anchor="mm", align="center")
        if i < 3:
            ax = x + bw + 6
            d.polygon([(ax, 310), (ax + gap - 12, 320), (ax, 330)], fill=ACCENT)
    d.text((W // 2, 500), "map<(employee, date), vector<busy interval>>", font=font(MONO, 22), fill=AMBER, anchor="mm")
    out.append((img, [
        "The plan has four steps.",
        "Parse each record. Split any meeting that crosses midnight. Clip each piece to business hours. Then sort and sweep each day to find the biggest gap.",
        "Everything is stored in a map from employee and date to that day's list of busy intervals.",
    ]))

    img, d = canvas("Helpers: time and dates", "3 / 9")
    hl_sets = [{4, 5}, {6, 7, 8, 9, 10, 11, 12, 13}, {6}]
    lines_ = [
        [("toMinutes turns an HH:MM string into minutes since midnight, and hhmm turns minutes back into HH:MM.",
          "to Minutes turns an hour and minute string into minutes since midnight, and h h m m turns minutes back into text.")],
        ["nextDate adds one day to a date string. It rolls over month ends and year ends, and gives February an extra day in leap years.",
         "A leap year is divisible by 4 but not by 100, unless it is also divisible by 400."],
        [("Dates are YYYY-MM-DD, so plain string comparison orders them correctly. The loop later relies on that.",
          "Dates are written year, month, day, so plain string comparison orders them correctly. The loop later relies on that.")],
    ]
    for hl, lines in zip(hl_sets, lines_):
        img, d = canvas("Helpers: time and dates", "3 / 9")
        draw_code(d, code_range(4, 14), 64, 110, size=16, highlight=hl, dim_others=True)
        out.append((img, lines))

    for hl, lines in [
        ({16, 17, 18, 19, 20}, ["In solve, we read the business hours and the record count, then call getline to finish that first line.",
                                "Both business times are converted to minutes."]),
        ({21}, ["The map key is a pair: employee ID and date. The value is the list of busy intervals for that day, already clipped to business hours.",
                "Because it is an ordered map, the output will come out sorted by employee, then by date."]),
        ({22, 23, 24, 25, 26, 27, 28, 29, 30}, [
            "Blank lines are skipped without counting them as records. Each record is split on commas.",
            "The first ten characters of each timestamp are the date, and characters eleven to fifteen are the time."]),
    ]:
        img, d = canvas("Reading the input", "4 / 9")
        draw_code(d, code_range(15, 31), 64, 104, size=15, highlight=hl, dim_others=True)
        out.append((img, lines))

    # midnight split
    def midnight(show_clip):
        img, d = canvas("Meetings that cross midnight", "5 / 9")
        draw_code(d, code_range(31, 38), 64, 104, size=15, highlight={32, 33, 34} if not show_clip else {31, 36, 37}, dim_others=True)
        bars = [(1320, 1440, RED, "22–24", 0), (1440, 2040, RED, "00:00–10:00", 0)]
        gaps = []
        if show_clip:
            bars = [(1320, 1440, "#7f1d1d", "", 0), (1440, 1980, "#7f1d1d", "dropped (outside 9–5)", 0), (1980, 2040, RED, "9–10", 0)]
            gaps = [(2040, 2460, GREEN, "free 420 min")]
        timeline(d, 70, 400, 1140, 1080, 2520, bars=bars, gaps=gaps, ticks=120, business=[(1980, 2460)],
                 label="Employee 102 · Overnight Deploy · Mar 11 22:00 → Mar 12 10:00", days=[(1440, "Mar 11", "Mar 12")])
        return img

    out.append((midnight(False), [
        "Now the key trick. A meeting can cross midnight, like employee 102's overnight deploy, from 10 PM on March 11 to 10 AM on March 12.",
        "We walk the dates from the join date to the leave date. On the first date the piece starts at the join time. On the last date it ends at the leave time. Any date in between is the full 24 hours.",
        "If a piece has zero length, for example a meeting that ends exactly at midnight, it is skipped.",
    ]))
    out.append((midnight(True), [
        "Each piece is then clipped to business hours. On March 11, the 10 PM to midnight piece is outside nine to five, so nothing is added.",
        "On March 12, only nine to ten stays busy, which leaves a free slot from ten to five: 420 minutes.",
        "Line 31 still creates a map entry for the join date, so March 11 appears in the output as a fully free day of 480 minutes.",
    ]))

    # sweep on employee 101
    meetings = [(570, 630, "Standup"), (600, 660, "Review"), (780, 840, "1:1")]
    states = [
        (0, 540, [], (540, 0), "Start: cursor = 09:00, best = 0", [
            "Now the sweep. Here are employee 101's busy intervals on March 11, sorted by start time.",
            "The cursor marks the end of the busy time merged so far. It starts at 9 AM, and the best gap starts at zero."]),
        (1, 630, [(540, 570, GREEN, "30")], (540, 30), "09:30 > cursor → gap 30 → best", [
            "The first meeting starts at 9:30, after the cursor. That leaves a 30 minute gap, which becomes the best so far.",
            "The cursor moves to the meeting's end, 10:30."]),
        (2, 660, [(540, 570, "#166534", "30")], (540, 30), "10:00 < cursor → overlap, extend", [
            "The next meeting starts at 10, before the cursor, so it overlaps. There is no gap.",
            "We simply extend the cursor to 11. This is how overlapping and touching meetings merge, without a separate merge step."]),
        (3, 840, [(540, 570, "#166534", "30"), (660, 780, GREEN, "120")], (660, 120), "13:00 > cursor → gap 120 → best", [
            "The third meeting starts at 1 PM. The gap from 11 to 1 is 120 minutes, a new best. The cursor moves to 2 PM."]),
        (3, 840, [(540, 570, "#166534", "30"), (660, 780, "#166534", "120"), (840, 1020, GREEN, "180")], (840, 180),
         "after loop: 14:00 → 17:00 = 180 → best", [
             "After the loop, we check the gap from the cursor to the end of business hours. Two to five is 180 minutes, the new best.",
             "Because the best is only replaced by a strictly longer gap, ties keep the earliest one."]),
    ]
    for shown, cur, gaps, (bstart, blen), note, lines in states:
        img, d = canvas("Sort & sweep · employee 101 · 2024-03-11", "6 / 9")
        bars = [(s, t, RED if i < shown else "#475569", name, i) for i, (s, t, name) in enumerate(meetings)]
        timeline(d, 70, 150, 720, 540, 1020, bars=bars, gaps=gaps, cursor=cur, business=(540, 1020))
        d.rounded_rectangle((830, 110, 1240, 300), 12, fill=PANEL)
        d.text((850, 126), "state", font=font(BOLD, 20), fill=DIM)
        d.text((850, 160), f"cursor = {mm(cur)}", font=font(MONO, 22), fill=AMBER)
        d.text((850, 196), f"best   = {mm(bstart)}–{mm(bstart + blen)}", font=font(MONO, 22), fill=GREEN)
        d.text((850, 232), f"len    = {blen}", font=font(MONO, 22), fill=GREEN)
        d.multiline_text((850, 268), note, font=font(SANS, 15), fill=FG)
        hl = {47, 48, 49} if blen < 180 else {51}
        if shown == 0:
            hl = {43, 44, 45}
        draw_code(d, code_range(43, 51), 64, 372, size=14, highlight=hl, dim_others=True)
        out.append((img, lines))

    img, d = canvas("Edge cases", "7 / 9")
    bullets(d, [
        "Fully booked day (employee 103): no gap is ever found, so best stays 0 → 09:00,09:00,0",
        "Overlapping or back-to-back meetings: s ≤ cursor, so they merge with no gap",
        "Meetings outside business hours are clipped away but the date still appears",
        "Month end, year end and leap years are handled by nextDate",
        "A meeting ending exactly at 00:00 adds nothing to the next day",
        "Blank lines in the input are skipped and not counted",
    ], 64, 116, size=23, gap=12, maxw=1150)
    out.append((img, [
        "A few edge cases. Employee 103 is in an offsite for the whole business day, so no gap is ever found. The output is a zero length slot starting at 9 AM.",
        "Back to back meetings merge because the next start is not greater than the cursor.",
        "Meetings entirely outside business hours are clipped away, but their date still shows up. Month ends, year ends, and leap years are handled by next Date.",
    ]))

    img, d = canvas("Output for the sample", "8 / 9")
    exe = os.path.join(tempfile.mkdtemp(), "sol")
    subprocess.run(["g++", "-std=c++17", "-O2", "-o", exe, os.path.join(HERE, "solution.cpp")], check=True)
    res = subprocess.run([exe],
                         stdin=open(os.path.join(HERE, "sample_input.txt")), capture_output=True, text=True).stdout
    draw_code(d, [(i + 1, s) for i, s in enumerate(res.splitlines())], 80, 130, size=22, width=700)
    notes = ["101: free 14:00–17:00 (180)", "102 Mar 11: whole day free", "102 Mar 12: free after 10:00", "103: fully booked"]
    for i, t in enumerate(notes):
        d.text((820, 135 + i * 32), t, font=font(SANS, 19), fill=DIM)
    out.append((img, [
        "Here is the program's output for the sample input.",
        "Employee 101 is free from 2 to 5. Employee 102 is free all of March 11, and from 10 to 5 on March 12. Employee 103 has no free time.",
    ]))

    img, d = canvas("Complexity & takeaways", "9 / 9")
    d.text((64, 120), "Time:   O(N log N + total days spanned)", font=font(MONO, 26), fill=GREEN)
    d.text((64, 170), "Space:  O(N + days spanned)", font=font(MONO, 26), fill=GREEN)
    bullets(d, [
        "Normalize every time to minutes since midnight",
        "Split at midnight, then clip to business hours",
        "Sort each day's intervals, sweep with one cursor",
        "Strict '>' keeps the earliest of tied gaps",
    ], 64, 260, size=25, gap=14)
    out.append((img, [
        ("Time complexity is O of N log N for parsing and sorting, plus the number of days that meetings span. Space is linear.",
         "Time complexity is O of N log N for parsing and sorting, plus the number of days that meetings span. Space is linear."),
        "To recap: convert times to minutes, split at midnight, clip to business hours, then sort and sweep with a single cursor. Thanks for watching.",
    ]))
    return out


# ---------- rendering ----------

def speak(text, path):
    voice = "mb-us2"
    if subprocess.run(["espeak-ng", "-v", voice, "-q", "x"], capture_output=True).returncode:
        voice = "en-us"
    subprocess.run(["espeak-ng", "-v", voice, "-s", "148", "-g", "4", "-a", "70", "-w", path, text], check=True)
    with wave.open(path) as w:
        return w.getnframes() / w.getframerate()


def srt_time(t):
    ms = int(round(t * 1000))
    return f"{ms // 3600000:02d}:{ms // 60000 % 60:02d}:{ms // 1000 % 60:02d},{ms % 1000:03d}"


def main():
    out_dir = sys.argv[1] if len(sys.argv) > 1 else HERE
    work = tempfile.mkdtemp()
    pause = 0.45
    concat_v, concat_a, srt, transcript = [], [], [], []
    t = 0.0
    k = 0
    for si, (img, lines) in enumerate(scenes()):
        transcript.append([])
        for line in lines:
            cap, spoken = line if isinstance(line, tuple) else (line, line)
            k += 1
            wav = os.path.join(work, f"a{k:03d}.wav")
            dur = speak(spoken, wav) + pause
            png = os.path.join(work, f"f{k:03d}.png")
            caption(img, cap).save(png)
            concat_v += [f"file '{png}'", f"duration {dur:.3f}"]
            concat_a.append((wav, dur))
            srt.append(f"{k}\n{srt_time(t)} --> {srt_time(t + dur - pause)}\n{cap}\n")
            transcript[-1].append((t, cap))
            t += dur
    concat_v.append(f"file '{png}'")
    open(os.path.join(work, "v.txt"), "w").write("\n".join(concat_v) + "\n")

    # pad each clip of speech with silence to its slot length, then join
    padded = []
    for i, (wav, dur) in enumerate(concat_a):
        p = os.path.join(work, f"p{i:03d}.wav")
        subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", wav, "-af", f"apad=whole_dur={dur:.3f}",
                        "-ar", "22050", "-ac", "1", p], check=True)
        padded.append(f"file '{p}'")
    open(os.path.join(work, "a.txt"), "w").write("\n".join(padded) + "\n")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(work, "a.txt"),
                    os.path.join(work, "voice.wav")], check=True)

    mp4 = os.path.join(out_dir, "longest_free_slot.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", os.path.join(work, "v.txt"),
                    "-i", os.path.join(work, "voice.wav"), "-vf", "fps=30,format=yuv420p", "-c:v", "libx264",
                    "-tune", "stillimage", "-crf", "20", "-c:a", "aac", "-b:a", "96k", "-shortest",
                    "-movflags", "+faststart", mp4], check=True)
    open(os.path.join(out_dir, "longest_free_slot.srt"), "w").write("\n".join(srt))
    with open(os.path.join(out_dir, "transcript.md"), "w") as f:
        f.write("# Longest Free Slot — Video Transcript\n\n")
        f.write(f"Video: `longest_free_slot.mp4` ({int(t // 60)}:{int(t % 60):02d}) · Code: `solution.cpp`\n")
        titles = ["Intro", "1. The problem", "2. The plan", "3. Helpers", "3. Helpers", "3. Helpers",
                  "4. Reading the input", "4. Reading the input", "4. Reading the input",
                  "5. Meetings that cross midnight", "5. Meetings that cross midnight",
                  "6. Sort & sweep", "6. Sort & sweep", "6. Sort & sweep", "6. Sort & sweep", "6. Sort & sweep",
                  "7. Edge cases", "8. Output", "9. Complexity & takeaways"]
        last = None
        for title, lines in zip(titles, transcript):
            if title != last:
                f.write(f"\n## {title}\n\n")
                last = title
            for ts, cap in lines:
                f.write(f"**[{int(ts // 60)}:{int(ts % 60):02d}]** {cap}\n\n")
    print(mp4, f"{t:.1f}s")


if __name__ == "__main__":
    main()
