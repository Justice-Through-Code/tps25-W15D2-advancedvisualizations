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



class HoverTooltip:
    def __init__(self, ax, canvas):
        self.ax = ax
        self.canvas = canvas
        self.annotation = self.ax.annotate(
            '',
            xy=(0, 0),
            xytext=(20, 20),
            textcoords='offset points',
            bbox=dict(boxstyle='round,pad=0.5', fc='yellow', alpha=0.9),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0'),
            visible=False,
            zorder=1000  # Ensure tooltip is on top
        )
        self.lines = []
        self.labels = []
    
    def add_line(self, line, label):
        """Add a line to monitor for hover events."""
        self.lines.append(line)
        self.labels.append(label)
    
    def update(self, event):
        """Update tooltip based on mouse position."""
        if event.inaxes != self.ax:
            self.annotation.set_visible(False)
            self.canvas.draw_idle()
            return
        
        # Find the nearest point on any line
        min_distance = float('inf')
        nearest_point = None
        nearest_label = None
        
        for line, label in zip(self.lines, self.labels):
            xdata = line.get_xdata()
            ydata = line.get_ydata()
            
            if len(xdata) == 0:
                continue
            
            # Convert display coordinates to data coordinates
            points = np.column_stack([xdata, ydata])
            
            # Find nearest point
            if event.xdata is not None and event.ydata is not None:
                distances = np.sqrt((points[:, 0] - event.xdata)**2 + 
                                  (points[:, 1] - event.ydata)**2)
                idx = np.argmin(distances)
                distance = distances[idx]
                
                if distance < min_distance:
                    min_distance = distance
                    nearest_point = (xdata[idx], ydata[idx], idx)
                    nearest_label = label
        
        # Update annotation if close enough to a point
        if nearest_point and min_distance < 0.05:  # Threshold in data units
            x, y, idx = nearest_point
            
            # Format the tooltip text
            if isinstance(x, (int, float)):
                # Assume x is matplotlib date number
                date = matplotlib.dates.num2date(x)
                date_str = date.strftime('%Y-%m-%d %H:%M')
            else:
                date_str = str(x)
            
            text = f'{nearest_label}\n{date_str}\nValue: {y:.2f}'
            
            # Update annotation
            self.annotation.xy = (x, y)
            self.annotation.set_text(text)
            self.annotation.set_visible(True)
            
            # Ensure annotation stays within axes bounds
            self._adjust_annotation_position()
        else:
            self.annotation.set_visible(False)
        
        self.canvas.draw_idle()
    
    def _adjust_annotation_position(self):
        """Adjust annotation position to stay within axes bounds."""
        # Get axes bounds in display coordinates
        bbox = self.ax.get_window_extent()
        
        # Get annotation bounds
        ann_bbox = self.annotation.get_window_extent()
        
        # Adjust if needed
        x_offset = 20
        y_offset = 20
        
        if ann_bbox.x1 > bbox.x1:
            x_offset = -100  # Move to left
        if ann_bbox.y1 > bbox.y1:
            y_offset = -50  # Move down
        
        self.annotation.xyann = (x_offset, y_offset)
