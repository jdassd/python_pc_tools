import os
import hashlib
import shutil
import re
import time
from collections import defaultdict

def find_duplicate_files(directory, include_subdirs=True):
    """查找重复文件"""
    try:
        file_hashes = defaultdict(list)
        
        if include_subdirs:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    file_path = os.path.join(root, file)
                    try:
                        file_hash = get_file_hash(file_path)
                        if file_hash:
                            file_hashes[file_hash].append(file_path)
                    except Exception:
                        continue
        else:
            for file in os.listdir(directory):
                file_path = os.path.join(directory, file)
                if os.path.isfile(file_path):
                    try:
                        file_hash = get_file_hash(file_path)
                        if file_hash:
                            file_hashes[file_hash].append(file_path)
                    except Exception:
                        continue
        
        # 只返回有重复的文件
        duplicates = {hash_val: paths for hash_val, paths in file_hashes.items() if len(paths) > 1}
        return duplicates, None
        
    except Exception as e:
        return None, str(e)

def get_file_hash(file_path, chunk_size=8192):
    """计算文件MD5哈希值"""
    try:
        hash_md5 = hashlib.md5()
        with open(file_path, "rb") as f:
            for chunk in iter(lambda: f.read(chunk_size), b""):
                hash_md5.update(chunk)
        return hash_md5.hexdigest()
    except Exception:
        return None

def batch_rename_files(directory, pattern, replacement, use_regex=False, include_extension=False):
    """批量重命名文件"""
    try:
        renamed_files = []
        errors = []
        
        for filename in os.listdir(directory):
            file_path = os.path.join(directory, filename)
            if not os.path.isfile(file_path):
                continue
            
            # 获取文件名和扩展名
            name, ext = os.path.splitext(filename)
            target_name = filename if include_extension else name
            
            # 执行重命名规则
            if use_regex:
                try:
                    new_name = re.sub(pattern, replacement, target_name)
                except re.error as e:
                    errors.append(f"{filename}: 正则表达式错误 - {str(e)}")
                    continue
            else:
                new_name = target_name.replace(pattern, replacement)
            
            # 如果不包含扩展名，需要重新加上
            if not include_extension:
                new_filename = new_name + ext
            else:
                new_filename = new_name
            
            # 检查是否有变化
            if new_filename == filename:
                continue
            
            new_file_path = os.path.join(directory, new_filename)
            
            # 检查目标文件是否已存在
            if os.path.exists(new_file_path):
                errors.append(f"{filename} -> {new_filename}: 目标文件已存在")
                continue
            
            try:
                os.rename(file_path, new_file_path)
                renamed_files.append((filename, new_filename))
            except Exception as e:
                errors.append(f"{filename} -> {new_filename}: {str(e)}")
        
        return renamed_files, errors
        
    except Exception as e:
        return None, [str(e)]

def compare_directories(dir1, dir2, compare_content=False):
    """比较两个目录"""
    try:
        comparison_result = {
            "only_in_dir1": [],
            "only_in_dir2": [],
            "common_files": [],
            "different_content": [],
            "same_content": []
        }
        
        # 获取所有文件
        files1 = set()
        files2 = set()
        
        for root, dirs, files in os.walk(dir1):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), dir1)
                files1.add(rel_path)
        
        for root, dirs, files in os.walk(dir2):
            for file in files:
                rel_path = os.path.relpath(os.path.join(root, file), dir2)
                files2.add(rel_path)
        
        # 分类文件
        comparison_result["only_in_dir1"] = list(files1 - files2)
        comparison_result["only_in_dir2"] = list(files2 - files1)
        comparison_result["common_files"] = list(files1 & files2)
        
        # 如果需要比较内容
        if compare_content:
            for file in comparison_result["common_files"]:
                file1_path = os.path.join(dir1, file)
                file2_path = os.path.join(dir2, file)
                
                try:
                    hash1 = get_file_hash(file1_path)
                    hash2 = get_file_hash(file2_path)
                    
                    if hash1 == hash2:
                        comparison_result["same_content"].append(file)
                    else:
                        comparison_result["different_content"].append(file)
                except Exception:
                    comparison_result["different_content"].append(file)  # 无法比较，归为不同
        
        return comparison_result, None
        
    except Exception as e:
        return None, str(e)

def find_empty_directories(root_directory, remove_empty=False):
    """查找空文件夹"""
    try:
        empty_dirs = []
        removed_dirs = []
        
        # 从底层开始遍历，这样可以正确处理嵌套的空目录
        for root, dirs, files in os.walk(root_directory, topdown=False):
            # 跳过根目录本身
            if root == root_directory:
                continue
            
            # 检查目录是否为空
            try:
                if not os.listdir(root):  # 目录为空
                    empty_dirs.append(root)
                    if remove_empty:
                        os.rmdir(root)
                        removed_dirs.append(root)
            except (OSError, PermissionError):
                continue
        
        if remove_empty:
            return {"empty_dirs": empty_dirs, "removed_dirs": removed_dirs}, None
        else:
            return {"empty_dirs": empty_dirs}, None
        
    except Exception as e:
        return None, str(e)

