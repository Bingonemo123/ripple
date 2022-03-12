import curses
import plotext as plt
import io
import sys
from contextlib import redirect_stdout


PlotFile = io.StringIO()
stdscr = curses.initscr()
curses.start_color()
curses.use_default_colors()

with redirect_stdout(PlotFile):
    y = plt.sin() # sinusoidal signal 
    plt.scatter(y, marker = "dot")
    plt.plot_size(121, 34)
    plt.title("Scatter Plot")
    plt.show()
PlotFile.flush()
PlotFile.seek(0)
print(stdscr.getmaxyx())
k = 0
for line in PlotFile:
    stdscr.addstr(k, 0, "╔═╗║║╚═╝╟─╢")
    k += 1
stdscr.refresh()
curses.napms(20000)
curses.endwin()
