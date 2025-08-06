import os
import time
from datetime import datetime
from PIL import Image, ImageGrab, ImageDraw, ImageFont
import barcode
from barcode.writer import ImageWriter
from barcode import Code128, Code39, EAN13, EAN8, UPC
import io
import tempfile
from pathlib import Path

def capture_screen(save_path=None, region=None, delay=0):
    """屏幕截图
    Args:
        save_path: 保存路径，如果为None则返回PIL Image对象
        region: 截图区域 (x, y, width, height)，None表示全屏
        delay: 延时截图时间（秒）
    """
    if delay > 0:
        time.sleep(delay)
    
    if region:
        # 区域截图
        bbox = (region[0], region[1], region[0] + region[2], region[1] + region[3])
        screenshot = ImageGrab.grab(bbox)
    else:
        # 全屏截图
        screenshot = ImageGrab.grab()
    
    if save_path:
        screenshot.save(save_path)
        return save_path
    else:
        return screenshot

def annotate_screenshot(image_path, annotations, output_path=None):
    """给截图添加标注
    Args:
        image_path: 图片路径或PIL Image对象
        annotations: 标注列表，每个标注包含类型、位置、文本等信息
        output_path: 输出路径
    """
    if isinstance(image_path, str):
        image = Image.open(image_path)
    else:
        image = image_path.copy()
    
    draw = ImageDraw.Draw(image)
    
    # 尝试使用默认字体
    try:
        font = ImageFont.truetype("arial.ttf", 16)
    except:
        font = ImageFont.load_default()
    
    for annotation in annotations:
        ann_type = annotation.get('type', 'text')
        
        if ann_type == 'text':
            x, y = annotation['position']
            text = annotation['text']
            color = annotation.get('color', 'red')
            draw.text((x, y), text, fill=color, font=font)
        
        elif ann_type == 'rectangle':
            x, y, width, height = annotation['bbox']
            color = annotation.get('color', 'red')
            width_line = annotation.get('width', 2)
            draw.rectangle([x, y, x + width, y + height], outline=color, width=width_line)
        
        elif ann_type == 'circle':
            x, y, radius = annotation['center'][0], annotation['center'][1], annotation['radius']
            color = annotation.get('color', 'red')
            width_line = annotation.get('width', 2)
            draw.ellipse([x - radius, y - radius, x + radius, y + radius], 
                        outline=color, width=width_line)
        
        elif ann_type == 'arrow':
            start_x, start_y = annotation['start']
            end_x, end_y = annotation['end']
            color = annotation.get('color', 'red')
            width_line = annotation.get('width', 2)
            
            # 画箭头线
            draw.line([(start_x, start_y), (end_x, end_y)], fill=color, width=width_line)
            
            # 画箭头头部
            import math
            angle = math.atan2(end_y - start_y, end_x - start_x)
            arrow_length = 10
            arrow_angle = math.pi / 6
            
            x1 = end_x - arrow_length * math.cos(angle - arrow_angle)
            y1 = end_y - arrow_length * math.sin(angle - arrow_angle)
            x2 = end_x - arrow_length * math.cos(angle + arrow_angle)
            y2 = end_y - arrow_length * math.sin(angle + arrow_angle)
            
            draw.line([(end_x, end_y), (x1, y1)], fill=color, width=width_line)
            draw.line([(end_x, end_y), (x2, y2)], fill=color, width=width_line)
    
    if output_path:
        image.save(output_path)
        return output_path
    else:
        return image

def create_gif_from_images(image_paths, output_path, duration=500, loop=0):
    """从图片序列创建GIF
    Args:
        image_paths: 图片路径列表
        output_path: 输出GIF路径
        duration: 每帧持续时间（毫秒）
        loop: 循环次数，0表示无限循环
    """
    if not image_paths:
        raise ValueError("图片路径列表不能为空")
    
    images = []
    for path in image_paths:
        img = Image.open(path)
        # 转换为RGB模式以确保兼容性
        if img.mode != 'RGB':
            img = img.convert('RGB')
        images.append(img)
    
    # 保存为GIF
    images[0].save(
        output_path,
        save_all=True,
        append_images=images[1:],
        duration=duration,
        loop=loop
    )
    
    return output_path

