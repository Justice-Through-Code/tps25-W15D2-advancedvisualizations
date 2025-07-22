import tkinter as tk
from tkinter import ttk
import matplotlib
matplotlib.use('TkAgg')
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg, NavigationToolbar2Tk
from matplotlib.figure import Figure
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import numpy as np
from datetime import datetime, timedelta
import random
from clickerinteractions import ClickInteraction
from hovertooltip import HoverTooltip
from interactiveoverlays import WeatherOverlay
from matplotlibenvi import InteractiveWeatherChart
from multichartdisplay import SynchronizedWeatherDashboard
from smoothanimations import AnimatedWeatherChart
from visualthemes import WeatherChartTheme


class DummyPreferenceManager:
    def __init__(self):
        self.preferences = {
            'display': {'theme': 'dark'}  # 'light', 'seaborn', 'minimalist'
        }

    def get(self, category, key, default=None):
        return self.preferences.get(category, {}).get(key, default)

# ----- Generate Sample Weather Data -----
def generate_sample_weather_data(n=120):
    now = datetime.now()
    timestamps = [now - timedelta(hours=i) for i in reversed(range(n))]
    return {
        'timestamps': mdates.date2num(timestamps),
        'temperature': [20 + np.sin(i / 10) * 5 + random.uniform(-1, 1) for i in range(n)],
        'humidity': [50 + np.cos(i / 15) * 10 + random.uniform(-2, 2) for i in range(n)],
        'pressure': [1013 + np.sin(i / 30) * 3 + random.uniform(-0.5, 0.5) for i in range(n)],
        'precipitation': [random.uniform(0, 3) if random.random() < 0.3 else 0 for _ in range(n)],
        'wind_speed': [5 + random.uniform(0, 5) for _ in range(n)],
        'wind_direction': [random.uniform(0, 360) for _ in range(n)],
        'feels_like': [19 + np.sin(i / 11) * 5 for i in range(n)]
    }

# ----- Main Application -----
class WeatherApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Weather Visualizer Pro")
        self.geometry("1280x900")
        self.pref_manager = DummyPreferenceManager()

        # Create notebook tabs
        tabs = ttk.Notebook(self)
        tabs.pack(fill=tk.BOTH, expand=True)

        # Tab 1: Synchronized dashboard
        dashboard = SynchronizedWeatherDashboard(tabs, preference_manager=self.pref_manager)
        tabs.add(dashboard, text="Dashboard")

        # Tab 2: Animated live chart
        animated_tab = ttk.Frame(tabs)
        tabs.add(animated_tab, text="Live Animation")
        self._init_animated_chart(animated_tab)

        # Tab 3: Interactive chart
        interactive_tab = ttk.Frame(tabs)
        tabs.add(interactive_tab, text="Interactive Chart")
        self._init_interactive_chart(interactive_tab)

        # Load static data for dashboard
        weather_data = generate_sample_weather_data(120)
        dashboard.update_data(weather_data)

    def _init_animated_chart(self, parent):
        fig = Figure(figsize=(12, 4), dpi=100)
        ax = fig.add_subplot(111)
        canvas = FigureCanvasTkAgg(fig, parent)
        canvas.get_tk_widget().pack(fill=tk.BOTH, expand=True)
        NavigationToolbar2Tk(canvas, parent).update()

        animated = AnimatedWeatherChart(fig, ax)
        animated.add_series("Temperature", color='orange')
        animated.add_series("Humidity", color='blue')
        animated.start_animation(update_interval=1000)

        def stream_data():
            now = mdates.date2num(datetime.now())
            animated.add_data_point(now, {
                "Temperature": 20 + random.uniform(-2, 2),
                "Humidity": 50 + random.uniform(-5, 5)
            })
            self.after(1000, stream_data)

        stream_data()

    def _init_interactive_chart(self, parent):
        chart = InteractiveWeatherChart(parent, preference_manager=self.pref_manager)
        chart.pack(fill=tk.BOTH, expand=True)

        # Load sample data
        data = generate_sample_weather_data(120)
        chart.data['timestamps'] = data['timestamps']
        chart.data['temperature'] = data['temperature']
        chart.data['humidity'] = data['humidity']
        chart.data['pressure'] = data['pressure']
        chart.plot_data()  # You need to implement this method to draw initial lines

        # Example overlays
        overlay = WeatherOverlay(chart.ax)
        overlay.add_temperature_threshold(30, "High Temp")
        overlay.add_time_range_highlight(data['timestamps'][30], data['timestamps'][50], "Hot Zone")

        # Tooltip + click interaction
        tooltip = HoverTooltip(chart.ax, chart.canvas)
        line = chart.ax.plot(data['timestamps'], data['temperature'], color='red', label='Temp')[0]
        tooltip.add_line(line, 'Temperature')
        clicker = ClickInteraction(chart.ax, chart.canvas, callback=lambda evt, data: print(f"{evt}: {data}"))
        chart.canvas.mpl_connect("button_press_event", lambda e: clicker.handle_click(e, [
            {'x': np.array(data['timestamps']), 'y': np.array(data['temperature']), 'label': 'Temp'}
        ]))

# ----- Run App -----
if __name__ == "__main__":
    app = WeatherApp()
    app.mainloop()