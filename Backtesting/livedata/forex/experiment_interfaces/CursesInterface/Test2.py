import plotext as plt
from contextlib import redirect_stdout
import io
import curses
PlotFile = io.StringIO()


with redirect_stdout(PlotFile):
    y = plt.sin() # sinusoidal signal 
    plt.scatter(y, marker='dot', )
    plt.title("Scatter Plot")
    plt.plot_size(80, 30)
    plt.colorless()
    plt.show()
PlotFile.seek(0)
w = PlotFile.readlines()
allchar = []
vischar = []
dechar = []
bychar = []
def main (stdscr):
    curses.start_color()
    k = 0
    for i in w:
        for c in i:
            if ord(c) not in allchar:
                allchar.append(ord(c))
                vischar.append(c)
                dechar.append(c.encode('utf-8'))
                bychar.append(bytes(dechar[-1]))
            stdscr.addstr(c)
        print(i)
        k += 1
    stdscr.refresh()
    curses.napms(3000)

curses.wrapper(main)


print(allchar)
print(vischar)
print(dechar)
print(bychar)


