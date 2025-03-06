"""
Utility functions for macro grid analysis
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Union, Any, Optional
import json
import os


def load_config_from_json(config_path: str) -> Dict[str, Any]:
    """
    Load configuration from JSON file

    Parameters:
    -----------
    config_path : str
        Path to configuration file

    Returns:
    --------
    Dict[str, Any]
        Configuration dictionary
    """
    if not os.path.exists(config_path):
        raise FileNotFoundError(f"配置文件不存在: {config_path}")
    
    with open(config_path, 'r', encoding='utf-8') as f:
        config = json.load(f)
    
    # 验证必要的配置项
    required_keys = ['horizontal_step', 'vertical_step', 'min_price_tick']
    missing_keys = [key for key in required_keys if key not in config]
    
    if missing_keys:
        raise ValueError(f"配置文件缺少必要的键: {', '.join(missing_keys)}")
    
    return config


def save_config_to_json(config: Dict[str, Any], config_path: str) -> None:
    """
    Save configuration to JSON file

    Parameters:
    -----------
    config : Dict[str, Any]
        Configuration dictionary
    config_path : str
        Path to save configuration file
    """
    with open(config_path, 'w', encoding='utf-8') as f:
        json.dump(config, f, indent=4)


def load_price_data(file_path: str, date_column: str = None, 
                   price_column: str = 'price', 
                   date_format: str = None) -> pd.DataFrame:
    """
    Load price data from CSV or Excel file

    Parameters:
    -----------
    file_path : str
        Path to data file
    date_column : str, optional
        Date column name, by default None (will use first column)
    price_column : str, optional
        Price column name, by default 'price'
    date_format : str, optional
        Date format string for parsing, by default None

    Returns:
    --------
    pd.DataFrame
        DataFrame with price data
    """
    # 检查文件扩展名
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.csv':
        df = pd.read_csv(file_path)
    elif file_ext in ['.xlsx', '.xls']:
        df = pd.read_excel(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {file_ext}")
    
    # 处理日期列
    if date_column is None:
        date_column = df.columns[0]
    
    if date_format:
        df[date_column] = pd.to_datetime(df[date_column], format=date_format)
    else:
        df[date_column] = pd.to_datetime(df[date_column])
    
    # 设置日期列为索引
    df.set_index(date_column, inplace=True)
    
    # 确保价格列存在
    if price_column not in df.columns:
        raise ValueError(f"价格列 '{price_column}' 不存在于数据中")
    
    return df


def resample_price_data(df: pd.DataFrame, price_column: str = 'price', 
                       freq: str = '1min', method: str = 'last') -> pd.Series:
    """
    Resample price data to specified frequency

    Parameters:
    -----------
    df : pd.DataFrame
        DataFrame with price data
    price_column : str, optional
        Price column name, by default 'price'
    freq : str, optional
        Resampling frequency, by default '1min'
    method : str, optional
        Resampling method ('last', 'first', 'mean', etc.), by default 'last'

    Returns:
    --------
    pd.Series
        Resampled price series
    """
    price_series = df[price_column]
    
    if method == 'last':
        resampled = price_series.resample(freq).last()
    elif method == 'first':
        resampled = price_series.resample(freq).first()
    elif method == 'mean':
        resampled = price_series.resample(freq).mean()
    elif method == 'ohlc':
        # 返回OHLC数据
        return df[price_column].resample(freq).ohlc()
    else:
        raise ValueError(f"不支持的重采样方法: {method}")
    
    return resampled.dropna()


def calculate_optimal_grid_params(price_series: pd.Series, 
                                 target_grid_count: int = 20,
                                 min_price_tick: float = 0.01) -> Dict[str, Any]:
    """
    Calculate optimal grid parameters based on price volatility

    Parameters:
    -----------
    price_series : pd.Series
        Price series
    target_grid_count : int, optional
        Target number of grids, by default 20
    min_price_tick : float, optional
        Minimum price tick, by default 0.01

    Returns:
    --------
    Dict[str, Any]
        Dictionary with optimal grid parameters
    """
    # 计算价格范围
    price_min = price_series.min()
    price_max = price_series.max()
    price_range = price_max - price_min
    
    # 计算价格波动率
    price_std = price_series.std()
    
    # 计算垂直步长
    vertical_step = max(1, int(price_range / (target_grid_count * min_price_tick)))
    
    # 计算水平步长 (基于数据点数量)
    n_points = len(price_series)
    horizontal_step = max(1, int(n_points / target_grid_count))
    
    return {
        'horizontal_step': horizontal_step,
        'vertical_step': vertical_step,
        'min_price_tick': min_price_tick,
        'price_range': price_range,
        'price_std': price_std,
        'price_min': price_min,
        'price_max': price_max
    }


def export_grid_data(grid_df: pd.DataFrame, file_path: str) -> None:
    """
    Export grid data to CSV or Excel file

    Parameters:
    -----------
    grid_df : pd.DataFrame
        Grid DataFrame
    file_path : str
        Path to save file
    """
    # 检查文件扩展名
    file_ext = os.path.splitext(file_path)[1].lower()
    
    if file_ext == '.csv':
        grid_df.to_csv(file_path)
    elif file_ext in ['.xlsx', '.xls']:
        grid_df.to_excel(file_path)
    else:
        raise ValueError(f"不支持的文件格式: {file_ext}")