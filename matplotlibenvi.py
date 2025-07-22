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

class InteractiveWeatherChart(ttk.Frame):
    def __init__(self, parent, preference_manager=None):
        super().__init__(parent)
        self.pref_manager = preference_manager
        
        # Create the matplotlib figure
        self.figure = Figure(figsize=(10, 6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        
        # Create canvas
        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add navigation toolbar
        self.toolbar = NavigationToolbar2Tk(self.canvas, self)
        self.toolbar.update()
        
        # Initialize data storage
        self.data = {
            'timestamps': [],
            'temperature': [],
            'humidity': [],
            'pressure': []
        }
        
        # Initialize interactive elements
        self.annotation = None
        self.hover_line = None
        self.selected_points = []
        
        # Connect event handlers
        self._connect_events()
        
        # Apply initial styling
        self._apply_styling()
    
    def _connect_events(self):
        """Connect matplotlib event handlers."""
        self.canvas.mpl_connect('motion_notify_event', self._on_mouse_move)
        self.canvas.mpl_connect('button_press_event', self._on_click)
        self.canvas.mpl_connect('key_press_event', self._on_key_press)
        self.canvas.mpl_connect('scroll_event', self._on_scroll)
        
        # Connect to figure events for responsiveness
        self.canvas.mpl_connect('resize_event', self._on_resize)

    def _on_mouse_move(self, event):
        pass

    def _on_click(self, event):
        pass

    def _on_key_press(self, event):
        pass

    def _on_scroll(self, event):
        pass

    def _on_resize(self, event):
        self.canvas.draw_idle()
    
    def _apply_styling(self):
        """Apply styling based on preferences."""
        if self.pref_manager:
            theme = self.pref_manager.get('display', 'theme', 'light')
            if theme == 'dark':
                plt.style.use('dark_background')
                self.figure.patch.set_facecolor('#1E1E1E')
                self.ax.set_facecolor('#2D2D2D')
            else:
                plt.style.use('seaborn-v0_8-whitegrid')
                self.figure.patch.set_facecolor('white')
                self.ax.set_facecolor('white')
        
        # Set grid styling
        self.ax.grid(True, alpha=0.3, linestyle='--')
        self.ax.set_xlabel('Time', fontsize=12)
        self.ax.set_ylabel('Value', fontsize=12)
        self.ax.set_title('Weather Data Visualization', fontsize=14, fontweight='bold')

    def plot_data(self):
        self.ax.clear()
        timestamps = self.data.get('timestamps', [])
        temperature = self.data.get('temperature', [])
        humidity = self.data.get('humidity', [])
        pressure = self.data.get('pressure', [])

        if len(timestamps) > 0:
            self.ax.plot(timestamps, temperature, color='red', label='Temperature')
            self.ax.plot(timestamps, humidity, color='blue', label='Humidity')
            self.ax.plot(timestamps, pressure, color='green', label='Pressure')

            self.ax.legend(loc='upper right')
            self.ax.grid(True, alpha=0.3)
            self.ax.set_title("Weather Data Visualization")

            self.canvas.draw_idle()
