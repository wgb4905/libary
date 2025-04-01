from PIL import Image, ImageDraw, ImageFont
import os
from django.conf import settings
import textwrap

def generate_book_cover(title, author=None, output_path=None):
    """生成无方框的纯文字封面"""
    width, height = 2480, 3508  # A4尺寸
    
    # 创建画布
    img = Image.new('RGB', (width, height), (250, 250, 240))  # 米白背景
    draw = ImageDraw.Draw(img)
    
    # 加载字体
    font_path = os.path.join(settings.BASE_DIR, 'static', 'fonts', 'simsunb.ttf')
    if not os.path.exists(font_path):
        raise ValueError(f"字体文件未找到: {font_path}")
    
    # 字体配置
    title_font = ImageFont.truetype(font_path, 200)
    author_font = ImageFont.truetype(font_path, 120)

    # --- 书名处理 ---
    max_line_width = width * 0.8
    max_lines = 3
    chars_per_line = 10
    
    wrapped_lines = []
    for line in textwrap.wrap(title, width=chars_per_line):
        if len(wrapped_lines) >= max_lines:
            wrapped_lines[-1] = wrapped_lines[-1] + "…"
            break
        wrapped_lines.append(line)
    
    # 绘制书名（移除了stroke_width参数）
    line_height = title_font.size * 1.2
    start_y = height * 0.2
    
    for i, line in enumerate(wrapped_lines):
        line_text = f"《{line}》" if i == 0 else line
        line_width = draw.textlength(line_text, font=title_font)
        draw.text(
            ((width - line_width) / 2, start_y + i * line_height),
            line_text,
            fill=(10, 10, 10),  # 纯黑色
            font=title_font      # 移除了stroke相关参数
        )
    
    # --- 作者信息 ---
    if author:
        author_text = f"— {author[:15]} —" if len(author) > 15 else f"— {author} —"
        author_width = draw.textlength(author_text, font=author_font)
        draw.text(
            ((width - author_width) / 2, height * 0.7),
            author_text,
            fill=(50, 50, 50),
            font=author_font     # 移除了stroke相关参数
        )
    
    if output_path:
        os.makedirs(os.path.dirname(output_path), exist_ok=True)
        img.save(output_path, 'PNG', quality=100)
        return output_path
    return img