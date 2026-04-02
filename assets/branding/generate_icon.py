from pathlib import Path

from PIL import Image, ImageDraw


def make_icon(size: int) -> Image.Image:
    img = Image.new("RGBA", (size, size), (12, 18, 34, 255))
    draw = ImageDraw.Draw(img)

    # Outer rounded frame
    pad = int(size * 0.07)
    draw.rounded_rectangle(
        (pad, pad, size - pad, size - pad),
        radius=int(size * 0.18),
        fill=(20, 31, 56, 255),
        outline=(64, 97, 180, 255),
        width=max(2, int(size * 0.02)),
    )

    # LCD panel area
    lcd_pad_x = int(size * 0.16)
    lcd_pad_y = int(size * 0.2)
    draw.rounded_rectangle(
        (
            lcd_pad_x,
            lcd_pad_y,
            size - lcd_pad_x,
            size - lcd_pad_y,
        ),
        radius=int(size * 0.08),
        fill=(5, 60, 92, 255),
        outline=(122, 222, 255, 255),
        width=max(2, int(size * 0.02)),
    )

    # Frequency text bars (stylized)
    y1 = int(size * 0.37)
    y2 = int(size * 0.57)
    x1 = int(size * 0.25)
    x2 = int(size * 0.75)

    draw.line((x1, y1, x2, y1), fill=(145, 255, 214, 255), width=max(2, int(size * 0.04)))
    draw.line((x1, y2, x2, y2), fill=(145, 255, 214, 255), width=max(2, int(size * 0.04)))

    # Knob accent
    knob_r = int(size * 0.07)
    knob_x = int(size * 0.82)
    knob_y = int(size * 0.82)
    draw.ellipse(
        (knob_x - knob_r, knob_y - knob_r, knob_x + knob_r, knob_y + knob_r),
        fill=(238, 248, 255, 255),
        outline=(118, 138, 177, 255),
        width=max(1, int(size * 0.01)),
    )

    return img


def main() -> None:
    out_dir = Path(__file__).resolve().parent
    out_file = out_dir / "app.ico"

    sizes = [16, 24, 32, 48, 64, 128, 256]
    base = make_icon(256)
    images = [base.resize((s, s), Image.Resampling.LANCZOS) for s in sizes]

    images[0].save(out_file, format="ICO", sizes=[(s, s) for s in sizes])
    print(f"Icon generated: {out_file}")


if __name__ == "__main__":
    main()
