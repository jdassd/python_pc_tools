import json
import os
import sys
from typing import Dict, Any

class DataManager:
    """数据持久化管理器，负责工具使用次数的存储和读取"""
    
    DATA_VERSION = "1.0"
    DATA_FILE = "data/usage_stats.json"
    
    # 默认工具配置
    DEFAULT_TOOLS = {
        "pdf_count": 0,
        "image_count": 0,
        "audio_count": 0,
        "video_count": 0,
        "mouse_count": 0,
        "text_count": 0,
        "system_count": 0,
        "network_count": 0,
        "crypto_count": 0,
        "dev_count": 0,
        "office_count": 0,
        "media_count": 0,
        "data_count": 0
    }
    
    def __init__(self):
        self.data_dir = self._get_data_dir()
        self.data_file_path = os.path.join(self.data_dir, "usage_stats.json")
        self._ensure_data_dir()
        self.data = self._load_data()
    
    def _get_data_dir(self) -> str:
        """获取data目录路径，位于exe同级目录"""
        if getattr(sys, 'frozen', False):
            # 打包后的exe环境
            return os.path.join(os.path.dirname(sys.executable), "data")
        else:
            # 开发环境
            return os.path.join(os.path.dirname(os.path.abspath(__file__)), "data")
    
    def _ensure_data_dir(self):
        """确保data目录存在"""
        os.makedirs(self.data_dir, exist_ok=True)
    
    def _load_data(self) -> Dict[str, Any]:
        """加载数据文件，处理版本兼容性"""
        if not os.path.exists(self.data_file_path):
            return self._create_default_data()
        
        try:
            with open(self.data_file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # 版本兼容性处理
            data = self._migrate_data(data)
            return data
            
        except (json.JSONDecodeError, IOError) as e:
            print(f"数据文件损坏，使用默认数据: {e}")
            return self._create_default_data()
    
    def _create_default_data(self) -> Dict[str, Any]:
        """创建默认数据结构"""
        return {
            "version": self.DATA_VERSION,
            "tools": self.DEFAULT_TOOLS.copy(),
            "metadata": {
                "created_at": self._get_current_timestamp(),
                "last_updated": self._get_current_timestamp()
            }
        }
    
    def _migrate_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """数据版本迁移处理"""
        # 如果没有版本信息，认为是旧版本
        if "version" not in data:
            data = self._migrate_from_legacy(data)
        
        # 确保所有默认工具都存在
        if "tools" not in data:
            data["tools"] = {}
        
        for tool_name, default_value in self.DEFAULT_TOOLS.items():
            if tool_name not in data["tools"]:
                data["tools"][tool_name] = default_value
        
        # 更新版本信息
        data["version"] = self.DATA_VERSION
        if "metadata" not in data:
            data["metadata"] = {}
        data["metadata"]["last_updated"] = self._get_current_timestamp()
        
        return data
    
    def _migrate_from_legacy(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """从旧版本数据格式迁移"""
        # 如果数据直接是计数器字典格式
        if all(isinstance(v, int) for v in data.values()):
            return {
                "version": self.DATA_VERSION,
                "tools": data,
                "metadata": {
                    "created_at": self._get_current_timestamp(),
                    "last_updated": self._get_current_timestamp(),
                    "migrated_from": "legacy"
                }
            }
        
        return data
    
    def _get_current_timestamp(self) -> str:
        """获取当前时间戳"""
        from datetime import datetime
        return datetime.now().isoformat()
    
    def get_tool_count(self, tool_name: str) -> int:
        """获取指定工具的使用次数"""
        return self.data.get("tools", {}).get(tool_name, 0)
    
    def increment_tool_count(self, tool_name: str) -> int:
        """增加指定工具的使用次数"""
        if "tools" not in self.data:
            self.data["tools"] = {}
        
        current_count = self.data["tools"].get(tool_name, 0)
        self.data["tools"][tool_name] = current_count + 1
        
        # 更新元数据
        if "metadata" not in self.data:
            self.data["metadata"] = {}
        self.data["metadata"]["last_updated"] = self._get_current_timestamp()
        
        self._save_data()
        return self.data["tools"][tool_name]
    
    def set_tool_count(self, tool_name: str, count: int):
        """设置指定工具的使用次数"""
        if "tools" not in self.data:
            self.data["tools"] = {}
        
        self.data["tools"][tool_name] = max(0, count)  # 确保不为负数
        
        # 更新元数据
        if "metadata" not in self.data:
            self.data["metadata"] = {}
        self.data["metadata"]["last_updated"] = self._get_current_timestamp()
        
        self._save_data()
    
    def get_all_counts(self) -> Dict[str, int]:
        """获取所有工具的使用次数"""
        return self.data.get("tools", {}).copy()
    
    def _save_data(self):
        """保存数据到文件"""
        try:
            with open(self.data_file_path, 'w', encoding='utf-8') as f:
                json.dump(self.data, f, ensure_ascii=False, indent=2)
        except IOError as e:
            print(f"保存数据失败: {e}")
    
    def reset_all_counts(self):
        """重置所有工具使用次数"""
        self.data["tools"] = self.DEFAULT_TOOLS.copy()
        if "metadata" not in self.data:
            self.data["metadata"] = {}
        self.data["metadata"]["last_updated"] = self._get_current_timestamp()
        self.data["metadata"]["reset_at"] = self._get_current_timestamp()
        self._save_data()
    
    def get_metadata(self) -> Dict[str, Any]:
        """获取数据元信息"""
        return self.data.get("metadata", {})