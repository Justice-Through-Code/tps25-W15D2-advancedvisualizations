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

class AnimatedWeatherChart:
    def __init__(self, figure, ax, max_points=100):
        self.figure = figure
        self.ax = ax
        self.max_points = max_points
        
        # Initialize data buffers
        self.time_buffer = []
        self.data_buffers = {}
        
        # Initialize line objects
        self.lines = {}
        
        # Animation object
        self.animation = None
        self.is_paused = False
        
        # Performance optimization
        self.use_blitting = True
    
    def add_series(self, name, color='blue', style='-', linewidth=2):
        """Add a data series to animate."""
        line, = self.ax.plot([], [], color=color, linestyle=style, 
                           linewidth=linewidth, label=name)
        self.lines[name] = line
        self.data_buffers[name] = []
        
        return line
    
    def start_animation(self, update_interval=1000):
        """Start the animation."""
        if self.animation is None:
            self.animation = FuncAnimation(
                self.figure,
                self._animate,
                interval=update_interval,
                blit=self.use_blitting,
                cache_frame_data=False
            )
    
    def stop_animation(self):
        """Stop the animation."""
        if self.animation:
            self.animation.event_source.stop()
    
    def pause_animation(self):
        """Pause/resume the animation."""
        if self.animation:
            if self.is_paused:
                self.animation.resume()
            else:
                self.animation.pause()
            self.is_paused = not self.is_paused
    
    def add_data_point(self, timestamp, data_dict):
        """Add a new data point to the animation buffers."""
        self.time_buffer.append(timestamp)
        
        for name, value in data_dict.items():
            if name in self.data_buffers:
                self.data_buffers[name].append(value)
        
        # Limit buffer size
        if len(self.time_buffer) > self.max_points:
            self.time_buffer.pop(0)
            for buffer in self.data_buffers.values():
                buffer.pop(0)
    
    def _animate(self, frame):
        """Animation update function."""
        artists = []
        
        for name, line in self.lines.items():
            if name in self.data_buffers and len(self.data_buffers[name]) > 0:
                line.set_data(self.time_buffer, self.data_buffers[name])
                artists.append(line)
        
        # Update axis limits
        if len(self.time_buffer) > 0:
            self.ax.set_xlim(self.time_buffer[0], self.time_buffer[-1])
            
            # Calculate y-limits
            all_values = []
            for buffer in self.data_buffers.values():
                all_values.extend(buffer)
            
            if all_values:
                ymin, ymax = min(all_values), max(all_values)
                margin = (ymax - ymin) * 0.1
                self.ax.set_ylim(ymin - margin, ymax + margin)
        
        return artists
    
    def create_transition_animation(self, old_data, new_data, duration=1000):
        """Create smooth transition between datasets."""
        steps = 30  # Number of animation frames
        
        def interpolate(old, new, step):
            """Interpolate between old and new values."""
            t = step / steps
            # Use easing function for smooth transition
            t = t * t * (3 - 2 * t)  # Smooth step (ease-in-out)
            return old + (new - old) * t
        
        def update(frame):
            for name, line in self.lines.items():
                if name in old_data and name in new_data:
                    # Interpolate data
                    interp_data = [
                        interpolate(old_data[name][i], new_data[name][i], frame)
                        for i in range(min(len(old_data[name]), len(new_data[name])))
                    ]
                    
                    line.set_ydata(interp_data)
            
            return list(self.lines.values())
        
        transition = FuncAnimation(
            self.figure,
            update,
            frames=steps,
            interval=duration // steps,
            blit=True,
            repeat=False
        )
        
        return transition
