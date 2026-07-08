"""Turn a Day-NN SPA practice script (Markdown) into an mp4 with TTS narration
and text slides. Usage: python make_video.py scripts/day01.md videos/day01.mp4
"""
import asyncio
import re
import subprocess
import sys
import textwrap
from pathlib import Path

import edge_tts
from PIL import Image, ImageDraw, ImageFont

WIDTH, HEIGHT = 1280, 720
VOICE = "en-US-AriaNeural"
THINK_TIME = 12  # seconds of silence while the viewer practices
FONT_PATH = "C:/Windows/Fonts/malgunbd.ttf"
FONT_PATH_REGULAR = "C:/Windows/Fonts/malgun.ttf"
FFMPEG = "ffmpeg"

PART_COLORS = {
    1: (30, 60, 90),
    2: (35, 80, 60),
    3: (90, 60, 30),
    4: (70, 40, 90),
    5: (80, 30, 40),
}

PART_PROMPTS = {
    3: "Describe the picture.",
    4: "Look at the graph and describe the trend.",
}


def parse_day_file(md_path: Path):
    text = md_path.read_text(encoding="utf-8")
    title_line = text.splitlines()[0].lstrip("# ").strip()

    parts = []
    for m in re.finditer(r"^## Part (\d)\.\s*(.+?)\s*\(", text, re.MULTILINE):
        part_num = int(m.group(1))
        part_title = m.group(2).strip()
        start = m.end()
        next_m = re.search(r"^## Part \d\.", text[start:], re.MULTILINE)
        section = text[start : start + next_m.start()] if next_m else text[start:]
        pairs = re.findall(r"\*\*(.+?)\*\*\s*\n>\s*(.+)", section)
        parts.append((part_num, part_title, pairs))
    return title_line, parts


def build_segments(part_num, part_title, pairs):
    """Return a list of (spoken_text_or_None, heading, body, tag) tuples."""
    segs = []

    if part_num in (1, 2):
        for label, answer in pairs:
            question = re.sub(r"^Q\d+\.\s*", "", label).strip()
            segs.append((f"Question: {question}", question, None, None))
            segs.append((None, question, None, "Think Time"))
            segs.append((f"Model answer. {answer}", question, answer, None))
    elif part_num in (3, 4):
        for label, answer in pairs:
            note = label.strip("[]").replace("화면 안내: ", "")
            segs.append((PART_PROMPTS[part_num], note, None, None))
            segs.append((None, note, None, "Think Time"))
            segs.append((f"Model answer. {answer}", note, answer, None))
    elif part_num == 5:
        note, article = pairs[0]
        _, summary = pairs[1]
        clean_note = note.strip("[]").replace("화면 안내: ", "")
        segs.append(("Read the following article.", clean_note, None, None))
        segs.append((article, "Article", article, None))
        segs.append(("Now, summarize the article in your own words.", "Article", article, None))
        segs.append((None, "Article", article, "Think Time"))
        segs.append((f"Model summary. {summary}", "Article", summary, None))
    return segs


def wrap(text, width):
    if not text:
        return []
    out = []
    for para in text.split("\n"):
        out.extend(textwrap.wrap(para, width=width) or [""])
    return out


