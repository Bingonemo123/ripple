import curses
import io
import time
from contextlib import redirect_stdout
from datetime import datetime, timedelta

import plotext as plt
import tqdm

from PackageDependencies.Constans import *


class CursesUtilities():
    def __init__(self):
        self.fake_file = io.StringIO()
        plt.colorless()
        plt.xlabel('Time')
        self.last_pbar_update = strd

    def unwrap_main(self, stdscr):
        self.stdscr = stdscr
        self.progressbarwin = curses.newwin(3, curses.COLS, 0, 0)
        self.progressbarwin.box()
        self.infowin = curses.newwin(curses.LINES - 6, curses.COLS//4, 3, 0)
        self.statuswin = curses.newwin(3, curses.COLS, curses.LINES-3, 0)
        self.graphwin = curses.newwin(curses.LINES - 6, curses.COLS - curses.COLS//4, 3, curses.COLS//4)

        self.pbar = tqdm.tqdm(total=int((datetime.utcnow().replace(tzinfo=timezone) - strd).total_seconds()/60), file=self.fake_file, ncols = curses.COLS-2)
        self.pbar.set_description('│')

    def refresh_status(self, status):
        self.statuswin.clear()
        self.statuswin.box()
        self.statuswin.addstr(1, 1, status)
        self.statuswin.refresh()
    
    def draw_plot(cols, lines, f):
        PlotFile = io.StringIO()
        with redirect_stdout(PlotFile):
            plt.clp()
            plt.clc()
            plt.cls()
            plt.plot_size(lines -1 , cols -1)
            y = [i[crpohlc] for i in cd[f][-100:]]
            plt.plot(y)
            plt.title(f)
            plt.show()
        PlotFile.seek(0)
        w = PlotFile.readlines()
        return w

    def log_display(self):
        self.pbar.update(int((currd - self.last_pbar_update).total_seconds()/60))
        self.last_pbar_update = currd
        self.pbar.set_description(f'│ {currd}')
        fake_file.flush()
        fake_file.seek(0)
        self.progressbarwin.addstr(1, 2, fake_file.readline())
        self.progressbarwin.refresh()

        self.infowin.clear()
        self.infowin.box()
        self.infowin.addstr(1, 1, f'Current Balance {curr_balance:,.2f}')
        self.infowin.addstr(2, 1, f'Safe Balance {safe_balance:,.2f}')
        self.infowin.addstr(3, 1, f'Margin Balance {margin_balance:,.2f}')
        self.infowin.addstr(4, 1, f'Free Balance {free_balance:,.2f}')
        self.infowin.addstr(5, 1, f'Total Profit {tp:,.2f}')

        maxcheckvars = [curr_balance, safe_balance, margin_balance, free_balance, len(ap)]
        for x in range(len(maxcheckvars)):
            if maximum_var[x] < maxcheckvars[x]:
                maximum_var[x] = maxcheckvars[x]

        mincheckvars = [curr_balance, safe_balance, margin_balance, free_balance]
        for x in range(len(mincheckvars)):
            if minimum_var[x] > mincheckvars[x]:
                minimum_var[x] = mincheckvars[x]

        self.infowin.addstr(6, 1, f'Max Current Balance {maximum_var[0]:,.2f}')
        self.infowin.addstr(7, 1, f'Max Safe Balance {maximum_var[1]:,.2f}')
        self.infowin.addstr(8, 1, f'Max Margin Balance {maximum_var[2]:,.2f}')
        self.infowin.addstr(9, 1, f'Max Free Balance {maximum_var[3]:,.2f}')
        self.infowin.addstr(10, 1, f'Min Current Balance {minimum_var[0]:,.2f}')
        self.infowin.addstr(11, 1, f'Min Safe Balance {minimum_var[1]:,.2f}')
        self.infowin.addstr(12, 1, f'Min Margin Balance {minimum_var[2]:,.2f}')
        self.infowin.addstr(13, 1, f'Min Free Balance {minimum_var[3]:,.2f}')
        
        self.infowin.addstr(15, 1, f'Active Positions {len(ap)}')
        self.infowin.addstr(16, 1, f'Total Positions {len(position_history)}')
        self.infowin.addstr(17, 1, f'AutoClosed {autoclosed}')
        self.infowin.addstr(18, 1, f'MarginClosed {marginclosed}')
        self.infowin.addstr(19, 1, f'CutoutClosed {cutoutclosed}')
        self.infowin.addstr(20, 1, f'Total Closed {autoclosed + marginclosed + cutoutclosed}')
        self.infowin.addstr(21, 1, f'Max Active Positions {maximum_var[4]}')

        self.infowin.addstr(25, 1, f'Cutout Index {cutoutindx}')

        self.z = 0
        for f in trdesk:
            self.infowin.addstr(27 + self.z, 1, f'{f} {crp.get(f, "NaN"):<20}') # prices
            if f in [i[1] for i in ap]:
                self.infowin.addstr('x')
            self.z += 1

        for f in trdesk:
            self.infowin.addstr(27 + self.z, 1, f'{f} ')
            prmeans = means_data.get(f, lastmean.get(f, ["NaN"]))
            if f in means_data:
                lastmean[f] = means_data[f]
            
            if prmeans[0] == "NaN":
                self.infowin.addstr(f'{prmeans[0]}')
            else:
                for x in prmeans:
                    self.infowin.addstr(f'{x:10.4f} ')
            self.z += 1

        if len(position_history) > 0:
            selected_position = position_history.get(max([x for x in position_history if len(position_history[x]) > 10], default=None), False)
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
        
        self.infowin.refresh()

    def nonglobal_gui(self):
        global last_graph_update
        self.infowin.addstr(23, 1, f'Active Desk {len(actdesk)}')
        self.infowin.addstr(24, 1, f'Possible Symbols {len(Filter)}')

        if foundmark:
            self.infowin.addstr(27 + self.z, 1, f'Foundmark {foundmark[1][0]} {foundmark[0]}')
        # self.pbar.write(f'Current Balance: {curr_balance}, Safe Balance: {safe_balance}, Total Profit: {tp}')
        ### draw the graph
    
        if currd - last_graph_update >= timedelta(minutes=15):
            self.graphwin.clear()
            w = self.draw_plot(curses.LINES - 6, curses.COLS - curses.COLS//4, 'EURUSD')
            
            k = 0
            for i in w:
                for c in i:
                    self.graphwin.addstr(c)
                k += 1
            self.graphwin.refresh()
            last_graph_update = currd

    def flow(self):
        self.log_display()
        self.nonglobal_gui()


    def loop_flow(self, stdscr):
        self.unwrap_main(stdscr)
        while True:
            self.flow()
            curses.napms(2000)

    def wrapper_main(self):
        curses.wrapper(self.loop_flow)

class PrintUtils ():
    def __inti__(self):
        pass

    def print_log(self):
        print(f'Current Balance {curr_balance:,.2f}')
        print(f'Safe Balance {safe_balance:,.2f}')
        print(f'Margin Balance {margin_balance:,.2f}')
        print(f'Free Balance {free_balance:,.2f}')
        print(f'Total Profit {tp:,.2f}')

        maxcheckvars = [curr_balance, safe_balance, margin_balance, free_balance, len(ap)]
        for x in range(len(maxcheckvars)):
            if maximum_var[x] < maxcheckvars[x]:
                maximum_var[x] = maxcheckvars[x]

        mincheckvars = [curr_balance, safe_balance, margin_balance, free_balance]
        for x in range(len(mincheckvars)):
            if minimum_var[x] > mincheckvars[x]:
                minimum_var[x] = mincheckvars[x]

        print(f'Max Current Balance {maximum_var[0]:,.2f}')
        print(f'Max Safe Balance {maximum_var[1]:,.2f}')
        print(f'Max Margin Balance {maximum_var[2]:,.2f}')
        print(f'Max Free Balance {maximum_var[3]:,.2f}')
        print(f'Min Current Balance {minimum_var[0]:,.2f}')
        print(f'Min Safe Balance {minimum_var[1]:,.2f}')
        print( f'Min Margin Balance {minimum_var[2]:,.2f}')
        print(f'Min Free Balance {minimum_var[3]:,.2f}')
        
        print( f'Active Positions {len(ap)}')
        print(f'Total Positions {len(position_history)}')
        print(f'AutoClosed {autoclosed}')
        print(f'MarginClosed {marginclosed}')
        print(f'CutoutClosed {cutoutclosed}')
        print(f'Total Closed {autoclosed + marginclosed + cutoutclosed}')
        print(f'Max Active Positions {maximum_var[4]}')

        print(f'Active Desk {len(actdesk)}')
        print(f'Possible Symbols {len(Filter)}')


        print(f'Cutout Index {cutoutindx}')

        self.z = 0
        for f in trdesk:
            print(f'{f} {crp.get(f, "NaN"):<20}', end='') # prices
            if f in [i[1] for i in ap]:
                print('x')
            else:
                print('')
            self.z += 1

        for f in trdesk:
            print( f'{f} ', end='')
            prmeans = means_data.get(f, lastmean.get(f, ["NaN"]))
            if f in means_data:
                lastmean[f] = means_data[f]
            
            if prmeans[0] == "NaN":
                print(f'{prmeans[0]}')
            else:
                for x in prmeans:
                    print(f'{x:10.4f} ')
            self.z += 1

        if len(position_history) > 0:
            selected_position = position_history.get(max([x for x in position_history if len(position_history[x]) > 10], default=None), False)
            if selected_position:
                self.z += 1
                print(f'Latest Closed Position')
                self.z += 1 
                for d in selected_position:
                    selected_data = selected_position[d]
                    if isinstance(selected_data, float):
                        selected_data = f'{selected_data:,}'
                    print(f'{d:{(curses.COLS//8) -3 }}  {f"{selected_data}":<{(curses.COLS//8) -3}}')
                    self.z += 1

        if foundmark:
            print(f'Foundmark {foundmark[1][0]} {foundmark[0]}')

    def loop_flow(self):
        while True:
            self.print_log()
            time.sleep(2)
