import json
import xml.etree.ElementTree as ET
import xml.dom.minidom
import re
import urllib.parse
import base64
import html
from typing import Dict, Any

def format_json(json_text: str, indent: int = 4) -> str:
    """格式化JSON"""
    try:
        parsed = json.loads(json_text)
        return json.dumps(parsed, indent=indent, ensure_ascii=False)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON格式错误: {str(e)}")

def minify_json(json_text: str) -> str:
    """压缩JSON"""
    try:
        parsed = json.loads(json_text)
        return json.dumps(parsed, separators=(',', ':'), ensure_ascii=False)
    except json.JSONDecodeError as e:
        raise ValueError(f"JSON格式错误: {str(e)}")

def validate_json(json_text: str) -> tuple[bool, str]:
    """验证JSON格式"""
    try:
        json.loads(json_text)
        return True, "JSON格式正确"
    except json.JSONDecodeError as e:
        return False, f"JSON格式错误: {str(e)}"

def format_xml(xml_text: str) -> str:
    """格式化XML"""
    try:
        root = ET.fromstring(xml_text)
        rough_string = ET.tostring(root, 'utf-8')
        reparsed = xml.dom.minidom.parseString(rough_string)
        return reparsed.toprettyxml(indent="  ")
    except ET.ParseError as e:
        raise ValueError(f"XML格式错误: {str(e)}")

def minify_xml(xml_text: str) -> str:
    """压缩XML"""
    try:
        root = ET.fromstring(xml_text)
        return ET.tostring(root, encoding='unicode')
    except ET.ParseError as e:
        raise ValueError(f"XML格式错误: {str(e)}")

def validate_xml(xml_text: str) -> tuple[bool, str]:
    """验证XML格式"""
    try:
        ET.fromstring(xml_text)
        return True, "XML格式正确"
    except ET.ParseError as e:
        return False, f"XML格式错误: {str(e)}"

def url_encode(text: str) -> str:
    """URL编码"""
    return urllib.parse.quote(text, safe='')

def url_decode(text: str) -> str:
    """URL解码"""
    try:
        return urllib.parse.unquote(text)
    except Exception as e:
        raise ValueError(f"URL解码错误: {str(e)}")

def base64_encode(text: str) -> str:
    """Base64编码"""
    try:
        return base64.b64encode(text.encode('utf-8')).decode('ascii')
    except Exception as e:
        raise ValueError(f"Base64编码错误: {str(e)}")

def base64_decode(text: str) -> str:
    """Base64解码"""
    try:
        return base64.b64decode(text).decode('utf-8')
    except Exception as e:
        raise ValueError(f"Base64解码错误: {str(e)}")

def html_encode(text: str) -> str:
    """HTML编码"""
    return html.escape(text)

def html_decode(text: str) -> str:
    """HTML解码"""
    return html.unescape(text)

def test_regex(pattern: str, text: str, flags: int = 0) -> Dict[str, Any]:
    """测试正则表达式"""
    try:
        compiled_pattern = re.compile(pattern, flags)
        matches = compiled_pattern.findall(text)
        match_objects = list(compiled_pattern.finditer(text))
        
        result = {
            "matches": matches,
            "match_count": len(matches),
            "match_details": []
        }
        
        for match in match_objects:
            result["match_details"].append({
                "match": match.group(),
                "start": match.start(),
                "end": match.end(),
                "groups": match.groups()
            })
        
        return result
    except re.error as e:
        raise ValueError(f"正则表达式错误: {str(e)}")

def regex_replace(pattern: str, replacement: str, text: str, flags: int = 0) -> str:
    """正则表达式替换"""
    try:
        compiled_pattern = re.compile(pattern, flags)
        return compiled_pattern.sub(replacement, text)
    except re.error as e:
        raise ValueError(f"正则表达式错误: {str(e)}")

