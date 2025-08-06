import os
import hashlib
import secrets
import string
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend
import base64

def generate_key_from_password(password: str, salt: bytes) -> bytes:
    """从密码生成加密密钥"""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key

def encrypt_file(file_path: str, password: str, output_path: str = None):
    """加密文件"""
    if not output_path:
        output_path = file_path + '.encrypted'
    
    # 生成随机盐
    salt = os.urandom(16)
    key = generate_key_from_password(password, salt)
    f = Fernet(key)
    
    with open(file_path, 'rb') as file:
        file_data = file.read()
    
    encrypted_data = f.encrypt(file_data)
    
    # 将盐和加密数据一起保存
    with open(output_path, 'wb') as file:
        file.write(salt + encrypted_data)
    
    return output_path

def decrypt_file(file_path: str, password: str, output_path: str = None):
    """解密文件"""
    if not output_path:
        output_path = file_path.replace('.encrypted', '')
        if output_path == file_path:
            output_path = file_path + '.decrypted'
    
    with open(file_path, 'rb') as file:
        file_data = file.read()
    
    # 提取盐和加密数据
    salt = file_data[:16]
    encrypted_data = file_data[16:]
    
    key = generate_key_from_password(password, salt)
    f = Fernet(key)
    
    try:
        decrypted_data = f.decrypt(encrypted_data)
        with open(output_path, 'wb') as file:
            file.write(decrypted_data)
        return output_path
    except:
        raise ValueError("解密失败，密码可能不正确")

def calculate_file_hash(file_path: str, algorithm: str = 'md5') -> str:
    """计算文件哈希值"""
    hash_algorithms = {
        'md5': hashlib.md5(),
        'sha1': hashlib.sha1(),
        'sha256': hashlib.sha256(),
        'sha512': hashlib.sha512()
    }
    
    if algorithm.lower() not in hash_algorithms:
        raise ValueError(f"不支持的哈希算法: {algorithm}")
    
    hash_obj = hash_algorithms[algorithm.lower()]
    
    with open(file_path, 'rb') as file:
        for chunk in iter(lambda: file.read(4096), b""):
            hash_obj.update(chunk)
    
    return hash_obj.hexdigest()

def calculate_text_hash(text: str, algorithm: str = 'md5') -> str:
    """计算文本哈希值"""
    hash_algorithms = {
        'md5': hashlib.md5(),
        'sha1': hashlib.sha1(),
        'sha256': hashlib.sha256(),
        'sha512': hashlib.sha512()
    }
    
    if algorithm.lower() not in hash_algorithms:
        raise ValueError(f"不支持的哈希算法: {algorithm}")
    
    hash_obj = hash_algorithms[algorithm.lower()]
    hash_obj.update(text.encode('utf-8'))
    return hash_obj.hexdigest()

def generate_password(length: int = 12, use_uppercase: bool = True, use_lowercase: bool = True, 
                     use_digits: bool = True, use_symbols: bool = True) -> str:
    """生成随机密码"""
    if length < 1:
        raise ValueError("密码长度必须大于0")
    
    characters = ""
    if use_uppercase:
        characters += string.ascii_uppercase
    if use_lowercase:
        characters += string.ascii_lowercase
    if use_digits:
        characters += string.digits
    if use_symbols:
        characters += "!@#$%^&*()_+-=[]{}|;:,.<>?"
    
    if not characters:
        raise ValueError("至少选择一种字符类型")
    
    password = ''.join(secrets.choice(characters) for _ in range(length))
    return password

def encrypt_text(text: str, password: str) -> str:
    """加密文本"""
    salt = os.urandom(16)
    key = generate_key_from_password(password, salt)
    f = Fernet(key)
    
    encrypted_data = f.encrypt(text.encode('utf-8'))
    # 返回base64编码的盐+加密数据
    return base64.b64encode(salt + encrypted_data).decode('utf-8')

def decrypt_text(encrypted_text: str, password: str) -> str:
    """解密文本"""
    try:
        # 解码base64
        data = base64.b64decode(encrypted_text.encode('utf-8'))
        
        # 提取盐和加密数据
        salt = data[:16]
        encrypted_data = data[16:]
        
        key = generate_key_from_password(password, salt)
        f = Fernet(key)
        
        decrypted_data = f.decrypt(encrypted_data)
        return decrypted_data.decode('utf-8')
    except:
        raise ValueError("解密失败，密码可能不正确或数据已损坏")