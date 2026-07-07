#!/usr/bin/env python3
"""
Generate a GIF and video of the full R₀ propagation panel for the README.
Requires: pip install numpy pillow
Optional video: pip install imageio imageio-ffmpeg
"""

import re
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from pathlib import Path

# Parameters (match index.html)
POPULATION = 100
DAYS = 10
STEPS_PER_DAY = 15
TOTAL_STEPS = DAYS * STEPS_PER_DAY
INFECTIOUS_PERIOD = 5 * STEPS_PER_DAY
CONTACT_RADIUS = 0.1
SPEED = 0.018
AVG_CONTACTS = 6
AGENT_RADIUS = 0.022

# GIF / Video
COLS, ROWS = 5, 4
CELL_W, CELL_H = 170, 195
CREDIT_HEIGHT = 32
IMG_W = COLS * CELL_W + 40
IMG_H = ROWS * CELL_H + 70 + CREDIT_HEIGHT
FPS = 10  # 25% más rápido que antes (8 * 1.25)
OUTPUT_GIF = Path(__file__).parent / "assets" / "r0_simulation.gif"
OUTPUT_VIDEO = Path(__file__).parent / "assets" / "r0_simulation.mp4"
CREDIT_TEXT = "JDConejeros/R0_animation"
GITHUB_LOGO_URL = "https://github.com/favicon.ico"

def parse_r0_midpoint(r0_display: str, base_r0: float) -> float:
    """If r0_display is a range, return midpoint; otherwise base_r0."""
    m = re.match(r"^(\d+\.?\d*)\s*[-–]\s*(\d+\.?\d*)$", r0_display.strip())
    if m:
        return (float(m.group(1)) + float(m.group(2))) / 2
    return base_r0


DISEASES = [
    {"name": "Measles", "r0_display": "12–18", "r0": 15},
    {"name": "Pertussis", "r0_display": "12–17", "r0": 14.5},
    {"name": "Chickenpox", "r0_display": "10–12", "r0": 11},
    {"name": "Mumps", "r0_display": "10–12", "r0": 11},
    {"name": "Norovirus", "r0_display": "7.2", "r0": 7.2},
    {"name": "Rubella", "r0_display": "6–7", "r0": 6.5},
    {"name": "Polio", "r0_display": "5–7", "r0": 6},
    {"name": "Smallpox", "r0_display": "3.5–6.0", "r0": 4.75},
    {"name": "HIV/AIDS", "r0_display": "2–5", "r0": 3.5},
    {"name": "SARS", "r0_display": "2–4", "r0": 3},
    {"name": "Diphtheria", "r0_display": "2.6", "r0": 2.6},
    {"name": "Common cold", "r0_display": "2–3", "r0": 2.5},
    {"name": "COVID-19", "r0_display": "2.9–20", "r0": 11.45},
    {"name": "Mpox", "r0_display": "2.1", "r0": 2.1},
    {"name": "Ebola", "r0_display": "1.8", "r0": 1.8},
    {"name": "Influenza", "r0_display": "1.3", "r0": 1.3},
    {"name": "Andes hantavirus", "r0_display": "1.2", "r0": 1.2},
    {"name": "Nipah virus", "r0_display": "0.5", "r0": 0.5},
    {"name": "MERS", "r0_display": "0.5", "r0": 0.5},
]
# Use midpoint R0 when display is a range
for d in DISEASES:
    d["r0"] = parse_r0_midpoint(d["r0_display"], d["r0"])


def create_simulation(r0: float):
    transmission_prob = min(0.85, r0 / (INFECTIOUS_PERIOD * AVG_CONTACTS))
    agents = []
    for i in range(POPULATION):
        agents.append({
            "x": np.random.random(),
            "y": np.random.random(),
            "vx": (np.random.random() - 0.5) * 2 * SPEED,
            "vy": (np.random.random() - 0.5) * 2 * SPEED,
            "state": "infected" if i == 0 else "susceptible",
            "infected_at": 0 if i == 0 else -1,
        })
    return agents, transmission_prob


