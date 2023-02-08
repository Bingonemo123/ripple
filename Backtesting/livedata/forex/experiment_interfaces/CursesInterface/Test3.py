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
        plt.plot_size(cols -1 , lines)
        plt.colorless()
        plt.show()
    PlotFile.seek(0)
    w = PlotFile.readlines()
    return w


def main (stdscr):
    curses.start_color()
    w = draw_plot(curses.COLS, curses.LINES)
    k = 0
    for i in w:
        for c in i:
            stdscr.addstr(c)
        k += 1
    stdscr.refresh()
    curses.napms(3000)

curses.wrapper(main)