def optimize_gif(input_path, output_path, max_colors=256, resize_ratio=1.0):
    """优化GIF文件大小
    Args:
        input_path: 输入GIF路径
        output_path: 输出GIF路径
        max_colors: 最大颜色数
        resize_ratio: 缩放比例
    """
    gif = Image.open(input_path)
    frames = []
    
    try:
        while True:
            frame = gif.copy()
            
            # 缩放
            if resize_ratio != 1.0:
                new_size = (int(frame.width * resize_ratio), int(frame.height * resize_ratio))
                frame = frame.resize(new_size, Image.Resampling.LANCZOS)
            
            # 减少颜色数
            if frame.mode != 'P':
                frame = frame.quantize(colors=max_colors)
            
            frames.append(frame)
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    
    if frames:
        frames[0].save(
            output_path,
            save_all=True,
            append_images=frames[1:],
            duration=gif.info.get('duration', 100),
            loop=gif.info.get('loop', 0)
        )
    
    return output_path

def generate_barcode(data, barcode_type='code128', output_path=None, **kwargs):
    """生成条形码
    Args:
        data: 条形码数据
        barcode_type: 条形码类型
        output_path: 输出路径
        **kwargs: 其他参数如宽度、高度等
    """
    # 条形码类型映射
    barcode_classes = {
        'code128': Code128,
        'code39': Code39,
        'ean13': EAN13,
        'ean8': EAN8,
        'upc': UPC,
    }
    
    if barcode_type.lower() not in barcode_classes:
        raise ValueError(f"不支持的条形码类型: {barcode_type}")
    
    barcode_class = barcode_classes[barcode_type.lower()]
    
    # 创建条形码
    try:
        code = barcode_class(str(data), writer=ImageWriter())
        
        # 设置选项
        options = {
            'module_width': kwargs.get('module_width', 0.2),
            'module_height': kwargs.get('module_height', 15),
            'font_size': kwargs.get('font_size', 10),
            'text_distance': kwargs.get('text_distance', 5),
            'background': kwargs.get('background', 'white'),
            'foreground': kwargs.get('foreground', 'black'),
        }
        
        if output_path:
            # 保存到文件
            code.save(output_path.rsplit('.', 1)[0], options=options)
            return output_path
        else:
            # 返回PIL Image对象
            buffer = io.BytesIO()
            code.write(buffer, options=options)
            buffer.seek(0)
            return Image.open(buffer)
            
    except Exception as e:
        raise ValueError(f"生成条形码失败: {str(e)}")

def create_image_collage(image_paths, output_path, layout='grid', spacing=10, background_color='white'):
    """创建图片拼贴
    Args:
        image_paths: 图片路径列表
        output_path: 输出路径
        layout: 布局方式 ('grid', 'horizontal', 'vertical')
        spacing: 图片间距
        background_color: 背景颜色
    """
    if not image_paths:
        raise ValueError("图片路径列表不能为空")
    
    # 加载图片
    images = []
    for path in image_paths:
        img = Image.open(path)
        images.append(img)
    
    if layout == 'horizontal':
        # 水平排列
        total_width = sum(img.width for img in images) + spacing * (len(images) - 1)
        max_height = max(img.height for img in images)
        
        collage = Image.new('RGB', (total_width, max_height), background_color)
        
        x_offset = 0
        for img in images:
            y_offset = (max_height - img.height) // 2  # 垂直居中
            collage.paste(img, (x_offset, y_offset))
            x_offset += img.width + spacing
    
    elif layout == 'vertical':
        # 垂直排列
        max_width = max(img.width for img in images)
        total_height = sum(img.height for img in images) + spacing * (len(images) - 1)
        
        collage = Image.new('RGB', (max_width, total_height), background_color)
        
        y_offset = 0
        for img in images:
            x_offset = (max_width - img.width) // 2  # 水平居中
            collage.paste(img, (x_offset, y_offset))
            y_offset += img.height + spacing
    
    else:  # grid
        # 网格排列
        import math
        cols = math.ceil(math.sqrt(len(images)))
        rows = math.ceil(len(images) / cols)
        
        # 计算每个网格的大小（使用最大图片尺寸）
        cell_width = max(img.width for img in images)
        cell_height = max(img.height for img in images)
        
        total_width = cell_width * cols + spacing * (cols - 1)
        total_height = cell_height * rows + spacing * (rows - 1)
        
        collage = Image.new('RGB', (total_width, total_height), background_color)
        
        for i, img in enumerate(images):
            row = i // cols
            col = i % cols
            
            x = col * (cell_width + spacing)
            y = row * (cell_height + spacing)
            
            # 在网格单元内居中
            x_offset = x + (cell_width - img.width) // 2
            y_offset = y + (cell_height - img.height) // 2
            
            collage.paste(img, (x_offset, y_offset))
    
    collage.save(output_path)
    return output_path