def resolve_collisions(agents):
    r2 = AGENT_RADIUS * 2
    r2_sq = r2 * r2
    for i in range(len(agents)):
        for j in range(i + 1, len(agents)):
            a, b = agents[i], agents[j]
            dx, dy = b["x"] - a["x"], b["y"] - a["y"]
            dist_sq = dx * dx + dy * dy
            if dist_sq < r2_sq and dist_sq > 1e-10:
                dist = np.sqrt(dist_sq)
                nx, ny = dx / dist, dy / dist
                overlap = r2 - dist
                a["x"] -= overlap * 0.5 * nx
                a["y"] -= overlap * 0.5 * ny
                b["x"] += overlap * 0.5 * nx
                b["y"] += overlap * 0.5 * ny
                v1n = a["vx"] * nx + a["vy"] * ny
                v2n = b["vx"] * nx + b["vy"] * ny
                a["vx"] += (v2n - v1n) * nx
                a["vy"] += (v2n - v1n) * ny
                b["vx"] += (v1n - v2n) * nx
                b["vy"] += (v1n - v2n) * ny


def step_simulation(agents, transmission_prob):
    infected = [a for a in agents if a["state"] == "infected"]
    for a in agents:
        a["x"] += a["vx"]
        a["y"] += a["vy"]
        if a["x"] <= 0 or a["x"] >= 1:
            a["vx"] *= -1
        if a["y"] <= 0 or a["y"] >= 1:
            a["vy"] *= -1
        a["x"] = np.clip(a["x"], 0, 1)
        a["y"] = np.clip(a["y"], 0, 1)
    resolve_collisions(agents)
    for inf in infected:
        for a in agents:
            if a["state"] != "susceptible":
                continue
            dx = a["x"] - inf["x"]
            dy = a["y"] - inf["y"]
            dist = np.sqrt(dx * dx + dy * dy)
            if dist < CONTACT_RADIUS and np.random.random() < transmission_prob:
                a["state"] = "infected"
                a["infected_at"] = 0
    for a in agents:
        if a["state"] == "infected" and a["infected_at"] >= 0:
            a["infected_at"] += 1
            if a["infected_at"] > INFECTIOUS_PERIOD:
                a["state"] = "recovered"
    currently_infected = sum(1 for a in agents if a["state"] == "infected")
    total_ever_infected = sum(1 for a in agents if a["state"] in ("infected", "recovered"))
    return currently_infected, total_ever_infected


def get_font(size: int, bold: bool = False):
    paths = (
        ["/System/Library/Fonts/Supplemental/Arial Bold.ttf", "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/System/Library/Fonts/Helvetica.ttc"]
        if bold
        else ["/System/Library/Fonts/Helvetica.ttc", "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"]
    )
    for path in paths:
        if Path(path).exists():
            try:
                return ImageFont.truetype(path, size)
            except Exception:
                pass
    return ImageFont.load_default()


def load_github_logo(size: int = 20):
    """Load GitHub logo. Returns None on failure."""
    try:
        import urllib.request
        from io import BytesIO
        req = urllib.request.Request(GITHUB_LOGO_URL, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=5) as r:
            img = Image.open(BytesIO(r.read())).convert("RGBA")
        img = img.resize((size, size), Image.Resampling.LANCZOS)
        # Invert for visibility on dark background
        arr = np.array(img)
        rgb = arr[:, :, :3]
        alpha = arr[:, :, 3:4]
        rgb_inv = 255 - rgb
        arr[:, :, :3] = np.where(alpha > 128, rgb_inv, rgb)
        return Image.fromarray(arr)
    except Exception:
        return None


