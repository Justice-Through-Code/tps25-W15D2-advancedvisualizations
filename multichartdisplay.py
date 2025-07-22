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

class SynchronizedWeatherDashboard(ttk.Frame):
    def __init__(self, parent, preference_manager=None):
        super().__init__(parent)
        self.pref_manager = preference_manager
        self.charts = []
        self.shared_x_axis = None
        
        # Create the dashboard layout
        self._create_layout()
        
        # Connect synchronization
        self._setup_synchronization()
    
    def _create_layout(self):
        """Create multi-chart layout."""
        # Create a scrollable frame
        canvas = tk.Canvas(self)
        scrollbar = ttk.Scrollbar(self, orient="vertical", command=canvas.yview)
        scrollable_frame = ttk.Frame(canvas)
        
        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )
        
        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        
        # Grid the canvas and scrollbar
        canvas.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        
        # Configure grid weights
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(0, weight=1)
        
        # Create charts
        self._create_temperature_chart(scrollable_frame)
        self._create_precipitation_chart(scrollable_frame)
        self._create_wind_chart(scrollable_frame)
        self._create_pressure_chart(scrollable_frame)
    
    def _create_temperature_chart(self, parent):
        """Create temperature chart."""
        frame = ttk.LabelFrame(parent, text="Temperature", padding="5")
        frame.grid(row=0, column=0, sticky="ew", padx=5, pady=5)
        
        fig = Figure(figsize=(12, 3), dpi=100)
        ax = fig.add_subplot(111)
        
        # Share x-axis with other charts
        if self.shared_x_axis is None:
            self.shared_x_axis = ax
        else:
            ax.sharex(self.shared_x_axis)
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        # Add toolbar
        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()
        
        self.charts.append({
            'name': 'temperature',
            'figure': fig,
            'ax': ax,
            'canvas': canvas,
            'toolbar': toolbar,
            'data_lines': [],
            'overlays': WeatherOverlay(ax),
            'tooltip': HoverTooltip(ax, canvas)
        })
        
        return ax
    
    def _create_precipitation_chart(self, parent):
        """Create precipitation chart."""
        frame = ttk.LabelFrame(parent, text="Precipitation", padding="5")
        frame.grid(row=1, column=0, sticky="ew", padx=5, pady=5)
        
        fig = Figure(figsize=(12, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.sharex(self.shared_x_axis)
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()
        
        self.charts.append({
            'name': 'precipitation',
            'figure': fig,
            'ax': ax,
            'canvas': canvas,
            'toolbar': toolbar,
            'data_lines': [],
            'overlays': WeatherOverlay(ax),
            'tooltip': HoverTooltip(ax, canvas)
        })
        
        return ax
    
    def _create_wind_chart(self, parent):
        """Create wind speed and direction chart."""
        frame = ttk.LabelFrame(parent, text="Wind", padding="5")
        frame.grid(row=2, column=0, sticky="ew", padx=5, pady=5)
        
        fig = Figure(figsize=(12, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.sharex(self.shared_x_axis)
        
        # Create second y-axis for wind direction
        ax2 = ax.twinx()
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()
        
        self.charts.append({
            'name': 'wind',
            'figure': fig,
            'ax': ax,
            'ax2': ax2,  # Secondary axis
            'canvas': canvas,
            'toolbar': toolbar,
            'data_lines': [],
            'overlays': WeatherOverlay(ax),
            'tooltip': HoverTooltip(ax, canvas)
        })
        
        return ax
    
    def _create_pressure_chart(self, parent):
        """Create pressure chart."""
        frame = ttk.LabelFrame(parent, text="Pressure", padding="5")
        frame.grid(row=3, column=0, sticky="ew", padx=5, pady=5)
        
        fig = Figure(figsize=(12, 3), dpi=100)
        ax = fig.add_subplot(111)
        ax.sharex(self.shared_x_axis)
        
        canvas = FigureCanvasTkAgg(fig, frame)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        
        toolbar = NavigationToolbar2Tk(canvas, frame)
        toolbar.update()
        
        self.charts.append({
            'name': 'pressure',
            'figure': fig,
            'ax': ax,
            'canvas': canvas,
            'toolbar': toolbar,
            'data_lines': [],
            'overlays': WeatherOverlay(ax),
            'tooltip': HoverTooltip(ax, canvas)
        })
        
        return ax
    
    def _setup_synchronization(self):
        """Setup synchronized zooming and panning."""
        # Connect zoom/pan events
        for chart in self.charts:
            chart['canvas'].mpl_connect('motion_notify_event', 
                                      lambda event, c=chart: self._on_motion(event, c))
            
            # Synchronize zoom events
            chart['ax'].callbacks.connect('xlim_changed', self._on_xlim_changed)
    
    def _on_xlim_changed(self, ax):
        """Handle x-axis limit changes for synchronization."""
        # Update all other charts to match
        xlim = ax.get_xlim()
        for chart in self.charts:
            if chart['ax'] != ax and chart['ax'].get_xlim() != xlim:
                chart['ax'].set_xlim(xlim)
                chart['canvas'].draw_idle()
    
    def _on_motion(self, event, chart):
        """Handle mouse motion for synchronized crosshair."""
        if event.inaxes:
            # Update tooltips
            chart['tooltip'].update(event)
            
            # Update crosshair on all charts
            if hasattr(self, 'crosshair_lines'):
                for line in self.crosshair_lines:
                    line.set_xdata([event.xdata, event.xdata])
            else:
                self.crosshair_lines = []
                for c in self.charts:
                    line = c['ax'].axvline(x=event.xdata, color='gray', 
                                         linestyle='--', alpha=0.5, linewidth=1)
                    self.crosshair_lines.append(line)
            
            # Redraw all charts
            for c in self.charts:
                c['canvas'].draw_idle()
    
    def update_data(self, weather_data):
        """Update all charts with new weather data."""
        # Clear existing data
        for chart in self.charts:
            chart['ax'].clear()
            chart['data_lines'] = []
        
        # Extract data
        timestamps = weather_data['timestamps']
        
        # Update temperature chart
        temp_chart = next(c for c in self.charts if c['name'] == 'temperature')
        temp_line = temp_chart['ax'].plot(timestamps, weather_data['temperature'], 
                                        'r-', label='Temperature')[0]
        temp_chart['data_lines'].append(temp_line)
        temp_chart['tooltip'].add_line(temp_line, 'Temperature')
        
        # Add feels-like temperature if available
        if 'feels_like' in weather_data:
            feels_line = temp_chart['ax'].plot(timestamps, weather_data['feels_like'], 
                                             'r--', alpha=0.7, label='Feels Like')[0]
            temp_chart['data_lines'].append(feels_line)
            temp_chart['tooltip'].add_line(feels_line, 'Feels Like')
        
        # Update precipitation chart
        precip_chart = next(c for c in self.charts if c['name'] == 'precipitation')
        precip_bars = precip_chart['ax'].bar(timestamps, weather_data['precipitation'], 
                                           width=0.02, alpha=0.7, label='Precipitation')
        
        # Update wind chart
        wind_chart = next(c for c in self.charts if c['name'] == 'wind')
        wind_speed_line = wind_chart['ax'].plot(timestamps, weather_data['wind_speed'], 
                                              'g-', label='Wind Speed')[0]
        wind_chart['data_lines'].append(wind_speed_line)
        wind_chart['tooltip'].add_line(wind_speed_line, 'Wind Speed')
        
        # Add wind direction on secondary axis
        if 'wind_direction' in weather_data:
            wind_dir_scatter = wind_chart['ax2'].scatter(timestamps, weather_data['wind_direction'], 
                                                       c='blue', s=20, alpha=0.6, label='Direction')
            wind_chart['ax2'].set_ylabel('Wind Direction (°)', color='blue')
            wind_chart['ax2'].tick_params(axis='y', labelcolor='blue')
        
        # Update pressure chart
        pressure_chart = next(c for c in self.charts if c['name'] == 'pressure')
        pressure_line = pressure_chart['ax'].plot(timestamps, weather_data['pressure'], 
                                                'b-', label='Pressure')[0]
        pressure_chart['data_lines'].append(pressure_line)
        pressure_chart['tooltip'].add_line(pressure_line, 'Pressure')
        
        # Format all charts
        for chart in self.charts:
            chart['ax'].legend(loc='upper right')
            chart['ax'].grid(True, alpha=0.3)
            chart['ax'].margins(x=0.01)
            
            # Format x-axis
            chart['ax'].xaxis.set_major_formatter(
                matplotlib.dates.DateFormatter('%m/%d %H:%M')
            )
            chart['figure'].autofmt_xdate()
            
            # Apply theme
            self._apply_chart_theme(chart)
            
            chart['canvas'].draw()
    
    def _apply_chart_theme(self, chart):
        """Apply theme to individual chart."""
        if self.pref_manager:
            theme = self.pref_manager.get('display', 'theme', 'light')
            
            if theme == 'dark':
                chart['figure'].patch.set_facecolor('#1E1E1E')
                chart['ax'].set_facecolor('#2D2D2D')
                chart['ax'].tick_params(colors='white')
                chart['ax'].xaxis.label.set_color('white')
                chart['ax'].yaxis.label.set_color('white')
                chart['ax'].title.set_color('white')
                
                # Update grid
                chart['ax'].grid(True, alpha=0.2, color='gray')
            else:
                chart['figure'].patch.set_facecolor('white')
                chart['ax'].set_facecolor('white')
                chart['ax'].tick_params(colors='black')
                chart['ax'].xaxis.label.set_color('black')
                chart['ax'].yaxis.label.set_color('black')
                chart['ax'].title.set_color('black')
