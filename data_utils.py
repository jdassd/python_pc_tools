import os
import pandas as pd
import numpy as np
import json
from datetime import datetime, timedelta
import re
from collections import Counter, defaultdict
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import csv
import sqlite3
import tempfile

# 设置中文字体支持
plt.rcParams['font.sans-serif'] = ['SimHei', 'DejaVu Sans']
plt.rcParams['axes.unicode_minus'] = False

def analyze_csv_file(file_path, sample_rows=1000):
    """分析CSV文件"""
    try:
        # 尝试自动检测编码
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
        df = None
        used_encoding = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding, nrows=sample_rows)
                used_encoding = encoding
                break
            except:
                continue
        
        if df is None:
            raise ValueError("无法读取CSV文件，请检查文件编码")
        
        analysis = {
            'basic_info': {
                'rows': len(df),
                'columns': len(df.columns),
                'encoding': used_encoding,
                'memory_usage': df.memory_usage(deep=True).sum(),
                'file_size': os.path.getsize(file_path)
            },
            'columns_info': {},
            'missing_data': {},
            'data_types': {}
        }
        
        # 分析每列
        for col in df.columns:
            col_data = df[col]
            
            # 基本信息
            analysis['columns_info'][col] = {
                'dtype': str(col_data.dtype),
                'non_null_count': col_data.count(),
                'null_count': col_data.isnull().sum(),
                'unique_count': col_data.nunique(),
                'memory_usage': col_data.memory_usage(deep=True)
            }
            
            # 缺失数据
            missing_ratio = col_data.isnull().sum() / len(col_data) * 100
            analysis['missing_data'][col] = {
                'count': col_data.isnull().sum(),
                'ratio': missing_ratio
            }
            
            # 数据类型检测
            if col_data.dtype in ['int64', 'float64']:
                analysis['data_types'][col] = 'numeric'
                analysis['columns_info'][col].update({
                    'min': col_data.min(),
                    'max': col_data.max(),
                    'mean': col_data.mean(),
                    'std': col_data.std(),
                    'median': col_data.median()
                })
            elif col_data.dtype == 'object':
                # 尝试检测日期
                if is_date_column(col_data):
                    analysis['data_types'][col] = 'datetime'
                else:
                    analysis['data_types'][col] = 'text'
                    
                # 文本统计
                str_lengths = col_data.astype(str).str.len()
                analysis['columns_info'][col].update({
                    'avg_length': str_lengths.mean(),
                    'max_length': str_lengths.max(),
                    'min_length': str_lengths.min()
                })
            else:
                analysis['data_types'][col] = 'other'
        
        return analysis
        
    except Exception as e:
        raise ValueError(f"分析CSV文件失败: {str(e)}")

def is_date_column(series, sample_size=100):
    """检测列是否为日期类型"""
    sample = series.dropna().head(sample_size)
    if len(sample) == 0:
        return False
    
    date_patterns = [
        r'\d{4}-\d{2}-\d{2}',  # YYYY-MM-DD
        r'\d{2}/\d{2}/\d{4}',  # MM/DD/YYYY
        r'\d{4}/\d{2}/\d{2}',  # YYYY/MM/DD
        r'\d{2}-\d{2}-\d{4}',  # MM-DD-YYYY
    ]
    
    match_count = 0
    for value in sample:
        str_value = str(value)
        for pattern in date_patterns:
            if re.match(pattern, str_value):
                match_count += 1
                break
    
    return match_count / len(sample) > 0.7