def draw_credits(draw, img, font_credit, github_logo, y_base):
    """Draw credits (logo + text) bottom-right, vertically aligned."""
    pad_right = 20
    text = CREDIT_TEXT
    try:
        bbox = draw.textbbox((0, 0), text, font=font_credit)
        tw = bbox[2] - bbox[0]
        th = bbox[3] - bbox[1]
    except (AttributeError, TypeError):
        tw, th = len(text) * 6, 14
    logo_size = 18 if github_logo else 0
    gap = 6
    total_w = logo_size + gap + tw
    x_start = IMG_W - total_w - pad_right
    y_center = y_base + CREDIT_HEIGHT / 2
    if github_logo:
        logo_y = int(y_center - logo_size / 2)
        logo_rgba = github_logo.resize((logo_size, logo_size), Image.Resampling.LANCZOS)
        logo_rgb = Image.new("RGB", (logo_size, logo_size), (22, 27, 34))
        logo_rgb.paste(logo_rgba, (0, 0), logo_rgba)
        img.paste(logo_rgb, (int(x_start), logo_y))
        x_start += logo_size + gap
    text_y = int(y_center - th / 2)
    draw.text((int(x_start), text_y), text, fill=(139, 148, 158), font=font_credit)


def draw_cell(draw, agents, name, r0_display, day, infected, total_infected, x0, y0, w, h, font_sm, font_sm_bold, font_md, font_lg, show_final=False, days_label=DAYS):
    pad = 6
    sim_w, sim_h = w - 2 * pad, h - 50
    scale = min(sim_w, sim_h) - 4

    # Fondo
    draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(22, 27, 34), outline=(48, 54, 61))

    if show_final:
        # Final frame: count only
        draw.rectangle([x0, y0, x0 + w, y0 + h], fill=(13, 17, 23), outline=(63, 185, 80), width=2)
        text = f"{total_infected}"
        try:
            bbox = draw.textbbox((0, 0), text, font=font_lg)
            tw, th = bbox[2] - bbox[0], bbox[3] - bbox[1]
        except (AttributeError, TypeError):
            tw, th = draw.textsize(text, font=font_lg) if hasattr(draw, 'textsize') else (60, 40)
        tx = x0 + (w - tw) // 2
        ty = y0 + (h - th) // 2
        draw.text((tx, ty), text, fill=(63, 185, 80), font=font_lg)
    else:
        # Puntos
        for a in agents:
            px = x0 + pad + 2 + a["x"] * (scale - 4)
            py = y0 + pad + 2 + a["y"] * (scale - 4)
            r = 2
            if a["state"] == "susceptible":
                color, outline = (33, 38, 45), (48, 54, 61)
            elif a["state"] == "infected":
                color = outline = (63, 185, 80)
            else:
                color, outline = (72, 79, 88), (48, 54, 61)
            draw.ellipse([px - r, py - r, px + r, py + r], fill=color, outline=outline)

    # Header
    draw.text((x0 + 8, y0 + 4), name, fill=(230, 237, 243), font=font_sm_bold)
    r0_str = f"R0={r0_display}"
    try:
        bbox = draw.textbbox((0, 0), r0_str, font=font_sm)
        r0_w = bbox[2] - bbox[0]
    except (AttributeError, TypeError):
        r0_w = len(r0_str) * 7
    draw.text((x0 + w - r0_w - 8, y0 + 4), r0_str, fill=(35, 134, 54), font=font_sm)
    if not show_final:
        draw.text((x0 + 8, y0 + h - 22), f"Day {day}/{days_label} | {infected} inf", fill=(139, 148, 158), font=font_sm)


