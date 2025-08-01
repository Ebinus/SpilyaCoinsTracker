import tkinter as tk
import random
from datetime import datetime
import pyperclip

from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
import matplotlib.pyplot as plt

class CurrencyPriceApp:
    def __init__(self, root):
        self.root = root
        self.root.title("PAWScoin Tracker")
        self.root.geometry("600x900")

        self.price_history = []
        self.time_history = []
        self.current_price = None

        self.prng = random.Random()

        self.price_label = tk.Label(root, text="Цена 1 PAWSкоина: ? очков", font=("Arial", 20))
        self.price_label.pack(pady=10)

        self.timer_label = tk.Label(root, text="До обновления: 30 сек", font=("Arial", 14))
        self.timer_label.pack(pady=5)

        self.copy_button = tk.Button(root, text="📋 Копировать текущую цену", command=self.copy_current_price)
        self.copy_button.pack(pady=5)

        self.exit_button = tk.Button(root, text="❌ Завершить программу", command=self.root.destroy)
        self.exit_button.pack(pady=5)

        self.figure, self.ax = plt.subplots(figsize=(6, 3))
        self.figure.subplots_adjust(bottom=0.25)
        self.ax.set_title("История цен PAWScoin")
        self.ax.set_ylabel("Цена")
        self.ax.set_xlabel("Обновления", labelpad=15)

        self.canvas = FigureCanvasTkAgg(self.figure, master=root)
        self.canvas_widget = self.canvas.get_tk_widget()
        self.canvas_widget.pack(pady=10)

        self.scatter = None
        self.annotation = self.ax.annotate(
            "", xy=(0,0), xytext=(10,10), textcoords="offset points",
            bbox=dict(boxstyle="round", fc="w"),
            arrowprops=dict(arrowstyle="->")
        )
        self.annotation.set_visible(False)
        self.canvas.mpl_connect("motion_notify_event", self.on_hover)
        self.canvas.mpl_connect("button_press_event", self.on_click)

        self.live_fig, self.live_ax = plt.subplots(figsize=(6, 2))
        self.live_canvas = FigureCanvasTkAgg(self.live_fig, master=self.root)
        self.live_canvas_widget = self.live_canvas.get_tk_widget()
        self.live_canvas_widget.pack_forget()
        self.live_canvas.draw()

        self.root.bind('<o>', self.toggle_probability_chart)

        self.countdown = 12
        self.update_price()
        self.update_timer()

    def generate_weighted_price(self):
        r = self.prng.random()
        skewed_value = int((1 - r ** 0.5) * 100)
        return min(max(skewed_value, 0), 99)

    def calculate_next_probabilities(self):
        return {}

    def update_price(self):
        self.current_price = self.generate_weighted_price()
        now = datetime.now()
        self.price_label.config(text=f"Цена 1 PAWSкоина: {self.current_price} очков")

        self.price_history.append(self.current_price)
        self.time_history.append(now)

        self.ax.clear()
        self.ax.set_title("История цен PAWScoin")
        self.ax.set_ylabel("Цена")
        self.ax.set_ylim(0, 100)
        self.ax.set_xlim(0, max(10, len(self.price_history)))
        self.ax.set_xlabel("Обновления", labelpad=15)

        x = list(range(len(self.price_history)))
        y = self.price_history
        self.ax.plot(x, y, marker='o')
        self.scatter = self.ax.scatter(x, y)

        self.canvas.draw()
        self.update_live_probability_chart()
        self.countdown = 12

    def update_timer(self):
        if self.countdown <= 0:
            self.update_price()
        else:
            self.timer_label.config(text=f"До обновления: {self.countdown} сек")
            self.countdown -= 1
        self.root.after(1000, self.update_timer)

    def copy_current_price(self):
        if self.current_price is not None:
            now = datetime.now().strftime("%H:%M:%S")
            text = f"Цена на {now} - {self.current_price} очков"
            pyperclip.copy(text)

    def on_hover(self, event):
        if self.scatter:
            cont, ind = self.scatter.contains(event)
            if cont:
                idx = ind["ind"][0]
                x, y = idx, self.price_history[idx]
                time_str = self.time_history[idx].strftime("%H:%M:%S")
                self.annotation.xy = (x, y)
                self.annotation.set_text(f"{time_str}\n{y} очков")
                self.annotation.set_visible(True)
                self.canvas.draw_idle()
            else:
                if self.annotation.get_visible():
                    self.annotation.set_visible(False)
                    self.canvas.draw_idle()

    def on_click(self, event):
        if self.scatter:
            cont, ind = self.scatter.contains(event)
            if cont:
                idx = ind["ind"][0]
                time_str = self.time_history[idx].strftime("%H:%M:%S")
                value = self.price_history[idx]
                text = f"Цена на {time_str} - {value} очков"
                pyperclip.copy(text)

    def update_live_probability_chart(self):
        simulated = [int((1 - self.prng.random() ** 0.5) * 100) for _ in range(100000)]

        bins = [0]*6
        for v in simulated:
            if v <= 15: bins[0] += 1
            elif v <= 45: bins[1] += 1
            elif v <= 68: bins[2] += 1
            elif v <= 85: bins[3] += 1
            elif v <= 90: bins[4] += 1
            else: bins[5] += 1

        total = sum(bins)
        probs = [(b / total) * 100 for b in bins]

        ranges = ["0–15", "16–45", "46–68", "69–85", "86–90", "91–99"]
        colors = ["#a3e1a3", "#b5d3e7", "#f6d58e", "#f3a683", "#f78fb3", "#cf6a87"]

        self.live_ax.clear()
        bars = self.live_ax.bar(ranges, probs, color=colors)
        self.live_ax.set_title("Шансы на следующее значение")
        self.live_ax.set_ylabel("% вероятности")
        self.live_ax.set_ylim(0, max(probs) + 5)

        for bar, prob in zip(bars, probs):
            height = bar.get_height()
            self.live_ax.text(bar.get_x() + bar.get_width()/2.0, height + 0.5, f"{prob:.2f}%", ha='center', va='bottom')

        self.live_canvas.draw()

    def toggle_probability_chart(self, event):
        widget = self.live_canvas_widget
        if widget.winfo_ismapped():
            widget.pack_forget()
        else:
            widget.pack(pady=10)

if __name__ == "__main__":
    root = tk.Tk()
    app = CurrencyPriceApp(root)
    root.mainloop()