def make_slide(path, part_num, part_label, heading, body, tag=None):
    img = Image.new("RGB", (WIDTH, HEIGHT), color=PART_COLORS.get(part_num, (40, 40, 40)))
    draw = ImageDraw.Draw(img)
    font_label = ImageFont.truetype(FONT_PATH, 30)
    font_heading = ImageFont.truetype(FONT_PATH, 34)
    font_body = ImageFont.truetype(FONT_PATH_REGULAR, 32)
    font_tag = ImageFont.truetype(FONT_PATH, 44)

    draw.text((60, 50), part_label, font=font_label, fill=(255, 210, 120))

    lines = wrap(heading, 46)
    y = 130
    for line in lines:
        draw.text((60, y), line, font=font_heading, fill=(255, 255, 255))
        y += 46

    if body:
        y += 30
        body_lines = wrap(body, 52)
        for line in body_lines[:12]:
            draw.text((60, y), line, font=font_body, fill=(220, 230, 240))
            y += 44

    if tag:
        bbox = draw.textbbox((0, 0), tag, font=font_tag)
        tw = bbox[2] - bbox[0]
        draw.text(((WIDTH - tw) // 2, HEIGHT - 140), tag, font=font_tag, fill=(255, 200, 60))

    img.save(path)


async def tts_to_file(text, out_path):
    communicate = edge_tts.Communicate(text, VOICE)
    await communicate.save(str(out_path))


def silent_audio(out_path, seconds):
    subprocess.run(
        [FFMPEG, "-y", "-f", "lavfi", "-i", f"anullsrc=r=44100:cl=mono",
         "-t", str(seconds), "-q:a", "9", str(out_path)],
        check=True, capture_output=True,
    )


def make_clip(image_path, audio_path, clip_path):
    subprocess.run(
        [FFMPEG, "-y", "-loop", "1", "-i", str(image_path), "-i", str(audio_path),
         "-c:v", "libx264", "-tune", "stillimage", "-c:a", "aac", "-b:a", "160k",
         "-pix_fmt", "yuv420p", "-shortest", str(clip_path)],
        check=True, capture_output=True,
    )


def concat_clips(clip_paths, out_path, work_dir):
    list_file = work_dir / "concat_list.txt"
    with open(list_file, "w", encoding="utf-8") as f:
        for p in clip_paths:
            f.write(f"file '{p.resolve().as_posix()}'\n")
    subprocess.run(
        [FFMPEG, "-y", "-f", "concat", "-safe", "0", "-i", str(list_file),
         "-c", "copy", str(out_path)],
        check=True, capture_output=True,
    )


def main(md_path_str, out_path_str):
    md_path = Path(md_path_str)
    out_path = Path(out_path_str)
    work_dir = out_path.parent / f"_work_{out_path.stem}"
    work_dir.mkdir(parents=True, exist_ok=True)

    day_title, parts = parse_day_file(md_path)

    clip_paths = []
    idx = 0

    # Day intro
    intro_wav = work_dir / "intro.mp3"
    asyncio.run(tts_to_file(f"{day_title}. Let's begin.", intro_wav))
    intro_png = work_dir / "intro.png"
    make_slide(intro_png, 1, "SPA Speaking Practice", day_title, None)
    intro_clip = work_dir / "clip_intro.mp4"
    make_clip(intro_png, intro_wav, intro_clip)
    clip_paths.append(intro_clip)

    for part_num, part_title, pairs in parts:
        part_label = f"Part {part_num} · {part_title}"

        # Part intro
        idx += 1
        png = work_dir / f"slide_{idx:03d}.png"
        audio = work_dir / f"audio_{idx:03d}.mp3"
        clip = work_dir / f"clip_{idx:03d}.mp4"
        asyncio.run(tts_to_file(f"Part {part_num}: {part_title}.", audio))
        make_slide(png, part_num, part_label, part_title, None)
        make_clip(png, audio, clip)
        clip_paths.append(clip)

        for spoken, heading, body, tag in build_segments(part_num, part_title, pairs):
            idx += 1
            png = work_dir / f"slide_{idx:03d}.png"
            audio = work_dir / f"audio_{idx:03d}.mp3"
            clip = work_dir / f"clip_{idx:03d}.mp4"

            if spoken:
                asyncio.run(tts_to_file(spoken, audio))
            else:
                silent_audio(audio, THINK_TIME)

            make_slide(png, part_num, part_label, heading, body, tag=tag)
            make_clip(png, audio, clip)
            clip_paths.append(clip)

    concat_clips(clip_paths, out_path, work_dir)
    print(f"Done: {out_path}")


if __name__ == "__main__":
    main(sys.argv[1], sys.argv[2])
