import codecs
import re
import os
from collections import Counter

def convert_encoding(input_text, source_encoding, target_encoding):
    """文本编码转换"""
    try:
        # 如果输入是字符串，先用源编码编码为bytes
        if isinstance(input_text, str):
            encoded_bytes = input_text.encode(source_encoding)
        else:
            encoded_bytes = input_text
        
        # 解码为字符串，然后用目标编码重新编码
        decoded_text = encoded_bytes.decode(source_encoding)
        return decoded_text, None
    except Exception as e:
        return None, str(e)

def batch_find_replace(text, find_replace_pairs, use_regex=False, case_sensitive=True):
    """批量查找替换"""
    try:
        result_text = text
        flags = 0 if case_sensitive else re.IGNORECASE
        
        for find_str, replace_str in find_replace_pairs:
            if not find_str:  # 空字符串跳过
                continue
                
            if use_regex:
                result_text = re.sub(find_str, replace_str, result_text, flags=flags)
            else:
                if case_sensitive:
                    result_text = result_text.replace(find_str, replace_str)
                else:
                    # 大小写不敏感的普通替换
                    pattern = re.escape(find_str)
                    result_text = re.sub(pattern, replace_str, result_text, flags=re.IGNORECASE)
        
        return result_text, None
    except re.error as e:
        return None, f"正则表达式错误: {e}"
    except Exception as e:
        return None, str(e)

def split_text(text, split_method, split_value):
    """文本分割"""
    try:
        if split_method == "lines":
            lines_per_chunk = int(split_value)
            if lines_per_chunk <= 0:
                return None, "每份行数必须大于0"
            lines = text.split('\n')
            chunks = []
            for i in range(0, len(lines), lines_per_chunk):
                chunk_lines = lines[i:i + lines_per_chunk]
                chunks.append('\n'.join(chunk_lines))
            return chunks, None
            
        elif split_method == "chars":
            chars_per_chunk = int(split_value)
            if chars_per_chunk <= 0:
                return None, "每份字符数必须大于0"
            chunks = []
            for i in range(0, len(text), chars_per_chunk):
                chunks.append(text[i:i + chars_per_chunk])
            return chunks, None
            
        elif split_method == "delimiter":
            delimiter = split_value
            if not delimiter:
                return None, "分隔符不能为空"
            chunks = text.split(delimiter)
            return chunks, None
            
        else:
            return None, "不支持的分割方法"
    except ValueError:
        return None, "分割值必须为整数"
    except Exception as e:
        return None, str(e)

def merge_texts(text_list, separator="\n"):
    """文本合并"""
    try:
        return separator.join(text_list), None
    except Exception as e:
        return None, str(e)

def clean_text(
    text,
    remove_empty_lines=False,
    strip_whitespace=False,
    collapse_spaces=False,
    dedupe_lines=False,
    ignore_case=False,
    sort_lines=None,
):
    """文本清洗"""
    try:
        if not any(
            [
                remove_empty_lines,
                strip_whitespace,
                collapse_spaces,
                dedupe_lines,
                sort_lines,
            ]
        ):
            return None, "请至少选择一项清洗规则"

        lines = text.splitlines()
        processed_lines = []
        seen = set()

        for line in lines:
            current_line = line
            if strip_whitespace:
                current_line = current_line.strip()
            if collapse_spaces:
                current_line = re.sub(r"\s+", " ", current_line).strip()

            if remove_empty_lines and not current_line.strip():
                continue

            if dedupe_lines:
                key = current_line.lower() if ignore_case else current_line
                if key in seen:
                    continue
                seen.add(key)

            processed_lines.append(current_line)

        if sort_lines:
            reverse = sort_lines == "desc"
            processed_lines = sorted(processed_lines, reverse=reverse)

        return "\n".join(processed_lines), None
    except Exception as e:
        return None, str(e)

def analyze_text(text):
    """文本统计分析"""
    try:
        # 基本统计
        char_count = len(text)
        char_count_no_spaces = len(text.replace(' ', '').replace('\t', '').replace('\n', ''))
        word_count = len(text.split())
        line_count = text.count('\n') + 1 if text else 0
        paragraph_count = len([p for p in text.split('\n\n') if p.strip()])
        
        # 字符频率统计
        char_frequency = Counter(text)
        most_common_chars = char_frequency.most_common(10)
        
        # 单词频率统计  
        words = re.findall(r'\b\w+\b', text.lower())
        word_frequency = Counter(words)
        most_common_words = word_frequency.most_common(10)
        
        # 句子统计
        sentences = re.split(r'[.!?]+', text)
        sentence_count = len([s for s in sentences if s.strip()])
        
        analysis_result = {
            "char_count": char_count,
            "char_count_no_spaces": char_count_no_spaces,
            "word_count": word_count,
            "line_count": line_count,
            "paragraph_count": paragraph_count,
            "sentence_count": sentence_count,
            "most_common_chars": most_common_chars,
            "most_common_words": most_common_words,
            "avg_words_per_sentence": round(word_count / sentence_count, 2) if sentence_count > 0 else 0,
            "avg_chars_per_word": round(char_count / word_count, 2) if word_count > 0 else 0
        }
        
        return analysis_result, None
        
    except Exception as e:
        return None, str(e)

