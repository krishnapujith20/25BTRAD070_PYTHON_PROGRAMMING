import csv
import os
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# 📥 Same data file as before (keep transit_data.py in the same folder)
from transit_data import TRANSIT_GRAPH, RUSH_HOURS, ROAD_VEHICLES, CONGESTION_MULTIPLIER


# ==========================================
# MODULE 1: THE TRAVEL NETWORK LOADER
# ==========================================
class TransitNetwork:
    def __init__(self):
        self.graph = TRANSIT_GRAPH

    def get_locations(self):
        locations = set(self.graph.keys())
        for destinations in self.graph.values():
            locations.update(destinations.keys())
        return sorted(locations)

    def get_routes(self, origin, destination):
        if origin in self.graph and destination in self.graph[origin]:
            return self.graph[origin][destination]
        return []


# ==========================================
# MODULE 2: DATABASE PERSISTENCE ENGINE
# ==========================================
class LogEngine:
    def __init__(self, filename="commute_history.csv"):
        self.filename = filename
        if not os.path.exists(self.filename):
            with open(self.filename, "w", newline="") as f:
                writer = csv.writer(f)
                writer.writerow(["Timestamp", "Origin", "Destination", "Mode", "Duration_Mins", "Cost_INR"])

    def log_commute(self, origin, destination, mode, duration, cost):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        with open(self.filename, "a", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([timestamp, origin, destination, mode, duration, cost])
        return True

    def read_all_logs(self):
        logs = []
        if not os.path.exists(self.filename):
            return logs
        with open(self.filename, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                logs.append({
                    "timestamp": row["Timestamp"], "origin": row["Origin"], "destination": row["Destination"],
                    "mode": row["Mode"], "duration": float(row["Duration_Mins"]), "cost": float(row["Cost_INR"])
                })
        return logs


# ==========================================
# MODULE 3: STATISTICAL ANALYTICS ENGINE
# ==========================================
class CommuteAnalytics:
    @staticmethod
    def generate_dashboard(logs):
        if not logs:
            return {"total_trips": 0, "total_spend": 0.0, "total_time": 0.0, "popular_mode": "None"}

        total_spend = sum(log["cost"] for log in logs)
        total_time = sum(log["duration"] for log in logs)

        mode_counts = {}
        for log in logs:
            mode_counts[log["mode"]] = mode_counts.get(log["mode"], 0) + 1
        popular_mode = max(mode_counts, key=mode_counts.get) if mode_counts else "None"

        return {
            "total_trips": len(logs), "total_spend": total_spend,
            "total_time": total_time, "popular_mode": popular_mode
        }


# ==========================================
# MODULE 4: INTELLIGENT ROUTING OPTIMIZER
# ==========================================
class RouteOptimizer:
    def __init__(self, network):
        self.network = network

    # NEW: returns ALL options (traffic adjusted) so the GUI can show a table
    def evaluate_options(self, origin, destination, departure_hour):
        routes = self.network.get_routes(origin, destination)
        is_peak = any(start <= departure_hour <= end for start, end in RUSH_HOURS)
        options = []
        for route in routes:
            adjusted_time = route["time"]
            if is_peak and route["mode"] in ROAD_VEHICLES:
                adjusted_time = int(route["time"] * CONGESTION_MULTIPLIER)
            options.append({
                "mode": route["mode"], "time": adjusted_time,
                "cost": route["cost"], "carbon": route["carbon"]
            })
        return options, is_peak

    def pick_best(self, options, priority="Fastest"):
        if priority == "Cheapest":
            return min(options, key=lambda x: x["cost"])
        elif priority == "Eco-Friendly":
            return min(options, key=lambda x: x["carbon"])
        return min(options, key=lambda x: x["time"])

    def calculate_best_option(self, origin, destination, departure_hour, priority="Fastest"):
        options, _ = self.evaluate_options(origin, destination, departure_hour)
        if not options:
            return None
        return self.pick_best(options, priority)


# ==========================================
# MODULE 5: GRAPHICAL USER INTERFACE (tkinter)
# ==========================================
class TravelApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("CUFFINGSEASON: Daily Travel Optimizer")
        self.geometry("720x520")
        self.minsize(640, 480)

        # Reuse the same backend objects as the console version
        self.network = TransitNetwork()
        self.db = LogEngine()
        self.optimizer = RouteOptimizer(self.network)

        ttk.Label(self, text="🚌 CUFFINGSEASON: DAILY TRAVEL OPTIMIZER",
                  font=("Segoe UI", 14, "bold")).pack(pady=10)

        self.tabs = ttk.Notebook(self)
        self.tabs.pack(fill="both", expand=True, padx=10, pady=(0, 10))

        self.build_route_tab()
        self.build_log_tab()
        self.build_dashboard_tab()

        # Refresh the dashboard whenever its tab is opened
        self.tabs.bind("<<NotebookTabChanged>>", self.on_tab_change)

    # ---------- TAB 1: Find best route ----------
    def build_route_tab(self):
        tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(tab, text="Find Best Route")
        locations = self.network.get_locations()

        form = ttk.Frame(tab)
        form.pack(fill="x")

        ttk.Label(form, text="Origin:").grid(row=0, column=0, sticky="w", pady=4)
        self.origin_var = tk.StringVar(value="Hostel_Block")
        ttk.Combobox(form, textvariable=self.origin_var, values=locations,
                     state="readonly", width=22).grid(row=0, column=1, padx=8)

        ttk.Label(form, text="Destination:").grid(row=0, column=2, sticky="w")
        self.dest_var = tk.StringVar(value="Campus_Gate")
        ttk.Combobox(form, textvariable=self.dest_var, values=locations,
                     state="readonly", width=22).grid(row=0, column=3, padx=8)

        ttk.Label(form, text="Departure hour (0-23):").grid(row=1, column=0, sticky="w", pady=4)
        self.hour_var = tk.IntVar(value=9)
        ttk.Spinbox(form, from_=0, to=23, textvariable=self.hour_var, width=6).grid(row=1, column=1, sticky="w", padx=8)

        ttk.Label(form, text="Priority:").grid(row=1, column=2, sticky="w")
        self.priority_var = tk.StringVar(value="Fastest")
        ttk.Combobox(form, textvariable=self.priority_var,
                     values=["Fastest", "Cheapest", "Eco-Friendly"],
                     state="readonly", width=22).grid(row=1, column=3, padx=8)

        ttk.Button(tab, text="Find Best Route", command=self.find_route).pack(pady=10)

        # Table with every option
        cols = ("mode", "time", "cost", "carbon")
        self.route_table = ttk.Treeview(tab, columns=cols, show="headings", height=5)
        for col, title in zip(cols, ["Mode", "Time (min)", "Cost (₹)", "Carbon (kg)"]):
            self.route_table.heading(col, text=title)
            self.route_table.column(col, anchor="center", width=130)
        self.route_table.tag_configure("best", background="#c8f7c5", font=("Segoe UI", 9, "bold"))
        self.route_table.pack(fill="x")

        self.route_result = ttk.Label(tab, text="", font=("Segoe UI", 11), justify="left")
        self.route_result.pack(pady=10, anchor="w")

    def find_route(self):
        try:
            hour = int(self.hour_var.get())
            if not 0 <= hour <= 23:
                raise ValueError
        except (ValueError, tk.TclError):
            messagebox.showerror("Invalid input", "Departure hour must be a number from 0 to 23.")
            return

        origin, dest = self.origin_var.get(), self.dest_var.get()
        priority = self.priority_var.get()

        self.route_table.delete(*self.route_table.get_children())
        options, is_peak = self.optimizer.evaluate_options(origin, dest, hour)

        if not options:
            self.route_result.config(text="❌ No direct mapping found between those hubs.")
            return

        best = self.optimizer.pick_best(options, priority)
        for opt in options:
            tag = ("best",) if opt is best else ()
            self.route_table.insert("", "end", tags=tag,
                                    values=(opt["mode"], opt["time"], opt["cost"], opt["carbon"]))

        traffic = "🚦 Rush hour: road vehicles slowed down" if is_peak else "✅ Normal traffic"
        self.route_result.config(text=(
            f"💡 RECOMMENDATION: Travel via {best['mode']}\n"
            f"⏱️ Expected duration (traffic adjusted): {best['time']} mins\n"
            f"💰 Out-of-pocket cost: ₹{best['cost']}\n"
            f"{traffic}"))

    # ---------- TAB 2: Log a trip ----------
    def build_log_tab(self):
        tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(tab, text="Log a Trip")

        self.log_vars = {}
        fields = [("Starting point", "origin"), ("Destination", "dest"),
                  ("Vehicle mode used", "mode"),
                  ("Actual duration (minutes)", "time"), ("Total fare cost (INR)", "cost")]
        for i, (label, key) in enumerate(fields):
            ttk.Label(tab, text=label + ":").grid(row=i, column=0, sticky="w", pady=6)
            var = tk.StringVar()
            ttk.Entry(tab, textvariable=var, width=30).grid(row=i, column=1, padx=10)
            self.log_vars[key] = var

        ttk.Button(tab, text="Save Trip", command=self.save_trip).grid(row=len(fields), column=0, columnspan=2, pady=14)

    def save_trip(self):
        v = {k: var.get().strip() for k, var in self.log_vars.items()}
        if not (v["origin"] and v["dest"] and v["mode"]):
            messagebox.showerror("Missing data", "Please fill in origin, destination and mode.")
            return
        try:
            t = float(v["time"])
            c = float(v["cost"])
        except ValueError:
            messagebox.showerror("Invalid input", "Duration and cost must be numbers.")
            return
        self.db.log_commute(v["origin"], v["dest"], v["mode"], t, c)
        messagebox.showinfo("Saved", "✅ Trip recorded in the database ledger.")
        for var in self.log_vars.values():
            var.set("")

    # ---------- TAB 3: Dashboard ----------
    def build_dashboard_tab(self):
        tab = ttk.Frame(self.tabs, padding=12)
        self.tabs.add(tab, text="Analytics Dashboard")

        self.stat_labels = {}
        stats = ttk.Frame(tab)
        stats.pack(fill="x")
        for i, (key, title) in enumerate([("total_trips", "Total commutes"), ("total_spend", "Cash spent"),
                                          ("total_time", "Time in transit"), ("popular_mode", "Top mode")]):
            box = ttk.LabelFrame(stats, text=title, padding=8)
            box.grid(row=0, column=i, padx=6, sticky="nsew")
            stats.columnconfigure(i, weight=1)
            lbl = ttk.Label(box, text="-", font=("Segoe UI", 13, "bold"))
            lbl.pack()
            self.stat_labels[key] = lbl

        cols = ("timestamp", "origin", "destination", "mode", "duration", "cost")
        self.history = ttk.Treeview(tab, columns=cols, show="headings", height=10)
        for col in cols:
            self.history.heading(col, text=col.title())
            self.history.column(col, anchor="center", width=100)
        self.history.pack(fill="both", expand=True, pady=12)

    def refresh_dashboard(self):
        logs = self.db.read_all_logs()
        s = CommuteAnalytics.generate_dashboard(logs)
        self.stat_labels["total_trips"].config(text=str(s["total_trips"]))
        self.stat_labels["total_spend"].config(text=f"₹{s['total_spend']}")
        self.stat_labels["total_time"].config(text=f"{s['total_time']} min")
        self.stat_labels["popular_mode"].config(text=s["popular_mode"])

        self.history.delete(*self.history.get_children())
        for log in reversed(logs):
            self.history.insert("", "end", values=(log["timestamp"], log["origin"], log["destination"],
                                                   log["mode"], log["duration"], log["cost"]))

    def on_tab_change(self, event):
        if self.tabs.tab(self.tabs.select(), "text") == "Analytics Dashboard":
            self.refresh_dashboard()


if __name__ == "__main__":
    TravelApp().mainloop()