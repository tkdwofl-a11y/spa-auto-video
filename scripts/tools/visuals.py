"""Generate the Part 3 (picture) and Part 4 (graph) images referenced by each
day's [화면 안내: ...] note, so make_video.py can embed a real image instead
of a text-only placeholder.
"""
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from PIL import Image, ImageDraw

BG = "#3a2050"
FG = "#e8e6f0"
GRID = "#5a4570"
LINE_COLORS = ["#ffd27f", "#7fd6ff", "#8fe38f", "#ff9e9e"]

GRAPH_DATA = {
    1: {
        "type": "bar",
        "title": "Company Sales, 2020-2024 ($M)",
        "x": ["2020", "2021", "2022", "2023", "2024"],
        "series": {"Sales": [100, 160, 230, 310, 400]},
    },
    2: {
        "type": "line",
        "title": "Product A vs Product B Sales, 2020-2024 ($M)",
        "x": ["2020", "2021", "2022", "2023", "2024"],
        "series": {
            "Product A": [400, 380, 360, 340, 320],
            "Product B": [150, 180, 250, 330, 400],
        },
    },
    3: {
        "type": "line",
        "title": "Auto Sales by Region, 2020-2024 ($M)",
        "x": ["2020", "2021", "2022", "2023", "2024"],
        "series": {
            "Korea": [250, 255, 245, 250, 248],
            "United States": [300, 290, 200, 230, 260],
            "Europe": [150, 170, 195, 230, 290],
        },
    },
    4: {
        "type": "line",
        "title": "Electricity Generation Mix, 2015-2024 (%)",
        "x": [str(y) for y in range(2015, 2025)],
        "series": {
            "Renewable": [15, 16, 17, 18, 20, 22, 26, 32, 40, 45],
            "Fossil Fuel": [85, 84, 83, 82, 80, 78, 74, 68, 60, 55],
        },
    },
    5: {
        "type": "line",
        "title": "Remote Work Adoption by Industry, 2019-2024 (%)",
        "x": [str(y) for y in range(2019, 2025)],
        "series": {
            "Tech": [40, 55, 65, 70, 72, 73],
            "Finance": [10, 20, 35, 50, 60, 68],
            "Manufacturing": [5, 6, 7, 8, 9, 10],
        },
    },
}


def draw_graph(day_num, out_path, size=(760, 480)):
    data = GRAPH_DATA[day_num]
    dpi = 100
    fig, ax = plt.subplots(figsize=(size[0] / dpi, size[1] / dpi), dpi=dpi)
    fig.patch.set_facecolor(BG)
    ax.set_facecolor(BG)

    if data["type"] == "bar":
        (label, values), = data["series"].items()
        ax.bar(data["x"], values, color=LINE_COLORS[0])
    else:
        for (label, values), color in zip(data["series"].items(), LINE_COLORS):
            ax.plot(data["x"], values, marker="o", label=label, color=color, linewidth=2.5)
        ax.legend(facecolor=BG, labelcolor=FG, edgecolor=GRID, fontsize=9)

    ax.set_title(data["title"], color=FG, fontsize=12)
    ax.tick_params(colors=FG)
    ax.grid(color=GRID, alpha=0.5)
    for spine in ax.spines.values():
        spine.set_color(GRID)

    fig.tight_layout()
    fig.savefig(out_path, facecolor=BG)
    plt.close(fig)


def _person(draw, x, y, color, helmet=False):
    draw.ellipse((x - 14, y - 14, x + 14, y + 14), fill=color)
    if helmet:
        draw.arc((x - 16, y - 24, x + 16, y + 4), 180, 360, fill=(255, 220, 90), width=5)
    draw.polygon([(x - 20, y + 70), (x + 20, y + 70), (x + 26, y + 16), (x - 26, y + 16)], fill=color)


def _laptop(draw, x, y):
    draw.rectangle((x - 30, y - 20, x + 30, y), outline=(230, 230, 240), width=3)
    draw.rectangle((x - 34, y, x + 34, y + 6), fill=(230, 230, 240))


SCENE_BG = (58, 32, 80)
PEOPLE_COLORS = [(255, 190, 130), (140, 210, 255), (170, 230, 170), (240, 160, 200)]


