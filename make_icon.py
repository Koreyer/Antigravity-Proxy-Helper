# -*- coding: utf-8 -*-
from PIL import Image, ImageDraw

SIZE = 1024
BG_TOP = (79, 70, 229)
BG_BOTTOM = (139, 92, 246)
INK = (17, 24, 39)
WHITE = (248, 250, 252)
GREEN = (52, 211, 153)


def build():
    grad = Image.new("RGB", (SIZE, SIZE))
    pen = ImageDraw.Draw(grad)
    for y in range(SIZE):
        t = y / (SIZE - 1)
        pen.line([(0, y), (SIZE, y)], fill=tuple(int(BG_TOP[i] + (BG_BOTTOM[i] - BG_TOP[i]) * t) for i in range(3)))

    mask = Image.new("L", (SIZE, SIZE), 0)
    ImageDraw.Draw(mask).rounded_rectangle([0, 0, SIZE - 1, SIZE - 1], radius=int(SIZE * 0.22), fill=255)

    img = Image.new("RGBA", (SIZE, SIZE), (0, 0, 0, 0))
    img.paste(grad, (0, 0), mask)
    draw = ImageDraw.Draw(img)

    draw.line([(SIZE // 2, int(SIZE * 0.34)), (SIZE // 2, int(SIZE * 0.21))], fill=WHITE, width=int(SIZE * 0.022))
    r = int(SIZE * 0.045)
    draw.ellipse([SIZE // 2 - r, int(SIZE * 0.21) - r, SIZE // 2 + r, int(SIZE * 0.21) + r], fill=GREEN)

    draw.rounded_rectangle(
        [int(SIZE * 0.22), int(SIZE * 0.34), int(SIZE * 0.78), int(SIZE * 0.80)],
        radius=int(SIZE * 0.10), fill=WHITE, outline=INK, width=int(SIZE * 0.014),
    )
    draw.rounded_rectangle(
        [int(SIZE * 0.155), int(SIZE * 0.50), int(SIZE * 0.22), int(SIZE * 0.65)],
        radius=int(SIZE * 0.03), fill=WHITE, outline=INK, width=int(SIZE * 0.012),
    )
    draw.rounded_rectangle(
        [int(SIZE * 0.78), int(SIZE * 0.50), int(SIZE * 0.845), int(SIZE * 0.65)],
        radius=int(SIZE * 0.03), fill=WHITE, outline=INK, width=int(SIZE * 0.012),
    )

    eye = int(SIZE * 0.055)
    for cx in (int(SIZE * 0.375), int(SIZE * 0.625)):
        cy = int(SIZE * 0.565)
        draw.ellipse([cx - eye, cy - eye, cx + eye, cy + eye], fill=INK)
        hl = int(eye * 0.36)
        draw.ellipse([cx - eye + hl, cy - eye + hl, cx - eye + hl * 2, cy - eye + hl * 2], fill=WHITE)

    draw.rounded_rectangle(
        [int(SIZE * 0.415), int(SIZE * 0.675), int(SIZE * 0.585), int(SIZE * 0.71)],
        radius=int(SIZE * 0.017), fill=INK,
    )
    return img


if __name__ == "__main__":
    icon = build()
    icon.save("icon.png")
    icon.save("icon.ico", sizes=[(16, 16), (24, 24), (32, 32), (48, 48), (64, 64), (128, 128), (256, 256)])
    print("icon.png / icon.ico generated")
