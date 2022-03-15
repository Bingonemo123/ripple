import plotext as plt
from contextlib import redirect_stdout
import io
import curses

def draw_plot(cols, lines):
    PlotFile = io.StringIO()
    with redirect_stdout(PlotFile):
        y = plt.sin() # sinusoidal signal 
        plt.plot(y )
        plt.title("Scatter Plot")
        plt.plot_size(cols -1 , lines-1)
        plt.colorless()
        plt.show()
    PlotFile.seek(0)
    w = PlotFile.readlines()
    return w


def main (stdscr):
    curses.start_color()
    winr = curses.newwin(30, 30, 30, 30)
    w = draw_plot(30, 30)
    k = 0
    for i in w:
        for c in i:
            winr.addstr(c)
        k += 1
    winr.refresh()
    curses.napms(3000)

curses.wrapper(main)

