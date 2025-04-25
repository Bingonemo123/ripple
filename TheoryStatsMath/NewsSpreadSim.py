import taichi as ti
import numpy as np

from datetime import timedelta
import time

# Initialize Taichi to use GPU
ti.init(arch=ti.gpu, random_seed=42)


print("Backend arch:", ti.cfg.arch)
# Get screen resolution (you may want to adjust this)
width, height = 1279, 719

def format_timedelta(td):
    days = td.days
    total_seconds = td.seconds  # this excludes full days
    hours, remainder = divmod(total_seconds, 3600)
    minutes, seconds = divmod(remainder, 60)

    if days > 0:
        return f"{days}d {hours:02}:{minutes:02}:{seconds:02}"
    else:
        return f"{hours:02}:{minutes:02}:{seconds:02}"


# Define a time-dependent rate function
def rate_function(minute_of_day):
    hour = (minute_of_day // 60) % 24
    if 9 <= hour < 17:
        return 0.005  # Higher probability during business hours
    elif 7 <= hour < 9 or 17 <= hour < 20:
        return 0.002  # Moderate probability during early morning and evening
    else:
        return 0.0005  # Lower probability during night


def sample_unique_pairs(x, y, n):
    assert n <= x * y, "Not enough unique pairs available!"

    # Step 1: Sample n unique flat indices from range [0, x*y)
    flat_indices = np.random.choice(x * y, size=n, replace=False)

    # Step 2: Convert flat indices to 2D (i, j) pairs
    i_vals, j_vals = np.unravel_index(flat_indices, (x, y))

    return i_vals.astype(np.int32), j_vals.astype(np.int32)


@ti.data_oriented
class NewsSpreadSimulation:
    def __init__(self):
        # Create fields to represent agent states
        self.agents = ti.field(dtype=ti.f32, shape=(width, height))
        self.agents_new = ti.field(dtype=ti.f32, shape=(width, height))
        self.fade = 0.8
        
        # Visualization
        self.pixels = ti.field(dtype=ti.f32, shape=(width, height, 3))
            
    @ti.kernel
    def update(self, x: ti.template(), y: ti.template()):
        # Update simulation - spread information to neighbors

        for i in range(x.shape[0]):
            # Use passed-in values
            xi = x[i]
            yi = y[i]

            self.agents[xi, yi] = 1
    
    @ti.kernel
    def render(self):
        # Convert agent states to colors
        for i, j in self.agents:
            if self.agents[i, j] == 1:
                # Knowers are white
                self.pixels[i, j, 0] = 255
                self.pixels[i, j, 1] = 255
                self.pixels[i, j, 2] = 255
            else:
                # Others are black
                self.pixels[i, j, 0] = ti.u8(0)
                self.pixels[i, j, 1] = ti.u8(0)
                self.pixels[i, j, 2] = ti.u8(0)

    def run(self):
        window = ti.ui.Window("News Spread Simulation", (width, height))
        canvas = window.get_canvas()
        gui = window.get_gui()

        elapsed = timedelta(0)  # Start with 0 time elapsed
        alpha = 5  # expected numbner of agents being impacted
        total_agents = width * height

        while window.running:
            # Update simulation
            rate = rate_function(elapsed.total_seconds() // 60)

            if np.random.rand() < rate:
                tpoint1 = time.time()
                per_of_impct_agnt = np.random.beta(alpha, total_agents - alpha)
                numb_of_impct_agnt = int(total_agents * per_of_impct_agnt)
                i_arr, j_arr = sample_unique_pairs(width, height, 
                                                   numb_of_impct_agnt)
                
                tpoint4 = time.time()
                
                # Convert to Taichi fields
                ti_i = ti.field(dtype=ti.i32, shape=numb_of_impct_agnt)
                ti_j = ti.field(dtype=ti.i32, shape=numb_of_impct_agnt)
                ti_i.from_numpy(i_arr)
                ti_j.from_numpy(j_arr)

                tpoint2 = time.time()

                self.update(ti_i, ti_j)

                tpoint3 = time.time()

                print("choice", tpoint2 - tpoint1, "hits", numb_of_impct_agnt)
                print("update", tpoint3 - tpoint2)
                print("field", tpoint2 - tpoint4)
            
            # # Copy new state to current
            # self.agents.copy_from(self.agents_new)

            # # Render
            self.render()
            canvas.set_image(self.pixels)

            elapsed += timedelta(minutes=1)  # Increment by 1 minute
            time_str = format_timedelta(elapsed)  # E.g., 1d 14:32:01

            with gui.sub_window("Stats", 0.05, 0.1, 0.2, 0.15) as w:
                w.text(time_str, color=(1.0, 0.0, 0.0))
                w.text(f"rate: {rate}")
                w.text(f"total agents: {total_agents}")

            # Show FPS
            window.show()
            
            # Exit on ESC
            if window.get_event(ti.ui.PRESS):
                if window.event.key == ti.ui.ESCAPE:
                    break

# Run the simulation
sim = NewsSpreadSimulation()
sim.run()
