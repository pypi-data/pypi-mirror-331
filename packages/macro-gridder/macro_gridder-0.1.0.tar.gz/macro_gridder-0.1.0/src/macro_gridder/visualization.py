"""
Visualization tools for macro grid analysis
"""

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.patches import Rectangle
from typing import Dict, List, Tuple, Union, Any, Optional

from .core import MacroGridder


def plot_with_grid(prices: pd.Series, grid_df: pd.DataFrame, 
                  gridder: MacroGridder, fig=None, ax=None, 
                  show_macro_grid: bool = True, show_micro_grid: bool = True,
                  macro_grid_color: str = 'blue', micro_grid_color: str = 'gray',
                  price_line_color: str = 'black', alpha: float = 0.7) -> Tuple:
    """
    Plot price data with grid overlay

    Parameters:
    -----------
    prices : pd.Series
        Price series
    grid_df : pd.DataFrame
        Grid DataFrame
    gridder : MacroGridder
        MacroGridder instance
    fig : matplotlib.figure.Figure, optional
        Figure to plot on, by default None
    ax : matplotlib.axes.Axes, optional
        Axes to plot on, by default None
    show_macro_grid : bool, optional
        Whether to show macro grid, by default True
    show_micro_grid : bool, optional
        Whether to show micro grid, by default True
    macro_grid_color : str, optional
        Macro grid color, by default 'blue'
    micro_grid_color : str, optional
        Micro grid color, by default 'gray'
    price_line_color : str, optional
        Price line color, by default 'black'
    alpha : float, optional
        Transparency, by default 0.7

    Returns:
    --------
    Tuple
        (fig, ax) tuple
    """
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(12, 6))
    
    # 绘制价格线
    ax.plot(grid_df['index_seq'], prices, color=price_line_color, linewidth=1.5)
    
    # 绘制宏观网格
    if show_macro_grid:
        rects = gridder.get_macro_grid_rectangles(grid_df)
        for x_left, y_bottom, width, height in rects:
            rect = Rectangle((x_left, y_bottom), width, height, 
                            fill=False, edgecolor=macro_grid_color, 
                            linewidth=1.0, alpha=alpha)
            ax.add_patch(rect)
    
    # 绘制微观网格（单元格）
    if show_micro_grid:
        for _, row in grid_df.iterrows():
            rect = Rectangle((row['unit_left'], row['unit_bottom']), 
                            gridder.unit_width, gridder.unit_height,
                            fill=False, edgecolor=micro_grid_color, 
                            linewidth=0.5, alpha=alpha/2)
            ax.add_patch(rect)
    
    # 设置坐标轴
    ax.set_xlabel('Time Index')
    ax.set_ylabel('Price')
    ax.set_title('Price with Macro Grid')
    
    # 设置坐标轴范围
    ax.set_xlim(grid_df['index_seq'].min() - 1, grid_df['index_seq'].max() + 1)
    price_min = prices.min()
    price_max = prices.max()
    price_range = price_max - price_min
    ax.set_ylim(price_min - price_range * 0.05, price_max + price_range * 0.05)
    
    return fig, ax


