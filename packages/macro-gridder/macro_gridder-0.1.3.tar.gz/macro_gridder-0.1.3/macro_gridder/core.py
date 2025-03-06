"""
Core functionality for macro grid calculation
"""

import numpy as np
import pandas as pd
from typing import Dict, List, Tuple, Union, Any, Optional

def compute_recommended_vertical_steps(
    median_price: float, min_price_tick: float, vertical_steps_ratio: float = 0.01
) -> int:
    """
    Calculate recommended vertical steps

    Parameters:
    -----------
    median_price : float
        Median price
    min_price_tick : float
        Minimum price tick
    vertical_steps_ratio : float, optional
        Vertical steps ratio, by default 0.01

    Returns:
    --------
    int
        Recommended vertical steps
    """
    # Calculate ratio-based step
    ratio_step = max(1, int(median_price * vertical_steps_ratio / min_price_tick))
    # Ensure step is a multiple of 5 for readability
    return max(1, int(ratio_step / 5) * 5)


class MacroGridder:
    """
    Price macro grid processor

    Converts price data into grid representation, supporting both macro grids and micro units
    """

    def __init__(self, config: Dict[str, Any]):
        """
        Initialize the macro grid processor

        Parameters:
        -----------
        config : Dict[str, Any]
            Configuration dictionary with keys:
            - horizontal_step: Time dimension grid step
            - vertical_step: Price dimension grid step
            - min_price_tick: Minimum price tick
        """
        self.config = config
        self.horizontal_step = config["horizontal_step"]
        self.vertical_step = config["vertical_step"]
        self.min_price_tick = config["min_price_tick"]
        self.visualizer = None

        # These will be set when creating the grid
        self.unit_width = 1.0
        self.unit_height = self.min_price_tick
        self.macro_width = self.horizontal_step * self.unit_width
        self.macro_height = self.vertical_step * self.unit_height
        self.time_origin = -self.unit_width / 2
        self.baseline = None
        self.price_origin = None

    def create_grid(self, times: Union[List, np.ndarray], prices: pd.Series) -> pd.DataFrame:
        """
        Create price grid

        Parameters:
        -----------
        times : Union[List, np.ndarray]
            Time series index
        prices : pd.Series
            Price series

        Returns:
        --------
        pd.DataFrame
            DataFrame containing grid information
        """
        n = len(times)
        seq = np.arange(n)
        self.unit_width = 1.0
        self.unit_height = self.min_price_tick
        self.macro_width = self.horizontal_step * self.unit_width
        self.macro_height = self.vertical_step * self.unit_height
        self.time_origin = -self.unit_width / 2
        self.baseline = prices.iloc[0]
        self.price_origin = self.baseline - self.macro_height / 2

        horizontal_index = np.floor(seq / self.horizontal_step).astype(int)
        vertical_index = np.floor((prices.values - self.price_origin) / self.macro_height).astype(int)
        unit_left = seq - self.unit_width / 2
        unit_bottom = prices.values - self.unit_height / 2

        grid_df = pd.DataFrame({
            'time_macro_index': horizontal_index,
            'price_macro_index': vertical_index,
            'unit_left': unit_left,
            'unit_bottom': unit_bottom,
            'index_seq': seq,
            'time_value': times,
            'price_center': prices.values
        }, index=times)
        return grid_df

    def get_macro_grid_rectangles(self, grid_df: pd.DataFrame) -> List[Tuple[float, float, float, float]]:
        """
        获取宏观网格矩形

        参数:
        -----------
        grid_df : pd.DataFrame
            网格数据框

        返回:
        --------
        List[Tuple[float, float, float, float]]
            矩形参数列表 [(x_left, y_bottom, width, height), ...]
        """
        unique_cells = grid_df[['time_macro_index', 'price_macro_index']].drop_duplicates()
        rects = []
        for _, row in unique_cells.iterrows():
            h_idx = row['time_macro_index']
            v_idx = row['price_macro_index']
            x_left = self.time_origin + h_idx * self.macro_width
            y_bottom = self.price_origin + v_idx * self.macro_height
            rects.append((x_left, y_bottom, self.macro_width, self.macro_height))
        return rects
    
    def get_grid_statistics(self, grid_df: pd.DataFrame) -> Dict[Tuple[int, int], Dict[str, Any]]:
        """
        计算每个宏观网格的统计信息

        参数:
        -----------
        grid_df : pd.DataFrame
            网格数据框

        返回:
        --------
        Dict[Tuple[int, int], Dict[str, Any]]
            包含网格统计信息的字典
        """
        stats = {}
        
        # 按宏观网格索引分组
        grouped = grid_df.groupby(['time_macro_index', 'price_macro_index'])
        
        for (h_idx, v_idx), group in grouped:
            grid_key = (h_idx, v_idx)
            
            # 计算统计信息
            stats[grid_key] = {
                'first_time': group.index.min(),
                'last_time': group.index.max(),
                'first_price': group['price_center'].iloc[0],
                'last_price': group['price_center'].iloc[-1],
                'high_price': group['price_center'].max(),
                'low_price': group['price_center'].min(),
                'mean_price': group['price_center'].mean(),
                'std_price': group['price_center'].std(),
                'count': len(group),
                'price_range': group['price_center'].max() - group['price_center'].min()
            }
            
        return stats