def draw_picture(day_num, out_path, size=(760, 480)):
    img = Image.new("RGB", size, SCENE_BG)
    draw = ImageDraw.Draw(img)
    w, h = size

    if day_num == 1:  # office meeting room, 4 people around a table
        draw.ellipse((w * 0.15, h * 0.55, w * 0.85, h * 0.85), fill=(80, 55, 100))
        positions = [(w * 0.25, h * 0.35), (w * 0.45, h * 0.3), (w * 0.6, h * 0.35), (w * 0.75, h * 0.3)]
        for (x, y), color in zip(positions, PEOPLE_COLORS):
            _person(draw, x, y, color)
        _laptop(draw, w * 0.45, h * 0.6)
        _laptop(draw, w * 0.62, h * 0.62)

    elif day_num == 2:  # whiteboard brainstorming
        draw.rectangle((w * 0.15, h * 0.15, w * 0.65, h * 0.55), fill=(240, 240, 245), outline=(20, 20, 20), width=4)
        draw.line((w * 0.2, h * 0.45, w * 0.35, h * 0.25, w * 0.5, h * 0.4, w * 0.6, h * 0.2), fill=(220, 60, 60), width=4)
        positions = [(w * 0.3, h * 0.75), (w * 0.5, h * 0.78), (w * 0.7, h * 0.75), (w * 0.85, h * 0.7)]
        for (x, y), color in zip(positions, PEOPLE_COLORS):
            _person(draw, x, y, color)

    elif day_num == 3:  # factory floor
        draw.rectangle((w * 0.55, h * 0.15, w * 0.95, h * 0.65), fill=(90, 90, 100), outline=(30, 30, 30), width=3)
        for i in range(3):
            draw.rectangle((w * (0.6 + i * 0.12), h * 0.2, w * (0.68 + i * 0.12), h * 0.6), fill=(120, 120, 130))
        _person(draw, w * 0.15, h * 0.55, PEOPLE_COLORS[0])
        draw.rectangle((w * 0.19, h * 0.5, w * 0.25, h * 0.58), outline=(230, 230, 240), width=2)
        for i, x in enumerate([w * 0.3, w * 0.37, w * 0.44]):
            _person(draw, x, h * 0.6, PEOPLE_COLORS[i + 1], helmet=True)

    elif day_num == 4:  # international conference
        draw.rectangle((w * 0.35, h * 0.15, w * 0.75, h * 0.4), fill=(230, 230, 240), outline=(20, 20, 20), width=3)
        for i, v in enumerate([0.6, 0.8, 0.5, 0.9]):
            bx = w * (0.4 + i * 0.09)
            draw.rectangle((bx, h * 0.4 - v * h * 0.2, bx + w * 0.06, h * 0.4), fill=(120, 190, 230))
        _person(draw, w * 0.5, h * 0.55, PEOPLE_COLORS[0])
        draw.rectangle((w * 0.46, h * 0.62, w * 0.54, h * 0.66), fill=(80, 60, 40))
        for row in range(2):
            for col in range(6):
                x = w * (0.15 + col * 0.12)
                y = h * (0.75 + row * 0.12)
                draw.ellipse((x - 8, y - 8, x + 8, y + 8), fill=PEOPLE_COLORS[(row + col) % 4])

    elif day_num == 5:  # startup office, standing desk
        draw.rectangle((w * 0.35, h * 0.55, w * 0.7, h * 0.62), fill=(150, 110, 70))
        draw.rectangle((w * 0.37, h * 0.62, w * 0.4, h * 0.85), fill=(90, 65, 40))
        draw.rectangle((w * 0.65, h * 0.62, w * 0.68, h * 0.85), fill=(90, 65, 40))
        _laptop(draw, w * 0.52, h * 0.5)
        positions = [(w * 0.3, h * 0.4), (w * 0.45, h * 0.35), (w * 0.6, h * 0.38), (w * 0.75, h * 0.42)]
        for (x, y), color in zip(positions, PEOPLE_COLORS):
            _person(draw, x, y, color)
        draw.ellipse((w * 0.85, h * 0.5, w * 0.95, h * 0.6), fill=(90, 160, 90))
        draw.rectangle((w * 0.89, h * 0.6, w * 0.91, h * 0.8), fill=(110, 80, 50))

    img.save(out_path)
