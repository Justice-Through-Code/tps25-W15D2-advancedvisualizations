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

class ClickInteraction:
    def __init__(self, ax, canvas, callback=None):
        self.ax = ax
        self.canvas = canvas
        self.callback = callback
        self.selected_points = []
        self.selection_markers = []
        self.range_selector = None
        self.selection_mode = 'point'  # 'point' or 'range'
    
    def set_selection_mode(self, mode):
        """Set selection mode ('point' or 'range')."""
        self.selection_mode = mode
        self.clear_selection()
    
    def handle_click(self, event, lines_data):
        """Handle mouse click events."""
        if event.inaxes != self.ax:
            return
        
        if self.selection_mode == 'point':
            self._handle_point_selection(event, lines_data)
        elif self.selection_mode == 'range':
            self._handle_range_selection(event)
    
    def _handle_point_selection(self, event, lines_data):
        """Handle selection of individual points."""
        # Find nearest point
        min_distance = float('inf')
        selected_point = None
        
        for line_data in lines_data:
            xdata = line_data['x']
            ydata = line_data['y']
            label = line_data['label']
            
            if len(xdata) == 0:
                continue
            
            # Calculate distances
            distances = np.sqrt((xdata - event.xdata)**2 + (ydata - event.ydata)**2)
            idx = np.argmin(distances)
            
            if distances[idx] < min_distance:
                min_distance = distances[idx]
                selected_point = {
                    'x': xdata[idx],
                    'y': ydata[idx],
                    'index': idx,
                    'label': label,
                    'series': line_data
                }
        
        # Select point if close enough
        if selected_point and min_distance < 0.05:
            # Toggle selection
            point_key = (selected_point['x'], selected_point['y'], selected_point['label'])
            
            if point_key in self.selected_points:
                # Deselect
                self.selected_points.remove(point_key)
                self._remove_selection_marker(point_key)
            else:
                # Select
                self.selected_points.append(point_key)
                self._add_selection_marker(selected_point)
            
            # Trigger callback
            if self.callback:
                self.callback('point_selected', selected_point)
            
            self.canvas.draw_idle()
    
    def _handle_range_selection(self, event):
        """Handle range selection with rectangle selector."""
        if self.range_selector is None:
            from matplotlib.widgets import RectangleSelector
            
            def on_select(eclick, erelease):
                x1, y1 = eclick.xdata, eclick.ydata
                x2, y2 = erelease.xdata, erelease.ydata
                
                if x1 is not None and x2 is not None:
                    # Ensure x1 < x2
                    if x1 > x2:
                        x1, x2 = x2, x1
                    if y1 > y2:
                        y1, y2 = y2, y1
                    
                    # Trigger callback with selected range
                    if self.callback:
                        self.callback('range_selected', {
                            'x_range': (x1, x2),
                            'y_range': (y1, y2)
                        })
            
            self.range_selector = RectangleSelector(
                self.ax,
                on_select,
                useblit=True,
                button=[1],  # Left mouse button
                minspanx=5,
                minspany=5,
                spancoords='pixels',
                interactive=True,
                rectprops=dict(facecolor='blue', alpha=0.2)
            )
    
    def _add_selection_marker(self, point):
        """Add visual marker for selected point."""
        marker = self.ax.scatter(
            point['x'],
            point['y'],
            c='yellow',
            s=150,
            marker='*',
            edgecolors='orange',
            linewidths=2,
            zorder=10
        )
        
        self.selection_markers.append({
            'marker': marker,
            'key': (point['x'], point['y'], point['label'])
        })
    
    def _remove_selection_marker(self, point_key):
        """Remove selection marker."""
        for i, item in enumerate(self.selection_markers):
            if item['key'] == point_key:
                item['marker'].remove()
                self.selection_markers.pop(i)
                break
    
    def clear_selection(self):
        """Clear all selections."""
        for item in self.selection_markers:
            item['marker'].remove()
        
        self.selection_markers = []
        self.selected_points = []
        
        if self.range_selector:
            self.range_selector.set_active(False)
            self.range_selector = None
