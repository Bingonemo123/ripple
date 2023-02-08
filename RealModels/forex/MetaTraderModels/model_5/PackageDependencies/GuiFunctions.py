import curses
import io
import time
from contextlib import redirect_stdout
from datetime import datetime, timedelta

import plotext as plt


class CursesUtilities():
    def __init__(self, lu):
        self.lu = lu
        plt.colorless()
        plt.xlabel('Time')
        self.last_pbar_update = self.lu.strd
        self.stdscr = curses.initscr()
        self.progressbarwin = curses.newwin(3, curses.COLS, 0, 0)
        self.progressbarwin.box()
        self.infowin = curses.newwin(curses.LINES - 6, curses.COLS//4, 3, 0)
        self.statuswin = curses.newwin(3, curses.COLS, curses.LINES-3, 0)
        self.graphwin = curses.newwin(curses.LINES - 6, curses.COLS - curses.COLS//4, 3, curses.COLS//4)
        self.curses = curses

    
    def draw_plot(self, cols, lines, f):
        PlotFile = io.StringIO()
        with redirect_stdout(PlotFile):
            plt.clp()
            plt.clc()
            plt.cls()
            plt.plot_size(lines -1 , cols -1)
            y = [i[self.lu.crpohlc] for i in self.lu.cd[f][-100:]]
            plt.plot(y)
            plt.title(f)
            plt.show()
        PlotFile.seek(0)
        w = PlotFile.readlines()
        return w

    def log_display(self):
        self.progressbarwin.clear()
        self.progressbarwin.addstr(1, 1, 'Progress: ' + str(self.lu.iteration))
        self.progressbarwin.addstr(' Drawing Time: ' + str(self.lu.drawing_time))
        self.progressbarwin.refresh()
        self.infowin.clear()
        self.infowin.box()
        self.infowin.addstr(1, 1, f'Current Balance {self.lu.curr_balance:,.2f}')
        self.infowin.addstr(2, 1, f'Safe Balance {self.lu.safe_balance:,.2f}')
        self.infowin.addstr(3, 1, f'Margin Balance {self.lu.margin_balance:,.2f}')
        self.infowin.addstr(4, 1, f'Free Balance {self.lu.free_balance:,.2f}')
        self.infowin.addstr(5, 1, f'Total Profit {self.lu.tp:,.2f}')

        maxcheckvars = [self.lu.curr_balance, self.lu.safe_balance, self.lu.margin_balance, self.lu.free_balance, len(self.lu.ap)]
        for x in range(len(maxcheckvars)):
            if self.lu.maximum_var[x] < maxcheckvars[x]:
                self.lu.maximum_var[x] = maxcheckvars[x]

        mincheckvars = [self.lu.curr_balance, self.lu.safe_balance, self.lu.margin_balance, self.lu.free_balance]
        for x in range(len(mincheckvars)):
            if self.lu.minimum_var[x] > mincheckvars[x]:
                self.lu.minimum_var[x] = mincheckvars[x]

        self.infowin.addstr(6, 1, f'Max Current Balance {self.lu.maximum_var[0]:,.2f}')
        self.infowin.addstr(7, 1, f'Max Safe Balance {self.lu.maximum_var[1]:,.2f}')
        self.infowin.addstr(8, 1, f'Max Margin Balance {self.lu.maximum_var[2]:,.2f}')
        self.infowin.addstr(9, 1, f'Max Free Balance {self.lu.maximum_var[3]:,.2f}')
        self.infowin.addstr(10, 1, f'Min Current Balance {self.lu.minimum_var[0]:,.2f}')
        self.infowin.addstr(11, 1, f'Min Safe Balance {self.lu.minimum_var[1]:,.2f}')
        self.infowin.addstr(12, 1, f'Min Margin Balance {self.lu.minimum_var[2]:,.2f}')
        self.infowin.addstr(13, 1, f'Min Free Balance {self.lu.minimum_var[3]:,.2f}')
        
        self.infowin.addstr(15, 1, f'Active Positions {len(self.lu.ap)}')
        self.infowin.addstr(16, 1, f'Total Positions {len(self.lu.position_history)}')
        self.infowin.addstr(17, 1, f'AutoClosed {self.lu.autoclosed}')
        self.infowin.addstr(18, 1, f'MarginClosed {self.lu.marginclosed}')
        self.infowin.addstr(19, 1, f'CutoutClosed {self.lu.cutoutclosed}')
        self.infowin.addstr(20, 1, f'Total Closed {self.lu.autoclosed + self.lu.marginclosed + self.lu.cutoutclosed}')
        self.infowin.addstr(21, 1, f'Max Active Positions {self.lu.maximum_var[4]}')

        self.infowin.addstr(23, 1, f'Active Desk {len(self.lu.actdesk)}')
        self.infowin.addstr(24, 1, f'Possible Symbols {len(self.lu.Filter)}')

        self.infowin.addstr(25, 1, f'Cutout Index {self.lu.cutoutindx}')

        self.z = 0
        for f in self.lu.trdesk:
            self.infowin.addstr(27 + self.z, 1, f'{f} {self.lu.crp.get(f, "NaN"):<20}') # prices
            if f in [i[1] for i in self.lu.ap]:
                self.infowin.addstr('x')
            self.z += 1

        for f in self.lu.trdesk:
            self.infowin.addstr(27 + self.z, 1, f'{f} ')
            prmeans = self.lu.means_data.get(f, self.lu.lastmean.get(f, ["NaN"]))
            if f in self.lu.means_data:
                self.lu.lastmean[f] = self.lu.means_data[f]
            
            if prmeans[0] == "NaN":
                self.infowin.addstr(f'{prmeans[0]}')
            else:
                for x in prmeans:
                    self.infowin.addstr(f'{x:10.4f} ')
            self.z += 1

        if len(self.lu.position_history) > 0:
            selected_position = self.lu.position_history.get(max([x for x in self.lu.position_history if len(self.lu.position_history[x]) > 10], default=None), False)
            if selected_position:
                self.z += 1
                self.infowin.addstr(27 + self.z, 1, f'Latest Closed Position')
                self.z += 1 
                for d in selected_position:
                    selected_data = selected_position[d]
                    if isinstance(selected_data, float):
                        selected_data = f'{selected_data:,}'
                    self.infowin.addstr(27 + self.z, 1, f'{d:{(curses.COLS//8) -3 }}  {f"{selected_data}":<{(curses.COLS//8) -3}}')
                    self.z += 1
        


        if self.lu.foundmark:
            self.infowin.addstr(27 + self.z, 1, f'Foundmark {self.lu.foundmark[1][0]} {self.lu.foundmark[0]}')
        else:
            self.infowin.addstr(27 + self.z, 1, f'Foundmark None')
        self.z += 1
        self.infowin.addstr(27 + self.z, 1, f'Foundmark {self.lu.last_foundmark_run} [{self.lu.last_foundmark_iter}]')
        self.infowin.refresh()
        # self.pbar.write(f'Current Balance: {curr_balance}, Safe Balance: {safe_balance}, Total Profit: {tp}')
        ### draw the graph
    
        self.graphwin.clear()
        w = self.draw_plot(curses.LINES - 6, curses.COLS - curses.COLS//4, 'EURUSD')
        
        k = 0
        for i in w:
            for c in i:
                self.graphwin.addstr(c)
            k += 1
        self.graphwin.refresh()
        self.lu.last_graph_update = datetime.now()

    def flow(self, lu):
        self.lu = lu
        self.log_display()
