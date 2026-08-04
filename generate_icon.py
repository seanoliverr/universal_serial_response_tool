"""生成串口工具图标（标准 RGBA 多尺寸 ico，兼容 Qt 与 Windows）"""
from PIL import Image, ImageDraw


def draw_icon(size):
    """在 size x size 的画布上绘制串口插头图标，返回 RGBA 图像。"""
    img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
    draw = ImageDraw.Draw(img)

    cx, cy = size / 2, size / 2

    plug_color = (30, 60, 130, 255)    # 深蓝色插头
    pin_color = (255, 200, 50, 255)    # 黄色引脚
    wave_color = (100, 180, 255, 255)  # 蓝色信号波形

    # 插头主体（圆角矩形）
    plug_w = size * 0.45
    plug_h = size * 0.5
    plug_x0 = cx - plug_w / 2
    plug_y0 = cy - plug_h / 2 + size * 0.05
    plug_x1 = cx + plug_w / 2
    plug_y1 = cy + plug_h / 2 + size * 0.05
    radius = max(1, int(size * 0.06))
    draw.rounded_rectangle([plug_x0, plug_y0, plug_x1, plug_y1],
                           radius=radius, fill=plug_color)

    # 三个引脚（插头下方）
    pin_w = max(1, plug_w * 0.12)
    pin_gap = plug_w * 0.14
    pin_len = size * 0.16
    total_w = 3 * pin_w + 2 * pin_gap
    start_x = cx - total_w / 2
    for i in range(3):
        px0 = start_x + i * (pin_w + pin_gap)
        draw.rectangle([px0, plug_y1, px0 + pin_w, plug_y1 + pin_len],
                       fill=pin_color)

    # 上方信号波形（折线）
    wave_w = size * 0.6
    wave_h = size * 0.18
    wx = cx - wave_w / 2
    wy = cy - plug_h / 2 - size * 0.02
    line_w = max(1, int(size * 0.05))
    points = []
    segs = 6
    for i in range(segs + 1):
        x = wx + wave_w * i / segs
        y = wy - (wave_h if i % 2 == 0 else 0)
        points.append((x, y))
    draw.line(points, fill=wave_color, width=line_w, joint='curve')

    return img


def create_serial_icon():
    sizes = [16, 24, 32, 48, 64, 128, 256]
    base = draw_icon(256)
    images = [base.resize((s, s), Image.LANCZOS) for s in sizes]
    base.save('icon.ico', format='ICO',
              sizes=[(s, s) for s in sizes])
    print(f"图标生成成功: icon.ico ({len(sizes)}个尺寸)")


if __name__ == '__main__':
    create_serial_icon()