def create_thumbnail_gallery(image_directory, output_path, thumbnail_size=(150, 150), 
                           columns=5, spacing=10, background_color='white', show_filenames=True):
    """创建缩略图画廊
    Args:
        image_directory: 图片目录
        output_path: 输出路径
        thumbnail_size: 缩略图尺寸
        columns: 列数
        spacing: 间距
        background_color: 背景颜色
        show_filenames: 是否显示文件名
    """
    # 获取图片文件
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    image_files = []
    
    for file in os.listdir(image_directory):
        if Path(file).suffix.lower() in image_extensions:
            image_files.append(os.path.join(image_directory, file))
    
    if not image_files:
        raise ValueError("目录中没有找到图片文件")
    
    image_files.sort()  # 按文件名排序
    
    rows = (len(image_files) + columns - 1) // columns
    
    # 计算画布尺寸
    cell_width = thumbnail_size[0]
    cell_height = thumbnail_size[1]
    
    if show_filenames:
        cell_height += 30  # 为文件名预留空间
    
    canvas_width = cell_width * columns + spacing * (columns - 1)
    canvas_height = cell_height * rows + spacing * (rows - 1)
    
    # 创建画布
    gallery = Image.new('RGB', (canvas_width, canvas_height), background_color)
    draw = ImageDraw.Draw(gallery)
    
    # 尝试使用字体
    try:
        font = ImageFont.truetype("arial.ttf", 12)
    except:
        font = ImageFont.load_default()
    
    for i, image_path in enumerate(image_files):
        row = i // columns
        col = i % columns
        
        x = col * (cell_width + spacing)
        y = row * (cell_height + spacing)
        
        try:
            # 创建缩略图
            img = Image.open(image_path)
            img.thumbnail(thumbnail_size, Image.Resampling.LANCZOS)
            
            # 计算居中位置
            thumb_x = x + (cell_width - img.width) // 2
            thumb_y = y + (thumbnail_size[1] - img.height) // 2
            
            gallery.paste(img, (thumb_x, thumb_y))
            
            # 添加文件名
            if show_filenames:
                filename = Path(image_path).name
                if len(filename) > 20:
                    filename = filename[:17] + "..."
                
                text_bbox = draw.textbbox((0, 0), filename, font=font)
                text_width = text_bbox[2] - text_bbox[0]
                text_x = x + (cell_width - text_width) // 2
                text_y = y + thumbnail_size[1] + 5
                
                draw.text((text_x, text_y), filename, fill='black', font=font)
                
        except Exception as e:
            print(f"处理图片失败 {image_path}: {str(e)}")
            continue
    
    gallery.save(output_path)
    return output_path