def main():
    OUTPUT_GIF.parent.mkdir(parents=True, exist_ok=True)
    font_sm = get_font(12)
    font_sm_bold = get_font(12, bold=True)
    font_md = get_font(16)
    font_md_bold = get_font(16, bold=True)
    font_lg = get_font(56)
    font_credit = get_font(12, bold=True)

    # Initialize all simulations
    sims = []
    for d in DISEASES:
        agents, tp = create_simulation(d["r0"])
        sims.append({"agents": agents, "tp": tp, "disease": d, "completed": False, "last_infected": 0, "total_ever_infected": 0})

    title = "R0 - First 10 days after outbreak onset | 100 people"
    github_logo = load_github_logo(18)
    credit_y = IMG_H - CREDIT_HEIGHT

    frames = []
    for step in range(TOTAL_STEPS):
        day = step // STEPS_PER_DAY
        img = Image.new("RGB", (IMG_W, IMG_H), color=(13, 17, 23))
        draw = ImageDraw.Draw(img)

        draw.text((20, 12), f"{title} | Day {day}/{DAYS}", fill=(230, 237, 243), font=font_md_bold)
        draw.rectangle([0, credit_y, IMG_W, IMG_H], fill=(22, 27, 34), outline=(48, 54, 61))
        draw_credits(draw, img, font_credit, github_logo, credit_y)

        for i, s in enumerate(sims):
            if not s["completed"]:
                infected, total_ever = step_simulation(s["agents"], s["tp"])
                s["last_infected"] = infected
                s["total_ever_infected"] = total_ever
                if infected >= POPULATION or step >= TOTAL_STEPS - 1:
                    s["completed"] = True

            col, row = i % COLS, i // COLS
            x0, y0 = 20 + col * CELL_W, 50 + row * CELL_H
            show_final = s["completed"]
            total_display = s["total_ever_infected"] if s["completed"] else s["last_infected"]
            draw_cell(draw, s["agents"], s["disease"]["name"], s["disease"]["r0_display"], day, s["last_infected"], total_display, x0, y0, CELL_W - 5, CELL_H - 5, font_sm, font_sm_bold, font_md, font_lg, show_final=show_final, days_label=DAYS)

        frames.append(img.copy())

    # Mark all simulations complete
    for s in sims:
        s["completed"] = True

    # Final frames with large counts (7 seconds)
    final_frames_count = FPS * 7
    for _ in range(final_frames_count):
        img = Image.new("RGB", (IMG_W, IMG_H), color=(13, 17, 23))
        draw = ImageDraw.Draw(img)
        draw.text((20, 12), "Infected after 10 days from outbreak onset", fill=(63, 185, 80), font=font_md_bold)
        draw.rectangle([0, credit_y, IMG_W, IMG_H], fill=(22, 27, 34), outline=(48, 54, 61))
        draw_credits(draw, img, font_credit, github_logo, credit_y)
        for i, s in enumerate(sims):
            col, row = i % COLS, i // COLS
            x0, y0 = 20 + col * CELL_W, 50 + row * CELL_H
            total = s["total_ever_infected"]
            draw_cell(draw, s["agents"], s["disease"]["name"], s["disease"]["r0_display"], DAYS, total, total, x0, y0, CELL_W - 5, CELL_H - 5, font_sm, font_sm_bold, font_md, font_lg, show_final=True, days_label=DAYS)
        frames.append(img.copy())

    duration = int(1000 / FPS)
    frames[0].save(OUTPUT_GIF, save_all=True, append_images=frames[1:], duration=duration, loop=0)
    print(f"GIF saved to: {OUTPUT_GIF} ({len(frames)} frames)")

    # Generate MP4 video
    try:
        import imageio
        frame_arrays = [np.array(f) for f in frames]
        imageio.mimsave(str(OUTPUT_VIDEO), frame_arrays, fps=FPS)
        print(f"Video saved to: {OUTPUT_VIDEO}")
    except ImportError:
        # Fallback: ffmpeg from command line
        import subprocess
        import tempfile
        tmpdir = Path(tempfile.mkdtemp())
        try:
            for i, f in enumerate(frames):
                f.save(tmpdir / f"frame_{i:05d}.png")
            subprocess.run([
                "ffmpeg", "-y", "-framerate", str(FPS), "-i", str(tmpdir / "frame_%05d.png"),
                "-c:v", "libx264", "-pix_fmt", "yuv420p", str(OUTPUT_VIDEO)
            ], check=True, capture_output=True)
            print(f"Video saved to: {OUTPUT_VIDEO}")
        except (FileNotFoundError, subprocess.CalledProcessError):
            print("To generate video: pip install imageio imageio-ffmpeg (or install ffmpeg)")
        finally:
            import shutil
            shutil.rmtree(tmpdir, ignore_errors=True)


if __name__ == "__main__":
    main()
