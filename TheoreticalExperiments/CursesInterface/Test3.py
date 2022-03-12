allchar = [27, 91, 49, 48, 55, 109, 51, 32, 83, 99, 97, 116, 101, 114, 10, 9484, 9472, 9488, 46, 9508, 57, 52, 8226, 9474, 54, 50, 45, 9492, 9516, 9496]
vischar = ['\x1b', '[', '1', '0', '7', 'm', '3', ' ', 'S', 'c', 'a', 't', 'e', 'r', '\n', '┌', '─', '┐', '.', '┤', '9', '4', '•', '│', '6', '2', '-', '└', '┬', '┘']
dechar = [b'\x1b', b'[', b'1', b'0', b'7', b'm', b'3', b' ', b'S', b'c', b'a', b't', b'e', b'r', b'\n', b'\xe2\x94\x8c', b'\xe2\x94\x80', b'\xe2\x94\x90', b'.', b'\xe2\x94\xa4', b'9', b'4', b'\xe2\x80\xa2', b'\xe2\x94\x82', b'6', b'2', b'-', b'\xe2\x94\x94', b'\xe2\x94\xac', b'\xe2\x94\x98']
for i in allchar:
    print(hex(i))

import curses
import locale
locale.setlocale(locale.LC_ALL, '')
code = locale.getpreferredencoding()

def main(stdscr):
    curses.start_color()
    curses.use_default_colors()
    k = 0
    for i in allchar:
        stdscr.addstr("||" + str(k) + '||')
        stdscr.addstr(chr(i).encode('utf-8'))
        k += 1
    stdscr.refresh()
    curses.napms(10000)
    input()

curses.wrapper(main)