def plot_grid_heatmap(grid_df: pd.DataFrame, gridder: MacroGridder, 
                     value_column: str = 'count', cmap: str = 'viridis',
                     fig=None, ax=None) -> Tuple:
    """
    Plot grid heatmap

    Parameters:
    -----------
    grid_df : pd.DataFrame
        Grid DataFrame
    gridder : MacroGridder
        MacroGridder instance
    value_column : str, optional
        Value column for heatmap, by default 'count'
    cmap : str, optional
        Colormap, by default 'viridis'
    fig : matplotlib.figure.Figure, optional
        Figure to plot on, by default None
    ax : matplotlib.axes.Axes, optional
        Axes to plot on, by default None

    Returns:
    --------
    Tuple
        (fig, ax) tuple
    """
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
    
    # 获取网格统计信息
    stats = gridder.get_grid_statistics(grid_df)
    
    # 准备热力图数据
    h_indices = [key[0] for key in stats.keys()]
    v_indices = [key[1] for key in stats.keys()]
    
    if not h_indices or not v_indices:
        ax.text(0.5, 0.5, 'Not enough data to generate heatmap', 
                horizontalalignment='center', verticalalignment='center')
        return fig, ax
    
    h_min, h_max = min(h_indices), max(h_indices)
    v_min, v_max = min(v_indices), max(v_indices)
    
    # 创建热力图矩阵
    heatmap_data = np.zeros((v_max - v_min + 1, h_max - h_min + 1))
    
    for (h_idx, v_idx), info in stats.items():
        if value_column == 'count':
            value = info['count']
        elif value_column == 'price_range':
            value = info['price_range']
        elif value_column == 'std_price':
            value = info['std_price']
        else:
            value = info.get(value_column, 0)
        
        heatmap_data[v_idx - v_min, h_idx - h_min] = value
    
    # 绘制热力图
    im = ax.imshow(heatmap_data, cmap=cmap, aspect='auto', origin='lower')
    
    # 添加颜色条
    cbar = fig.colorbar(im, ax=ax)
    cbar.set_label(value_column)
    
    # 设置坐标轴
    ax.set_xlabel('Time Macro Grid Index')
    ax.set_ylabel('Price Macro Grid Index')
    ax.set_title(f'Grid Heatmap ({value_column})')
    
    # 设置刻度
    ax.set_xticks(np.arange(0, h_max - h_min + 1, max(1, (h_max - h_min) // 10)))
    ax.set_xticklabels(np.arange(h_min, h_max + 1, max(1, (h_max - h_min) // 10)))
    
    ax.set_yticks(np.arange(0, v_max - v_min + 1, max(1, (v_max - v_min) // 10)))
    ax.set_yticklabels(np.arange(v_min, v_max + 1, max(1, (v_max - v_min) // 10)))
    
    return fig, ax


def plot_grid_transition(grid_df: pd.DataFrame, n_recent: int = 100, 
                        arrow_scale: float = 0.01, min_count: int = 2,
                        fig=None, ax=None) -> Tuple:
    """
    Plot grid transition, showing price movement between grids

    Parameters:
    -----------
    grid_df : pd.DataFrame
        Grid DataFrame
    n_recent : int, optional
        Use n most recent records, by default 100
    arrow_scale : float, optional
        Arrow scale factor, by default 0.01
    min_count : int, optional
        Minimum count to show arrow, by default 2
    fig : matplotlib.figure.Figure, optional
        Figure to plot on, by default None
    ax : matplotlib.axes.Axes, optional
        Axes to plot on, by default None

    Returns:
    --------
    Tuple
        (fig, ax) tuple
    """
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
    
    # 获取最近的记录
    recent_df = grid_df.iloc[-n_recent:].copy() if len(grid_df) > n_recent else grid_df.copy()
    
    if len(recent_df) < 2:
        ax.text(0.5, 0.5, 'Not enough data to generate transition plot', 
                horizontalalignment='center', verticalalignment='center')
        return fig, ax
    
    # 计算网格转移
    transitions = {}
    prev_h_idx = None
    prev_v_idx = None
    
    for _, row in recent_df.iterrows():
        h_idx = row['time_macro_index']
        v_idx = row['price_macro_index']
        
        if prev_h_idx is not None and prev_v_idx is not None:
            if (prev_h_idx != h_idx or prev_v_idx != v_idx):
                key = ((prev_h_idx, prev_v_idx), (h_idx, v_idx))
                transitions[key] = transitions.get(key, 0) + 1
        
        prev_h_idx = h_idx
        prev_v_idx = v_idx
    
    # 绘制网格点
    unique_grids = recent_df[['time_macro_index', 'price_macro_index']].drop_duplicates()
    ax.scatter(unique_grids['time_macro_index'], unique_grids['price_macro_index'], 
              s=50, c='blue', alpha=0.7)
    
    # 绘制转移箭头
    for (start, end), count in transitions.items():
        if count >= min_count:
            ax.arrow(start[0], start[1], end[0] - start[0], end[1] - start[1],
                    head_width=0.2, head_length=0.3, fc='red', ec='red',
                    length_includes_head=True, alpha=min(0.9, count * arrow_scale))
    
    # 设置坐标轴
    ax.set_xlabel('Time Macro Grid Index')
    ax.set_ylabel('Price Macro Grid Index')
    ax.set_title('Grid Transition Plot')
    
    # 设置网格
    ax.grid(True, linestyle='--', alpha=0.7)
    
    return fig, ax


def plot_grid_statistics(grid_df: pd.DataFrame, gridder: MacroGridder, 
                        stat_type: str = 'price_range', n_top: int = 10,
                        fig=None, ax=None) -> Tuple:
    """
    Plot grid statistics

    Parameters:
    -----------
    grid_df : pd.DataFrame
        Grid DataFrame
    gridder : MacroGridder
        MacroGridder instance
    stat_type : str, optional
        Statistic type to plot, by default 'price_range'
    n_top : int, optional
        Number of top grids to show, by default 10
    fig : matplotlib.figure.Figure, optional
        Figure to plot on, by default None
    ax : matplotlib.axes.Axes, optional
        Axes to plot on, by default None

    Returns:
    --------
    Tuple
        (fig, ax) tuple
    """
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(10, 6))
    
    # 获取网格统计信息
    stats = gridder.get_grid_statistics(grid_df)
    
    if not stats:
        ax.text(0.5, 0.5, 'No grid statistics available', 
                horizontalalignment='center', verticalalignment='center')
        return fig, ax
    
    # 提取统计数据
    grid_keys = []
    stat_values = []
    
    for key, info in stats.items():
        if stat_type in info:
            grid_keys.append(f"({key[0]},{key[1]})")
            stat_values.append(info[stat_type])
    
    # 排序并获取前n个
    if not grid_keys:
        ax.text(0.5, 0.5, f'No {stat_type} statistics available', 
                horizontalalignment='center', verticalalignment='center')
        return fig, ax
    
    sorted_indices = np.argsort(stat_values)[::-1]
    top_indices = sorted_indices[:n_top]
    
    top_keys = [grid_keys[i] for i in top_indices]
    top_values = [stat_values[i] for i in top_indices]
    
    # 绘制条形图
    ax.bar(top_keys, top_values, color='skyblue')
    
    # 设置坐标轴
    ax.set_xlabel('Grid Index (time, price)')
    ax.set_ylabel(stat_type)
    ax.set_title(f'Top {n_top} Grids by {stat_type}')
    
    # 旋转x轴标签以避免重叠
    plt.xticks(rotation=45, ha='right')
    
    # 调整布局
    plt.tight_layout()
    
    return fig, ax


def create_grid_dashboard(prices: pd.Series, grid_df: pd.DataFrame, 
                         gridder: MacroGridder, n_recent: int = 100) -> plt.Figure:
    """
    Create a comprehensive grid analysis dashboard

    Parameters:
    -----------
    prices : pd.Series
        Price series
    grid_df : pd.DataFrame
        Grid DataFrame
    gridder : MacroGridder
        MacroGridder instance
    n_recent : int, optional
        Number of recent data points to use for transition plot, by default 100

    Returns:
    --------
    plt.Figure
        Dashboard figure
    """
    # 创建仪表板
    fig = plt.figure(figsize=(18, 12))
    
    # 设置子图
    gs = fig.add_gridspec(2, 2)
    ax1 = fig.add_subplot(gs[0, 0])
    ax2 = fig.add_subplot(gs[0, 1])
    ax3 = fig.add_subplot(gs[1, 0])
    ax4 = fig.add_subplot(gs[1, 1])
    
    # 绘制价格与网格
    plot_with_grid(prices, grid_df, gridder, fig, ax1, 
                  show_micro_grid=False, alpha=0.5)
    
    # 绘制网格热力图
    plot_grid_heatmap(grid_df, gridder, value_column='count', fig=fig, ax=ax2)
    
    # 绘制网格转移图
    plot_grid_transition(grid_df, n_recent=n_recent, fig=fig, ax=ax3)
    
    # 绘制网格统计信息
    plot_grid_statistics(grid_df, gridder, stat_type='price_range', fig=fig, ax=ax4)
    
    # 设置标题
    fig.suptitle('Macro Grid Analysis Dashboard', fontsize=16)
    
    # 调整布局
    plt.tight_layout(rect=[0, 0, 1, 0.95])
    
    return fig


def plot_realtime_grid(gridder, fig=None, ax=None, 
                      show_history: bool = True, n_history: int = 20,
                      current_color: str = 'red', history_color: str = 'blue',
                      alpha: float = 0.7) -> Tuple:
    """
    Plot real-time grid information

    Parameters:
    -----------
    gridder : RealtimeMacroGridder
        RealtimeMacroGridder instance
    fig : matplotlib.figure.Figure, optional
        Figure to plot on, by default None
    ax : matplotlib.axes.Axes, optional
        Axes to plot on, by default None
    show_history : bool, optional
        Whether to show grid history, by default True
    n_history : int, optional
        Number of historical grids to show, by default 20
    current_color : str, optional
        Current grid color, by default 'red'
    history_color : str, optional
        Historical grid color, by default 'blue'
    alpha : float, optional
        Transparency, by default 0.7

    Returns:
    --------
    Tuple
        (fig, ax) tuple
    """
    if fig is None or ax is None:
        fig, ax = plt.subplots(figsize=(10, 8))
    
    # 获取当前网格信息
    current_grid = gridder.get_current_macro_grid()
    if current_grid is None:
        ax.text(0.5, 0.5, 'No current grid information available', 
                horizontalalignment='center', verticalalignment='center')
        return fig, ax
    
    # 绘制当前网格
    current_h_idx = gridder.current_time_macro_index
    current_v_idx = gridder.current_price_macro_index
    ax.scatter(current_h_idx, current_v_idx, s=100, c=current_color, 
              marker='o', label='Current Grid', zorder=10)
    
    # 绘制历史网格
    if show_history:
        recent_grids = gridder.get_recent_macro_grids(n_history)
        if recent_grids:
            # 修复：为每个列表推导式创建单独的循环变量
            h_indices = []
            v_indices = []
            counts = []
            
            # 使用常规循环替代列表推导式，避免变量作用域问题
            for grid_h_idx, grid_v_idx, info in recent_grids:
                if (grid_h_idx, grid_v_idx) != (current_h_idx, current_v_idx):
                    h_indices.append(grid_h_idx)
                    v_indices.append(grid_v_idx)
                    counts.append(info['count'])
            
            if h_indices and v_indices:
                sizes = [max(30, min(200, count * 5)) for count in counts]
                scatter = ax.scatter(h_indices, v_indices, s=sizes, c=history_color, 
                                    alpha=alpha, marker='o', label='Recent Grids')
                
                # 添加计数标签
                for grid_h_idx, grid_v_idx, info in recent_grids:
                    if (grid_h_idx, grid_v_idx) != (current_h_idx, current_v_idx):
                        ax.annotate(str(info['count']), (grid_h_idx, grid_v_idx), 
                                   xytext=(3, 3), textcoords='offset points')
    
    # 设置坐标轴
    ax.set_xlabel('Time Macro Grid Index')
    ax.set_ylabel('Price Macro Grid Index')
    ax.set_title('Real-time Grid Status')
    
    # 设置网格
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # 添加图例
    ax.legend()
    
    return fig, ax

def animate_grid_updates(gridder, times, prices, interval=200, 
                        save_animation=False, filename='grid_animation.mp4'):
    """
    Create animation of grid updates

    Parameters:
    -----------
    gridder : RealtimeMacroGridder
        RealtimeMacroGridder instance
    times : List
        List of time values
    prices : List
        List of price values
    interval : int, optional
        Animation interval in milliseconds, by default 200
    save_animation : bool, optional
        Whether to save animation, by default False
    filename : str, optional
        Output filename, by default 'grid_animation.mp4'

    Returns:
    --------
    matplotlib.animation.FuncAnimation
        Animation object
    """
    import matplotlib.animation as animation
    
    # 初始化网格
    gridder.initialize_with_history(times[:10], prices[:10])
    
    # 创建图形
    fig, ax = plt.subplots(figsize=(12, 8))
    
    # 设置坐标轴范围
    price_min = min(prices)
    price_max = max(prices)
    price_range = price_max - price_min
    ax.set_ylim(price_min - price_range * 0.1, price_max + price_range * 0.1)
    
    # 初始化绘图元素
    price_line, = ax.plot([], [], 'k-', lw=1.5, label='Price')
    grid_scatter = ax.scatter([], [], s=100, c='red', alpha=0.7)
    
    # 设置标题和标签
    ax.set_xlabel('Time Index')
    ax.set_ylabel('Price')
    ax.set_title('Grid Animation')
    ax.grid(True, linestyle='--', alpha=0.5)
    ax.legend()
    
    # 初始化函数
    def init():
        price_line.set_data([], [])
        grid_scatter.set_offsets(np.empty((0, 2)))
        return price_line, grid_scatter
    
    # 更新函数
    def update(frame):
        # 更新网格
        if frame > 10:  # 跳过已经初始化的数据
            h_idx, v_idx = gridder.update_with_tick(times[frame], prices[frame])
        
        # 更新价格线
        x_data = list(range(frame + 1))
        y_data = prices[:frame + 1]
        price_line.set_data(x_data, y_data)
        
        # 更新网格散点图
        grid_data = gridder.grid_data
        if not grid_data.empty:
            unique_grids = grid_data[['time_macro_index', 'price_macro_index']].drop_duplicates()
            grid_scatter.set_offsets(unique_grids[['time_macro_index', 'price_macro_index']].values)
        
        # 动态调整x轴范围
        ax.set_xlim(max(0, frame - 50), frame + 10)
        
        return price_line, grid_scatter
    
    # 创建动画
    ani = animation.FuncAnimation(fig, update, frames=len(times),
                                 init_func=init, blit=True, interval=interval)
    
    # 保存动画
    if save_animation:
        ani.save(filename, writer='ffmpeg', fps=30)
    
    return ani