def clean_system_temp(dry_run=True):
    """清理系统临时文件"""
    try:
        cleaned_files = []
        cleaned_size = 0
        errors = []
        
        # Windows临时目录
        temp_dirs = []
        if os.name == 'nt':  # Windows
            temp_dirs = [
                os.environ.get('TEMP', ''),
                os.environ.get('TMP', ''),
                os.path.join(os.environ.get('LOCALAPPDATA', ''), 'Temp'),
            ]
        else:  # Unix/Linux/Mac
            temp_dirs = ['/tmp', '/var/tmp']
        
        for temp_dir in temp_dirs:
            if not temp_dir or not os.path.exists(temp_dir):
                continue
            
            try:
                for item in os.listdir(temp_dir):
                    item_path = os.path.join(temp_dir, item)
                    
                    # 跳过正在使用的文件
                    try:
                        if os.path.isfile(item_path):
                            # 检查文件是否超过1天未修改
                            if time.time() - os.path.getmtime(item_path) > 86400:
                                file_size = os.path.getsize(item_path)
                                if not dry_run:
                                    os.remove(item_path)
                                cleaned_files.append(item_path)
                                cleaned_size += file_size
                        elif os.path.isdir(item_path):
                            # 对于目录，递归删除（谨慎操作）
                            if not dry_run:
                                shutil.rmtree(item_path, ignore_errors=True)
                            cleaned_files.append(item_path)
                    except (OSError, PermissionError) as e:
                        errors.append(f"{item_path}: {str(e)}")
            except (OSError, PermissionError):
                continue
        
        return {
            "cleaned_files": cleaned_files,
            "cleaned_size": cleaned_size,
            "errors": errors,
            "dry_run": dry_run
        }, None
        
    except Exception as e:
        return None, str(e)

def generate_numbered_names(base_name, count, start_num=1, padding=3):
    """生成带序号的文件名列表"""
    try:
        names = []
        name, ext = os.path.splitext(base_name)
        
        for i in range(count):
            num = start_num + i
            padded_num = str(num).zfill(padding)
            new_name = f"{name}_{padded_num}{ext}"
            names.append(new_name)
        
        return names, None
        
    except Exception as e:
        return None, str(e)

def batch_rename_with_sequence(directory, base_name, start_num=1, padding=3):
    """批量重命名为有序序列"""
    try:
        files = [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]
        files.sort()  # 按名称排序
        
        renamed_files = []
        errors = []
        
        # 获取扩展名（使用第一个文件的扩展名，或者允许用户指定）
        if files:
            _, default_ext = os.path.splitext(files[0])
        else:
            default_ext = ""
        
        name_base, ext = os.path.splitext(base_name)
        if not ext:
            ext = default_ext
        
        for i, old_filename in enumerate(files):
            old_path = os.path.join(directory, old_filename)
            
            # 生成新文件名
            num = start_num + i
            padded_num = str(num).zfill(padding)
            new_filename = f"{name_base}_{padded_num}{ext}"
            new_path = os.path.join(directory, new_filename)
            
            # 检查目标文件是否已存在
            if os.path.exists(new_path):
                errors.append(f"{old_filename} -> {new_filename}: 目标文件已存在")
                continue
            
            try:
                os.rename(old_path, new_path)
                renamed_files.append((old_filename, new_filename))
            except Exception as e:
                errors.append(f"{old_filename} -> {new_filename}: {str(e)}")
        
        return renamed_files, errors
        
    except Exception as e:
        return None, [str(e)]

def get_directory_size(directory):
    """计算目录大小"""
    try:
        total_size = 0
        file_count = 0
        dir_count = 0
        
        for root, dirs, files in os.walk(directory):
            dir_count += len(dirs)
            for file in files:
                file_path = os.path.join(root, file)
                try:
                    file_size = os.path.getsize(file_path)
                    total_size += file_size
                    file_count += 1
                except (OSError, FileNotFoundError):
                    continue
        
        return {
            "total_size": total_size,
            "file_count": file_count,
            "dir_count": dir_count,
            "size_mb": round(total_size / (1024 * 1024), 2),
            "size_gb": round(total_size / (1024 * 1024 * 1024), 3)
        }, None
        
    except Exception as e:
        return None, str(e)

def format_file_size(size_bytes):
    """格式化文件大小显示"""
    if size_bytes < 1024:
        return f"{size_bytes} B"
    elif size_bytes < 1024 * 1024:
        return f"{size_bytes / 1024:.1f} KB"
    elif size_bytes < 1024 * 1024 * 1024:
        return f"{size_bytes / (1024 * 1024):.1f} MB"
    else:
        return f"{size_bytes / (1024 * 1024 * 1024):.2f} GB"