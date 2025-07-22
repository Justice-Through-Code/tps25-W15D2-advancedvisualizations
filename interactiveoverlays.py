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


class WeatherOverlay:
    def __init__(self, ax):
        self.ax = ax
        self.overlays = []
    
    def add_temperature_threshold(self, threshold, label, color='red', alpha=0.2):
        """Add a horizontal line showing temperature threshold."""
        line = self.ax.axhline(
            y=threshold,
            color=color,
            linestyle='--',
            linewidth=2,
            alpha=0.7,
            label=f'{label} ({threshold}°)'
        )
        
        # Add shaded region above/below threshold
        if 'high' in label.lower():
            span = self.ax.axhspan(
                threshold, 
                self.ax.get_ylim()[1],
                alpha=alpha,
                color=color,
                label=f'{label} zone'
            )
        else:
            span = self.ax.axhspan(
                self.ax.get_ylim()[0],
                threshold,
                alpha=alpha,
                color=color,
                label=f'{label} zone'
            )
        
        self.overlays.extend([line, span])
        return line, span
    
    def add_time_range_highlight(self, start_time, end_time, label, color='yellow', alpha=0.3):
        """Highlight a specific time range."""
        span = self.ax.axvspan(
            start_time,
            end_time,
            alpha=alpha,
            color=color,
            label=label
        )
        
        # Add text annotation
        mid_time = start_time + (end_time - start_time) / 2
        y_pos = self.ax.get_ylim()[1] * 0.95
        
        text = self.ax.text(
            mid_time,
            y_pos,
            label,
            horizontalalignment='center',
            verticalalignment='top',
            fontsize=10,
            bbox=dict(boxstyle='round,pad=0.3', facecolor=color, alpha=0.7)
        )
        
        self.overlays.extend([span, text])
        return span, text
    
    def add_anomaly_markers(self, times, values, labels=None):
        """Mark anomalous data points."""
        scatter = self.ax.scatter(
            times,
            values,
            c='red',
            s=100,
            marker='o',
            edgecolors='darkred',
            linewidths=2,
            label='Anomalies',
            zorder=5
        )
        
        # Add labels if provided
        texts = []
        if labels:
            for time, value, label in zip(times, values, labels):
                text = self.ax.annotate(
                    label,
                    xy=(time, value),
                    xytext=(10, 10),
                    textcoords='offset points',
                    fontsize=8,
                    bbox=dict(boxstyle='round,pad=0.3', facecolor='white', alpha=0.8),
                    arrowprops=dict(arrowstyle='->', color='red')
                )
                texts.append(text)
        
        self.overlays.append(scatter)
        self.overlays.extend(texts)
        return scatter, texts
    
    def add_trend_line(self, x_data, y_data, label='Trend', color='green', linewidth=2):
        """Add a trend line using linear regression."""
        # Convert dates to numbers for regression
        x_numeric = matplotlib.dates.date2num(x_data) if isinstance(x_data[0], datetime) else x_data
        
        # Calculate trend line
        z = np.polyfit(x_numeric, y_data, 1)
        p = np.poly1d(z)
        
        trend_line = self.ax.plot(
            x_data,
            p(x_numeric),
            color=color,
            linestyle='--',
            linewidth=linewidth,
            label=f'{label} (slope: {z[0]:.2f})',
            alpha=0.8
        )[0]
        
        self.overlays.append(trend_line)
        return trend_line
    
    def clear_overlays(self):
        """Remove all overlays."""
        for overlay in self.overlays:
            overlay.remove()
        self.overlays = []