def clean_csv_data(input_path, output_path, operations):
    """清理CSV数据"""
    try:
        # 读取数据
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(input_path, encoding=encoding)
                break
            except:
                continue
        
        if df is None:
            raise ValueError("无法读取CSV文件")
        
        original_shape = df.shape
        
        for operation in operations:
            if operation == 'remove_duplicates':
                df = df.drop_duplicates()
            
            elif operation == 'remove_empty_rows':
                df = df.dropna(how='all')
            
            elif operation == 'remove_empty_columns':
                df = df.dropna(axis=1, how='all')
            
            elif operation == 'fill_missing_mean':
                numeric_columns = df.select_dtypes(include=[np.number]).columns
                df[numeric_columns] = df[numeric_columns].fillna(df[numeric_columns].mean())
            
            elif operation == 'fill_missing_mode':
                for col in df.columns:
                    if df[col].dtype == 'object':
                        mode_value = df[col].mode()
                        if len(mode_value) > 0:
                            df[col] = df[col].fillna(mode_value[0])
            
            elif operation == 'standardize_text':
                text_columns = df.select_dtypes(include=['object']).columns
                for col in text_columns:
                    df[col] = df[col].astype(str).str.strip().str.title()
            
            elif operation == 'convert_dates':
                for col in df.columns:
                    if df[col].dtype == 'object' and is_date_column(df[col]):
                        df[col] = pd.to_datetime(df[col], errors='coerce')
        
        # 保存清理后的数据
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        return {
            'original_shape': original_shape,
            'cleaned_shape': df.shape,
            'removed_rows': original_shape[0] - df.shape[0],
            'removed_columns': original_shape[1] - df.shape[1]
        }
        
    except Exception as e:
        raise ValueError(f"清理数据失败: {str(e)}")

def generate_data_report(file_path, output_dir):
    """生成数据分析报告"""
    try:
        # 分析数据
        analysis = analyze_csv_file(file_path)
        
        # 读取数据用于可视化
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(file_path, encoding=encoding, nrows=10000)  # 限制行数以提高性能
                break
            except:
                continue
        
        if df is None:
            raise ValueError("无法读取CSV文件")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        # 生成HTML报告
        report_path = os.path.join(output_dir, "data_report.html")
        generate_html_report(analysis, df, report_path)
        
        # 生成图表
        charts_created = generate_data_charts(df, output_dir)
        
        return {
            'report_path': report_path,
            'charts_created': charts_created,
            'analysis': analysis
        }
        
    except Exception as e:
        raise ValueError(f"生成报告失败: {str(e)}")

def generate_html_report(analysis, df, output_path):
    """生成HTML数据报告"""
    html_content = f"""
    <!DOCTYPE html>
    <html lang="zh-CN">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>数据分析报告</title>
        <style>
            body {{ font-family: Arial, sans-serif; margin: 20px; }}
            .header {{ background-color: #f0f0f0; padding: 20px; border-radius: 5px; }}
            .section {{ margin: 20px 0; }}
            table {{ border-collapse: collapse; width: 100%; }}
            th, td {{ border: 1px solid #ddd; padding: 8px; text-align: left; }}
            th {{ background-color: #f2f2f2; }}
            .chart {{ text-align: center; margin: 20px 0; }}
            .missing-high {{ background-color: #ffebee; }}
            .missing-medium {{ background-color: #fff3e0; }}
            .missing-low {{ background-color: #e8f5e8; }}
        </style>
    </head>
    <body>
        <div class="header">
            <h1>数据分析报告</h1>
            <p>生成时间: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        </div>
        
        <div class="section">
            <h2>基本信息</h2>
            <table>
                <tr><th>项目</th><th>值</th></tr>
                <tr><td>行数</td><td>{analysis['basic_info']['rows']:,}</td></tr>
                <tr><td>列数</td><td>{analysis['basic_info']['columns']}</td></tr>
                <tr><td>文件大小</td><td>{analysis['basic_info']['file_size'] / 1024 / 1024:.2f} MB</td></tr>
                <tr><td>内存使用</td><td>{analysis['basic_info']['memory_usage'] / 1024 / 1024:.2f} MB</td></tr>
                <tr><td>编码格式</td><td>{analysis['basic_info']['encoding']}</td></tr>
            </table>
        </div>
        
        <div class="section">
            <h2>列信息</h2>
            <table>
                <tr>
                    <th>列名</th><th>数据类型</th><th>非空值</th><th>空值</th>
                    <th>缺失率</th><th>唯一值</th><th>内存使用</th>
                </tr>
    """
    
    for col, info in analysis['columns_info'].items():
        missing_ratio = analysis['missing_data'][col]['ratio']
        if missing_ratio > 50:
            row_class = 'missing-high'
        elif missing_ratio > 20:
            row_class = 'missing-medium'
        else:
            row_class = 'missing-low'
            
        html_content += f"""
                <tr class="{row_class}">
                    <td>{col}</td>
                    <td>{info['dtype']}</td>
                    <td>{info['non_null_count']:,}</td>
                    <td>{info['null_count']:,}</td>
                    <td>{missing_ratio:.1f}%</td>
                    <td>{info['unique_count']:,}</td>
                    <td>{info['memory_usage'] / 1024:.1f} KB</td>
                </tr>
        """
    
    html_content += """
            </table>
        </div>
        
        <div class="section">
            <h2>数值列统计</h2>
            <table>
                <tr><th>列名</th><th>最小值</th><th>最大值</th><th>平均值</th><th>标准差</th><th>中位数</th></tr>
    """
    
    numeric_columns = df.select_dtypes(include=[np.number]).columns
    for col in numeric_columns:
        if col in analysis['columns_info']:
            info = analysis['columns_info'][col]
            if 'min' in info:
                html_content += f"""
                <tr>
                    <td>{col}</td>
                    <td>{info.get('min', 'N/A')}</td>
                    <td>{info.get('max', 'N/A')}</td>
                    <td>{info.get('mean', 0):.2f}</td>
                    <td>{info.get('std', 0):.2f}</td>
                    <td>{info.get('median', 'N/A')}</td>
                </tr>
                """
    
    html_content += """
            </table>
        </div>
        
        <div class="section">
            <h2>数据质量总结</h2>
            <ul>
    """
    
    # 添加数据质量总结
    total_missing = sum(info['ratio'] for info in analysis['missing_data'].values())
    avg_missing = total_missing / len(analysis['missing_data']) if analysis['missing_data'] else 0
    
    high_missing_cols = [col for col, info in analysis['missing_data'].items() if info['ratio'] > 50]
    duplicate_potential = len(df) - len(df.drop_duplicates()) if len(df) <= 10000 else "未计算(数据量过大)"
    
    html_content += f"""
                <li>平均缺失率: {avg_missing:.1f}%</li>
                <li>高缺失率列数 (>50%): {len(high_missing_cols)}</li>
                <li>可能重复行数: {duplicate_potential}</li>
                <li>数值列数: {len(numeric_columns)}</li>
                <li>文本列数: {len(df.select_dtypes(include=['object']).columns)}</li>
            </ul>
        </div>
    </body>
    </html>
    """
    
    with open(output_path, 'w', encoding='utf-8') as f:
        f.write(html_content)

