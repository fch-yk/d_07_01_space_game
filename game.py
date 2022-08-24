import asyncio
import curses
import time


async def blink(canvas, row, column, symbol='*'):
    while True:
        canvas.addstr(row, column, symbol, curses.A_DIM)
        for __ in range(20):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for __ in range(3):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for __ in range(5):
            await asyncio.sleep(0)
        canvas.addstr(row, column, symbol)
        for __ in range(3):
            await asyncio.sleep(0)


def draw(canvas):
    row = 5
    column = 20

    canvas.border()
    curses.curs_set(False)
    corutines = []
    for column in range(20, 25):
        corutines.append(blink(canvas, row, column))

    while True:
        for corutine in corutines:
            corutine.send(None)
        canvas.refresh()
        time.sleep(0.1)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(draw)
