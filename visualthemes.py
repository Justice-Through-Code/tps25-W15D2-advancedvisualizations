import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')  # Ensure we're using the Tkinter backend
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import numpy as np
from datetime import datetime, timedelta
import json
from hovertooltip import HoverTooltip
from interactiveoverlays import WeatherOverlay
import matplotlib.animation as animation
from matplotlib.animation import FuncAnimation


class WeatherChartTheme:
    """Define and apply custom themes to weather charts."""
    
    # Define theme presets
    THEMES = {
        'light': {
            'figure.facecolor': '#FFFFFF',
            'axes.facecolor': '#FAFAFA',
            'axes.edgecolor': '#CCCCCC',
            'axes.labelcolor': '#333333',
            'axes.grid': True,
            'grid.color': '#E0E0E0',
            'grid.linestyle': '--',
            'grid.alpha': 0.5,
            'text.color': '#333333',
            'xtick.color': '#666666',
            'ytick.color': '#666666',
            'legend.facecolor': '#FFFFFF',
            'legend.edgecolor': '#CCCCCC',
            'lines.linewidth': 2,
            'font.size': 10,
            'font.family': 'sans-serif'
        },
        'dark': {
            'figure.facecolor': '#1E1E1E',
            'axes.facecolor': '#2D2D2D',
            'axes.edgecolor': '#444444',
            'axes.labelcolor': '#E0E0E0',
            'axes.grid': True,
            'grid.color': '#404040',
            'grid.linestyle': '--',
            'grid.alpha': 0.3,
            'text.color': '#E0E0E0',
            'xtick.color': '#CCCCCC',
            'ytick.color': '#CCCCCC',
            'legend.facecolor': '#2D2D2D',
            'legend.edgecolor': '#444444',
            'lines.linewidth': 2,
            'font.size': 10,
            'font.family': 'sans-serif'
        },
        'seaborn': {
            'figure.facecolor': 'white',
            'axes.facecolor': '#EAEAF2',
            'axes.edgecolor': '.8',
            'axes.labelcolor': '.15',
            'axes.grid': True,
            'grid.color': 'white',
            'grid.linestyle': '-',
            'grid.alpha': 1,
            'text.color': '.15',
            'xtick.color': '.15',
            'ytick.color': '.15',
            'legend.facecolor': 'white',
            'legend.edgecolor': '.8',
            'lines.linewidth': 2.5,
            'font.size': 11,
            'font.family': 'sans-serif'
        },
        'minimalist': {
            'figure.facecolor': 'white',
            'axes.facecolor': 'white',
            'axes.edgecolor': 'none',
            'axes.labelcolor': '#666666',
            'axes.grid': False,
            'grid.color': '#F0F0F0',
            'grid.linestyle': '-',
            'grid.alpha': 0.2,
            'text.color': '#666666',
            'xtick.color': '#999999',
            'ytick.color': '#999999',
            'legend.facecolor': 'white',
            'legend.edgecolor': 'none',
            'lines.linewidth': 3,
            'font.size': 9,
            'font.family': 'monospace'
        }
    }
    
    # Define color schemes for different data types
    COLOR_SCHEMES = {
        'temperature': {
            'light': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FD7272'],
            'dark': ['#FF6B6B', '#4ECDC4', '#45B7D1', '#FD7272'],
            'gradient': ['#2E86AB', '#F24236', '#F6AE2D', '#2F4858']
        },
        'precipitation': {
            'light': ['#3498DB', '#2980B9', '#1F618D', '#154360'],
            'dark': ['#5DADE2', '#3498DB', '#2980B9', '#1F618D'],
            'gradient': ['#D4E6F1', '#85C1E2', '#3498DB', '#1B4F72']
        },
        'wind': {
            'light': ['#27AE60', '#229954', '#1E8449', '#196F3D'],
            'dark': ['#58D68D', '#27AE60', '#229954', '#1E8449'],
            'gradient': ['#ABEBC6', '#58D68D', '#27AE60', '#145A32']
        }
    }
    
    @classmethod
    def apply_theme(cls, figure, ax, theme_name='light', custom_params=None):
        """Apply a theme to a matplotlib figure and axes."""
        if theme_name not in cls.THEMES:
            theme_name = 'light'
        
        theme = cls.THEMES[theme_name].copy()
        
        # Apply custom parameters if provided
        if custom_params:
            theme.update(custom_params)
        
        # Apply to figure
        figure.patch.set_facecolor(theme['figure.facecolor'])
        
        # Apply to axes
        ax.set_facecolor(theme['axes.facecolor'])
        ax.spines['top'].set_color(theme['axes.edgecolor'])
        ax.spines['bottom'].set_color(theme['axes.edgecolor'])
        ax.spines['left'].set_color(theme['axes.edgecolor'])
        ax.spines['right'].set_color(theme['axes.edgecolor'])
        
        # Apply to labels and ticks
        ax.xaxis.label.set_color(theme['axes.labelcolor'])
        ax.yaxis.label.set_color(theme['axes.labelcolor'])
        ax.tick_params(axis='x', colors=theme['xtick.color'])
        ax.tick_params(axis='y', colors=theme['ytick.color'])
        
        # Apply grid settings
        ax.grid(theme['axes.grid'], 
               color=theme['grid.color'],
               linestyle=theme['grid.linestyle'],
               alpha=theme['grid.alpha'])
        
        # Apply font settings
        plt.rcParams.update({
            'font.size': theme['font.size'],
            'font.family': theme['font.family']
        })
        
        # Apply to title if exists
        if ax.get_title():
            ax.title.set_color(theme['text.color'])
    
    @classmethod
    def get_color_palette(cls, data_type, theme='light', n_colors=4):
        """Get color palette for specific data type and theme."""
        if data_type in cls.COLOR_SCHEMES:
            scheme = cls.COLOR_SCHEMES[data_type]
            if theme in scheme:
                colors = scheme[theme]
                # Cycle colors if more needed
                return [colors[i % len(colors)] for i in range(n_colors)]
        
        # Default palette
        return plt.cm.viridis(np.linspace(0, 1, n_colors))
    
    @classmethod
    def apply_gradient_background(cls, ax, direction='vertical', colors=None):
        """Apply gradient background to axes."""
        if colors is None:
            colors = ['#FFFFFF', '#F0F0F0']
        
        # Create gradient
        if direction == 'vertical':
            gradient = np.linspace(0, 1, 256).reshape(256, 1)
            gradient = np.hstack((gradient, gradient))
        else:
            gradient = np.linspace(0, 1, 256).reshape(1, 256)
            gradient = np.vstack((gradient, gradient))
        
        # Apply gradient as background
        im = ax.imshow(gradient, aspect='auto', 
                      extent=[*ax.get_xlim(), *ax.get_ylim()],
                      interpolation='bilinear', alpha=0.3,
                      cmap=matplotlib.colors.LinearSegmentedColormap.from_list('', colors))
        
        # Ensure it's behind everything
        im.set_zorder(0)
        
        return im