def extract_frames_from_gif(gif_path, output_directory, frame_format='png'):
    """从GIF中提取帧
    Args:
        gif_path: GIF文件路径
        output_directory: 输出目录
        frame_format: 帧格式
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    gif = Image.open(gif_path)
    frame_count = 0
    extracted_files = []
    
    try:
        while True:
            frame = gif.copy()
            frame_filename = f"frame_{frame_count:04d}.{frame_format}"
            frame_path = os.path.join(output_directory, frame_filename)
            
            # 转换颜色模式
            if frame_format.lower() in ['jpg', 'jpeg'] and frame.mode != 'RGB':
                frame = frame.convert('RGB')
            elif frame_format.lower() == 'png' and frame.mode not in ['RGB', 'RGBA']:
                frame = frame.convert('RGBA')
            
            frame.save(frame_path)
            extracted_files.append(frame_path)
            
            frame_count += 1
            gif.seek(gif.tell() + 1)
    except EOFError:
        pass
    
    return extracted_files

def resize_image_batch(input_directory, output_directory, new_size, 
                      maintain_aspect=True, quality=95):
    """批量调整图片尺寸
    Args:
        input_directory: 输入目录
        output_directory: 输出目录
        new_size: 新尺寸 (width, height)
        maintain_aspect: 是否保持宽高比
        quality: JPEG质量
    """
    if not os.path.exists(output_directory):
        os.makedirs(output_directory)
    
    image_extensions = {'.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp'}
    processed_files = []
    
    for filename in os.listdir(input_directory):
        if Path(filename).suffix.lower() not in image_extensions:
            continue
        
        input_path = os.path.join(input_directory, filename)
        output_path = os.path.join(output_directory, filename)
        
        try:
            img = Image.open(input_path)
            
            if maintain_aspect:
                img.thumbnail(new_size, Image.Resampling.LANCZOS)
            else:
                img = img.resize(new_size, Image.Resampling.LANCZOS)
            
            # 保存参数
            save_kwargs = {}
            if Path(filename).suffix.lower() in ['.jpg', '.jpeg']:
                save_kwargs['quality'] = quality
                save_kwargs['optimize'] = True
            
            img.save(output_path, **save_kwargs)
            processed_files.append(output_path)
            
        except Exception as e:
            print(f"处理图片失败 {filename}: {str(e)}")
            continue
    
    return processed_files

def create_image_watermark(image_path, watermark_text, output_path=None, 
                         position='bottom-right', opacity=128, font_size=36):
    """给图片添加文字水印
    Args:
        image_path: 图片路径
        watermark_text: 水印文字
        output_path: 输出路径
        position: 水印位置
        opacity: 透明度 (0-255)
        font_size: 字体大小
    """
    img = Image.open(image_path).convert('RGBA')
    
    # 创建水印图层
    watermark = Image.new('RGBA', img.size, (255, 255, 255, 0))
    draw = ImageDraw.Draw(watermark)
    
    # 尝试加载字体
    try:
        font = ImageFont.truetype("arial.ttf", font_size)
    except:
        font = ImageFont.load_default()
    
    # 获取文字尺寸
    text_bbox = draw.textbbox((0, 0), watermark_text, font=font)
    text_width = text_bbox[2] - text_bbox[0]
    text_height = text_bbox[3] - text_bbox[1]
    
    # 计算位置
    margin = 20
    if position == 'top-left':
        x, y = margin, margin
    elif position == 'top-right':
        x, y = img.width - text_width - margin, margin
    elif position == 'bottom-left':
        x, y = margin, img.height - text_height - margin
    elif position == 'bottom-right':
        x, y = img.width - text_width - margin, img.height - text_height - margin
    elif position == 'center':
        x, y = (img.width - text_width) // 2, (img.height - text_height) // 2
    else:
        x, y = margin, img.height - text_height - margin  # 默认左下角
    
    # 绘制水印
    draw.text((x, y), watermark_text, font=font, fill=(255, 255, 255, opacity))
    
    # 合并图层
    watermarked = Image.alpha_composite(img, watermark)
    
    if output_path:
        # 转换回RGB模式保存
        if watermarked.mode == 'RGBA':
            watermarked = watermarked.convert('RGB')
        watermarked.save(output_path)
        return output_path
    else:
        return watermarked