def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    """十六进制颜色转RGB"""
    hex_color = hex_color.lstrip('#')
    if len(hex_color) != 6:
        raise ValueError("十六进制颜色格式错误，应为 #RRGGBB")
    
    try:
        return tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
    except ValueError:
        raise ValueError("十六进制颜色格式错误")

def rgb_to_hex(r: int, g: int, b: int) -> str:
    """RGB转十六进制颜色"""
    if not all(0 <= x <= 255 for x in [r, g, b]):
        raise ValueError("RGB值必须在0-255之间")
    
    return f"#{r:02x}{g:02x}{b:02x}".upper()

def rgb_to_hsl(r: int, g: int, b: int) -> tuple[int, int, int]:
    """RGB转HSL"""
    r, g, b = r/255.0, g/255.0, b/255.0
    max_val = max(r, g, b)
    min_val = min(r, g, b)
    h, s, l = 0, 0, (max_val + min_val) / 2

    if max_val == min_val:
        h = s = 0  # achromatic
    else:
        d = max_val - min_val
        s = d / (2 - max_val - min_val) if l > 0.5 else d / (max_val + min_val)
        if max_val == r:
            h = (g - b) / d + (6 if g < b else 0)
        elif max_val == g:
            h = (b - r) / d + 2
        elif max_val == b:
            h = (r - g) / d + 4
        h /= 6

    return int(h * 360), int(s * 100), int(l * 100)

def hsl_to_rgb(h: int, s: int, l: int) -> tuple[int, int, int]:
    """HSL转RGB"""
    h, s, l = h/360.0, s/100.0, l/100.0
    
    def hue_to_rgb(p, q, t):
        if t < 0: t += 1
        if t > 1: t -= 1
        if t < 1/6: return p + (q - p) * 6 * t
        if t < 1/2: return q
        if t < 2/3: return p + (q - p) * (2/3 - t) * 6
        return p
    
    if s == 0:
        r = g = b = l  # achromatic
    else:
        q = l * (1 + s) if l < 0.5 else l + s - l * s
        p = 2 * l - q
        r = hue_to_rgb(p, q, h + 1/3)
        g = hue_to_rgb(p, q, h)
        b = hue_to_rgb(p, q, h - 1/3)
    
    return int(r * 255), int(g * 255), int(b * 255)

def generate_color_palette(base_color: str, count: int = 5) -> list[str]:
    """生成调色板"""
    try:
        r, g, b = hex_to_rgb(base_color)
        h, s, l = rgb_to_hsl(r, g, b)
        
        palette = []
        for i in range(count):
            # 调整亮度生成不同色调
            new_l = max(10, min(90, l + (i - count//2) * 15))
            new_r, new_g, new_b = hsl_to_rgb(h, s, new_l)
            palette.append(rgb_to_hex(new_r, new_g, new_b))
        
        return palette
    except Exception as e:
        raise ValueError(f"生成调色板失败: {str(e)}")

def format_css(css_text: str) -> str:
    """简单的CSS格式化"""
    # 简单的CSS格式化，添加缩进和换行
    formatted = css_text.replace('{', ' {\n    ')
    formatted = formatted.replace('}', '\n}\n')
    formatted = formatted.replace(';', ';\n    ')
    # 清理多余的空白
    formatted = re.sub(r'\n\s*\n', '\n', formatted)
    formatted = re.sub(r'\n    \}', '\n}', formatted)
    return formatted.strip()

def minify_css(css_text: str) -> str:
    """压缩CSS"""
    # 移除注释
    css_text = re.sub(r'/\*.*?\*/', '', css_text, flags=re.DOTALL)
    # 移除多余空白
    css_text = re.sub(r'\s+', ' ', css_text)
    # 移除不必要的空格
    css_text = re.sub(r';\s*', ';', css_text)
    css_text = re.sub(r'{\s*', '{', css_text)
    css_text = re.sub(r'\s*}', '}', css_text)
    css_text = re.sub(r':\s*', ':', css_text)
    return css_text.strip()