def generate_data_charts(df, output_dir):
    """生成数据图表"""
    charts_created = []
    
    try:
        # 1. 缺失值热图
        missing_data = df.isnull()
        if missing_data.sum().sum() > 0:
            plt.figure(figsize=(12, 8))
            sns.heatmap(missing_data, yticklabels=False, cmap='viridis', cbar_kws={'label': '缺失值'})
            plt.title('缺失值分布热图')
            plt.xticks(rotation=45)
            plt.tight_layout()
            chart_path = os.path.join(output_dir, "missing_values_heatmap.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            charts_created.append(chart_path)
        
        # 2. 数值列分布直方图
        numeric_columns = df.select_dtypes(include=[np.number]).columns
        if len(numeric_columns) > 0:
            n_cols = min(3, len(numeric_columns))
            n_rows = (len(numeric_columns) + n_cols - 1) // n_cols
            
            plt.figure(figsize=(15, 5 * n_rows))
            for i, col in enumerate(numeric_columns[:9], 1):  # 最多9个图
                plt.subplot(n_rows, n_cols, i)
                df[col].hist(bins=50, alpha=0.7)
                plt.title(f'{col} 分布')
                plt.xlabel(col)
                plt.ylabel('频次')
            
            plt.tight_layout()
            chart_path = os.path.join(output_dir, "numeric_distributions.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            charts_created.append(chart_path)
        
        # 3. 相关性矩阵
        if len(numeric_columns) > 1:
            corr_matrix = df[numeric_columns].corr()
            plt.figure(figsize=(10, 8))
            sns.heatmap(corr_matrix, annot=True, cmap='coolwarm', center=0,
                       square=True, fmt='.2f')
            plt.title('数值列相关性矩阵')
            plt.tight_layout()
            chart_path = os.path.join(output_dir, "correlation_matrix.png")
            plt.savefig(chart_path, dpi=300, bbox_inches='tight')
            plt.close()
            charts_created.append(chart_path)
        
        # 4. 分类列频次图
        categorical_columns = df.select_dtypes(include=['object']).columns
        for col in categorical_columns[:5]:  # 最多处理5列
            if df[col].nunique() <= 20:  # 只处理类别数较少的列
                plt.figure(figsize=(12, 6))
                value_counts = df[col].value_counts().head(10)
                value_counts.plot(kind='bar')
                plt.title(f'{col} 频次分布')
                plt.xlabel(col)
                plt.ylabel('频次')
                plt.xticks(rotation=45)
                plt.tight_layout()
                chart_path = os.path.join(output_dir, f"{col}_frequency.png")
                plt.savefig(chart_path, dpi=300, bbox_inches='tight')
                plt.close()
                charts_created.append(chart_path)
        
    except Exception as e:
        print(f"生成图表时出错: {str(e)}")
    
    return charts_created

def merge_multiple_csv(file_paths, output_path, merge_type='vertical'):
    """合并多个CSV文件"""
    try:
        dataframes = []
        
        for file_path in file_paths:
            # 尝试不同编码
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
            df = None
            
            for encoding in encodings:
                try:
                    df = pd.read_csv(file_path, encoding=encoding)
                    break
                except:
                    continue
            
            if df is not None:
                df['source_file'] = os.path.basename(file_path)  # 添加源文件标识
                dataframes.append(df)
        
        if not dataframes:
            raise ValueError("无法读取任何CSV文件")
        
        if merge_type == 'vertical':
            # 垂直合并（堆叠）
            merged_df = pd.concat(dataframes, ignore_index=True, sort=False)
        else:
            # 水平合并（按索引）
            merged_df = pd.concat(dataframes, axis=1)
        
        # 保存合并结果
        merged_df.to_csv(output_path, index=False, encoding='utf-8-sig')
        
        return {
            'merged_rows': len(merged_df),
            'merged_columns': len(merged_df.columns),
            'source_files': len(dataframes)
        }
        
    except Exception as e:
        raise ValueError(f"合并CSV文件失败: {str(e)}")

def split_csv_by_column(input_path, output_dir, split_column):
    """根据列值拆分CSV文件"""
    try:
        # 读取数据
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(input_path, encoding=encoding)
                break
            except:
                continue
        
        if df is None:
            raise ValueError("无法读取CSV文件")
        
        if split_column not in df.columns:
            raise ValueError(f"列 '{split_column}' 不存在")
        
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
        
        output_files = []
        unique_values = df[split_column].unique()
        
        for value in unique_values:
            if pd.isna(value):
                filename = f"{split_column}_NULL.csv"
            else:
                # 清理文件名中的特殊字符
                safe_value = re.sub(r'[<>:"/\\|?*]', '_', str(value))
                filename = f"{split_column}_{safe_value}.csv"
            
            subset = df[df[split_column] == value]
            output_path = os.path.join(output_dir, filename)
            subset.to_csv(output_path, index=False, encoding='utf-8-sig')
            output_files.append(output_path)
        
        return output_files
        
    except Exception as e:
        raise ValueError(f"拆分CSV文件失败: {str(e)}")

def analyze_log_file(log_file_path, patterns=None):
    """分析日志文件"""
    try:
        if patterns is None:
            patterns = {
                'ERROR': r'ERROR|Error|error',
                'WARNING': r'WARNING|Warning|warning',
                'INFO': r'INFO|Info|info',
                'IP': r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b',
                'TIMESTAMP': r'\d{4}-\d{2}-\d{2} \d{2}:\d{2}:\d{2}|\d{2}/\d{2}/\d{4} \d{2}:\d{2}:\d{2}'
            }
        
        analysis = {
            'total_lines': 0,
            'pattern_counts': {pattern: 0 for pattern in patterns},
            'line_samples': {pattern: [] for pattern in patterns},
            'file_size': os.path.getsize(log_file_path),
            'timestamps': []
        }
        
        # 尝试不同编码读取日志文件
        encodings = ['utf-8', 'gbk', 'gb2312', 'latin1']
        
        for encoding in encodings:
            try:
                with open(log_file_path, 'r', encoding=encoding) as f:
                    for line_num, line in enumerate(f, 1):
                        analysis['total_lines'] = line_num
                        
                        # 检查每个模式
                        for pattern_name, pattern in patterns.items():
                            if re.search(pattern, line, re.IGNORECASE):
                                analysis['pattern_counts'][pattern_name] += 1
                                
                                # 保存样本行（最多5行）
                                if len(analysis['line_samples'][pattern_name]) < 5:
                                    analysis['line_samples'][pattern_name].append({
                                        'line_number': line_num,
                                        'content': line.strip()
                                    })
                        
                        # 提取时间戳
                        timestamp_match = re.search(patterns.get('TIMESTAMP', ''), line)
                        if timestamp_match:
                            analysis['timestamps'].append(timestamp_match.group())
                
                break  # 成功读取则退出循环
                
            except UnicodeDecodeError:
                continue
        
        # 时间统计
        if analysis['timestamps']:
            analysis['time_range'] = {
                'first': analysis['timestamps'][0] if analysis['timestamps'] else None,
                'last': analysis['timestamps'][-1] if analysis['timestamps'] else None,
                'count': len(analysis['timestamps'])
            }
        
        return analysis
        
    except Exception as e:
        raise ValueError(f"分析日志文件失败: {str(e)}")

def create_data_summary(data_dict):
    """创建数据摘要"""
    try:
        summary = {
            'total_records': 0,
            'columns': [],
            'data_types': Counter(),
            'missing_data': 0,
            'memory_usage': 0
        }
        
        if isinstance(data_dict, dict):
            for key, value in data_dict.items():
                if isinstance(value, (list, tuple)):
                    summary['total_records'] = max(summary['total_records'], len(value))
                    summary['columns'].append(key)
                    summary['data_types'][type(value[0]).__name__ if value else 'empty'] += 1
        
        return summary
        
    except Exception as e:
        raise ValueError(f"创建数据摘要失败: {str(e)}")

def convert_data_format(input_file, output_file, input_format, output_format):
    """转换数据格式"""
    try:
        # 读取数据
        if input_format.lower() == 'csv':
            encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
            df = None
            for encoding in encodings:
                try:
                    df = pd.read_csv(input_file, encoding=encoding)
                    break
                except:
                    continue
        elif input_format.lower() == 'excel':
            df = pd.read_excel(input_file)
        elif input_format.lower() == 'json':
            df = pd.read_json(input_file)
        else:
            raise ValueError(f"不支持的输入格式: {input_format}")
        
        if df is None:
            raise ValueError("无法读取输入文件")
        
        # 保存数据
        if output_format.lower() == 'csv':
            df.to_csv(output_file, index=False, encoding='utf-8-sig')
        elif output_format.lower() == 'excel':
            df.to_excel(output_file, index=False)
        elif output_format.lower() == 'json':
            df.to_json(output_file, orient='records', force_ascii=False, indent=2)
        elif output_format.lower() == 'html':
            df.to_html(output_file, index=False, escape=False, table_id='data-table')
        else:
            raise ValueError(f"不支持的输出格式: {output_format}")
        
        return output_file
        
    except Exception as e:
        raise ValueError(f"转换数据格式失败: {str(e)}")

def create_pivot_table(input_file, output_file, index_col, columns_col, values_col, agg_func='sum'):
    """创建数据透视表"""
    try:
        # 读取数据
        encodings = ['utf-8', 'gbk', 'gb2312', 'utf-8-sig']
        df = None
        
        for encoding in encodings:
            try:
                df = pd.read_csv(input_file, encoding=encoding)
                break
            except:
                continue
        
        if df is None:
            raise ValueError("无法读取CSV文件")
        
        # 检查列是否存在
        required_cols = [index_col, columns_col, values_col]
        missing_cols = [col for col in required_cols if col not in df.columns]
        if missing_cols:
            raise ValueError(f"缺少列: {', '.join(missing_cols)}")
        
        # 创建透视表
        pivot_table = pd.pivot_table(
            df,
            index=index_col,
            columns=columns_col,
            values=values_col,
            aggfunc=agg_func,
            fill_value=0
        )
        
        # 保存结果
        pivot_table.to_csv(output_file, encoding='utf-8-sig')
        
        return {
            'rows': len(pivot_table),
            'columns': len(pivot_table.columns),
            'output_file': output_file
        }
        
    except Exception as e:
        raise ValueError(f"创建透视表失败: {str(e)}")