"""
Real-time macro grid calculation functionality
"""

import numpy as np
import pandas as pd
from collections import deque
from typing import Dict, List, Tuple, Union, Any, Optional, Deque

from .core import MacroGridder


class RealtimeMacroGridder(MacroGridder):
    """
    Real-time price macro grid processor

    Extends MacroGridder to support real-time price data processing
    """

    def __init__(self, config: Dict[str, Any], max_history: int = 10000):
        """
        Initialize real-time macro grid processor

        Parameters:
        -----------
        config : Dict[str, Any]
            Configuration dictionary
        max_history : int, optional
            Maximum history data points to keep, by default 10000
        """
        super().__init__(config)
        self.max_history = max_history
        self.initialized = False
        
        # Use deque for efficient data storage
        self.times_queue: Deque = deque(maxlen=max_history)
        self.prices_queue: Deque = deque(maxlen=max_history)
        
        # Store calculated grid data
        self.grid_data = pd.DataFrame()
        
        # Latest macro grid indices
        self.current_time_macro_index: Optional[int] = None
        self.current_price_macro_index: Optional[int] = None
        
        # Macro grid history
        self.macro_grid_history: Dict[Tuple[int, int], Dict[str, Any]] = {}
        
    def initialize_with_history(self, times: Union[List, np.ndarray], 
                               prices: Union[List, np.ndarray, pd.Series]) -> pd.DataFrame:
        """
        Initialize grid with historical data

        Parameters:
        -----------
        times : Union[List, np.ndarray]
            Historical time series
        prices : Union[List, np.ndarray, pd.Series]
            Historical price series

        Returns:
        --------
        pd.DataFrame
            Grid DataFrame
        """
        # Initialize queues
        self.times_queue.extend(times[-self.max_history:])
        self.prices_queue.extend(prices[-self.max_history:])
        
        # Create initial grid
        times_array = np.array(list(self.times_queue))
        prices_array = np.array(list(self.prices_queue))
        
        if isinstance(prices, pd.Series):
            price_series = prices.iloc[-len(times_array):]
        else:
            price_series = pd.Series(prices_array, index=times_array)
            
        self.grid_data = self.create_grid(times_array, price_series)
        
        # Update macro grid history
        self._update_macro_grid_history()
        
        self.initialized = True
        return self.grid_data
    
    def update_with_tick(self, time: Any, price: float) -> Tuple[int, int]:
        """
        Update grid with latest tick data

        Parameters:
        -----------
        time : Any
            Latest tick time
        price : float
            Latest tick price

        Returns:
        --------
        Tuple[int, int]
            (time_macro_index, price_macro_index) of the latest tick
        """
        if not self.initialized:
            raise RuntimeError("请先使用历史数据初始化网格")
        
        # Add new data
        self.times_queue.append(time)
        self.prices_queue.append(price)
        
        # Calculate new data's macro grid indices
        seq_index = len(self.times_queue) - 1
        horizontal_index = int(np.floor(seq_index / self.horizontal_step))
        vertical_index = int(np.floor((price - self.price_origin) / self.macro_height))
        
        # Update current macro grid indices
        self.current_time_macro_index = horizontal_index
        self.current_price_macro_index = vertical_index
        
        # Create new grid record
        new_grid_row = pd.DataFrame({
            'time_macro_index': [horizontal_index],
            'price_macro_index': [vertical_index],
            'unit_left': [seq_index - self.unit_width / 2],
            'unit_bottom': [price - self.unit_height / 2],
            'index_seq': [seq_index],
            'time_value': [time],
            'price_center': [price]
        }, index=[time])
        
        # Update grid data
        self.grid_data = pd.concat([self.grid_data, new_grid_row])
        if len(self.grid_data) > self.max_history:
            self.grid_data = self.grid_data.iloc[-self.max_history:]
        
        # Update macro grid history
        self._update_macro_grid_with_tick(time, price, horizontal_index, vertical_index)
        
        return horizontal_index, vertical_index
    
    def _update_macro_grid_history(self) -> None:
        """Update macro grid history"""
        for _, row in self.grid_data.iterrows():
            h_idx = row['time_macro_index']
            v_idx = row['price_macro_index']
            time = row.name
            price = row['price_center']
            
            grid_key = (h_idx, v_idx)
            if grid_key not in self.macro_grid_history:
                self.macro_grid_history[grid_key] = {
                    'first_time': time,
                    'first_price': price,
                    'last_time': time,
                    'last_price': price,
                    'high_price': price,
                    'low_price': price,
                    'prices': [price],
                    'times': [time],
                    'count': 1
                }
            else:
                info = self.macro_grid_history[grid_key]
                info['last_time'] = time
                info['last_price'] = price
                info['high_price'] = max(info['high_price'], price)
                info['low_price'] = min(info['low_price'], price)
                info['prices'].append(price)
                info['times'].append(time)
                info['count'] += 1
    
    def _update_macro_grid_with_tick(self, time: Any, price: float, 
                                    h_idx: int, v_idx: int) -> None:
        """
        Update macro grid history with a single tick

        Parameters:
        -----------
        time : Any
            Tick time
        price : float
            Tick price
        h_idx : int
            Horizontal macro grid index
        v_idx : int
            Vertical macro grid index
        """
        grid_key = (h_idx, v_idx)
        if grid_key not in self.macro_grid_history:
            self.macro_grid_history[grid_key] = {
                'first_time': time,
                'first_price': price,
                'last_time': time,
                'last_price': price,
                'high_price': price,
                'low_price': price,
                'prices': [price],
                'times': [time],
                'count': 1
            }
        else:
            info = self.macro_grid_history[grid_key]
            info['last_time'] = time
            info['last_price'] = price
            info['high_price'] = max(info['high_price'], price)
            info['low_price'] = min(info['low_price'], price)
            info['prices'].append(price)
            info['times'].append(time)
            info['count'] += 1
    
    def get_current_macro_grid(self) -> Optional[Dict[str, Any]]:
        """
        Get current macro grid information

        Returns:
        --------
        Optional[Dict[str, Any]]
            Current macro grid information or None if not initialized
        """
        if self.current_time_macro_index is None or self.current_price_macro_index is None:
            return None
        
        grid_key = (self.current_time_macro_index, self.current_price_macro_index)
        return self.macro_grid_history.get(grid_key)
    
    def get_macro_grid_info(self, time_macro_index: int, 
                           price_macro_index: int) -> Optional[Dict[str, Any]]:
        """
        Get information for a specific macro grid

        Parameters:
        -----------
        time_macro_index : int
            Time macro grid index
        price_macro_index : int
            Price macro grid index

        Returns:
        --------
        Optional[Dict[str, Any]]
            Macro grid information or None if not found
        """
        grid_key = (time_macro_index, price_macro_index)
        return self.macro_grid_history.get(grid_key)
    
    def get_recent_macro_grids(self, n: int = 5) -> List[Tuple[int, int, Dict[str, Any]]]:
        """
        Get recent n macro grids information

        Parameters:
        -----------
        n : int, optional
            Number of recent grids to return, by default 5

        Returns:
        --------
        List[Tuple[int, int, Dict[str, Any]]]
            List of (h_idx, v_idx, grid_info) tuples
        """
        if not self.grid_data.empty:
            recent_data = self.grid_data.iloc[-n:]
            unique_grids = recent_data[['time_macro_index', 'price_macro_index']].drop_duplicates()
            result = []
            for _, row in unique_grids.iterrows():
                h_idx = row['time_macro_index']
                v_idx = row['price_macro_index']
                grid_info = self.get_macro_grid_info(h_idx, v_idx)
                if grid_info:
                    result.append((h_idx, v_idx, grid_info))
            return result
        return []