def process_text_file(file_path, operation, **kwargs):
    """处理文本文件"""
    try:
        if not os.path.exists(file_path):
            return None, f"未找到文件: {file_path}"
        if not os.path.isfile(file_path):
            return None, f"路径不是文件: {file_path}"

        # 检测文件编码
        source_encoding = kwargs.get("source_encoding")
        encoding = source_encoding or detect_file_encoding(file_path)

        try:
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
        except UnicodeDecodeError as e:
            return None, f"读取文件失败，可能是编码不匹配: {e}"
        
        if operation == "convert_encoding":
            result, error = convert_encoding(content, encoding, kwargs['target_encoding'])
            if error:
                return None, error
            
            # 保存转换后的文件
            output_path = kwargs.get('output_path', file_path.replace('.txt', f'_{kwargs["target_encoding"]}.txt'))
            with open(output_path, 'w', encoding=kwargs['target_encoding']) as f:
                f.write(result)
            return output_path, None
            
        elif operation == "find_replace":
            result, error = batch_find_replace(
                content, 
                kwargs['find_replace_pairs'],
                kwargs.get('use_regex', False),
                kwargs.get('case_sensitive', True)
            )
            if error:
                return None, error
                
            # 保存替换后的文件
            output_path = kwargs.get('output_path', file_path.replace('.txt', '_replaced.txt'))
            with open(output_path, 'w', encoding=encoding) as f:
                f.write(result)
            return output_path, None
            
        elif operation == "split":
            chunks, error = split_text(content, kwargs['split_method'], kwargs['split_value'])
            if error:
                return None, error
                
            # 保存分割后的文件
            base_name = os.path.splitext(file_path)[0]
            output_files = []
            for i, chunk in enumerate(chunks, 1):
                output_path = f"{base_name}_part{i}.txt"
                with open(output_path, 'w', encoding=encoding) as f:
                    f.write(chunk)
                output_files.append(output_path)
            return output_files, None
            
        elif operation == "clean":
            result, error = clean_text(
                content,
                remove_empty_lines=kwargs.get("remove_empty_lines", False),
                strip_whitespace=kwargs.get("strip_whitespace", False),
                collapse_spaces=kwargs.get("collapse_spaces", False),
                dedupe_lines=kwargs.get("dedupe_lines", False),
                ignore_case=kwargs.get("ignore_case", False),
                sort_lines=kwargs.get("sort_lines"),
            )
            if error:
                return None, error

            output_path = kwargs.get(
                "output_path", file_path.replace('.txt', '_cleaned.txt')
            )
            with open(output_path, 'w', encoding=encoding) as f:
                f.write(result)
            return output_path, None

        elif operation == "analyze":
            result, error = analyze_text(content)
            return result, error
            
        else:
            return None, "不支持的操作"
            
    except Exception as e:
        return None, str(e)

def detect_file_encoding(file_path):
    """检测文件编码"""
    try:
        with open(file_path, 'rb') as f:
            raw_data = f.read(10000)  # 读取前10KB用于检测
        
        # 尝试常见编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-16', 'ascii']
        
        for encoding in encodings:
            try:
                raw_data.decode(encoding)
                return encoding
            except UnicodeDecodeError:
                continue
        
        # 如果都失败了，返回utf-8作为默认值
        return 'utf-8'
        
    except Exception:
        return 'utf-8'

def merge_text_files(file_paths, output_path, separator="\n"):
    """合并多个文本文件"""
    try:
        if not file_paths:
            return None, "请至少选择一个文件进行合并"
        merged_content = []
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                return None, f"未找到文件: {file_path}"
            if not os.path.isfile(file_path):
                return None, f"路径不是文件: {file_path}"
            encoding = detect_file_encoding(file_path)
            with open(file_path, 'r', encoding=encoding) as f:
                content = f.read()
                merged_content.append(content)
        
        result = merge_texts(merged_content, separator)
        if result[1]:  # 如果有错误
            return None, result[1]
            
        # 保存合并后的文件
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write(result[0])
            
        return output_path, None
        
    except Exception as e:
        return None, str(e)
