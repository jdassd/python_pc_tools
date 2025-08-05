from PIL import Image, ImageDraw, ImageFont

def convert_image_format(input_path, output_path, format):
    """Converts an image to a different format."""
    try:
        img = Image.open(input_path)
        img.save(output_path, format=format)
        return f"Successfully converted {input_path} to {output_path}"
    except Exception as e:
        return f"Error converting image: {e}"

def resize_image(input_path, output_path, size):
    """Resizes an image."""
    try:
        img = Image.open(input_path)
        resized_img = img.resize(size)
        resized_img.save(output_path)
        return f"Successfully resized {input_path} to {size}"
    except Exception as e:
        return f"Error resizing image: {e}"

def crop_image(input_path, output_path, box):
    """Crops an image."""
    try:
        img = Image.open(input_path)
        cropped_img = img.crop(box)
        cropped_img.save(output_path)
        return f"Successfully cropped {input_path}"
    except Exception as e:
        return f"Error cropping image: {e}"

def add_watermark(input_path, output_path, text, position, font_path=None, font_size=20, color=(255, 255, 255, 128)):
    """Adds a text watermark to an image."""
    try:
        img = Image.open(input_path).convert("RGBA")
        txt = Image.new("RGBA", img.size, (255, 255, 255, 0))

        try:
            font = ImageFont.truetype(font_path, font_size)
        except IOError:
            font = ImageFont.load_default()

        draw = ImageDraw.Draw(txt)
        draw.text(position, text, font=font, fill=color)

        watermarked_img = Image.alpha_composite(img, txt)
        watermarked_img.save(output_path)
        return f"Successfully added watermark to {input_path}"
    except Exception as e:
        return f"Error adding watermark: {e}"