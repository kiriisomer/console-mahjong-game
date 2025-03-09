# 游戏画面，用来绘制麻将牌
# 在控制台中绘制
import curses
import tile
import time
from utils import DEBUG

# 字符界面仿照"FC4人麻将"，有下列几行：
# 01: 宝牌牌山
# 02: [PLAYER 4] 弃牌行2
# 03:            弃牌行1
# 04: 玩家4手牌     玩家4副露
# 05: [PLAYER 3] 弃牌行2
# 06:            弃牌行1
# 07: 玩家3手牌     玩家3副露
# 08: [PLAYER 2] 弃牌行2
# 09:            弃牌行1
# 10: 玩家2手牌     玩家2副露
# 11: [PLAYER 1] 弃牌行2
# 12:            弃牌行1
# 13: 玩家1手牌     玩家1副露
# 14: 游标，指示出哪张牌


class Tui:
    """字符界面"""

    def __init__(self):
        self.screen = None

        self.stdscr = None

    def initialize(self):
        self.stdscr = curses.initscr()
        curses.noecho()
        curses.cbreak()
        curses.curs_set(0)
        self.stdscr.keypad(True)

    def terminate(self):
        self.stdscr.keypad(False)
        curses.curs_set(2)
        curses.nocbreak()
        curses.echo()
        curses.endwin()

    def draw(self, screen_info: list[str] = None):
        """绘制"""
        # 可能会报错：_curses.error: addwstr() returned ERR
        # 一般是因为控制台窗口太小
        # 检查窗口大小，目前的设计是最多14行
        height, width = self.stdscr.getmaxyx()

        self.stdscr.clear()
        # DEBUG("==== draw ====")
        for idx, text in enumerate(screen_info):
            # DEBUG(text)
            row = idx + 1
            if row >= height:
                break
            self.stdscr.addstr(row, 1, text)

        # DEBUG("==== draw ====")
        self.stdscr.refresh()


if __name__ == "__main__":
    # test
    tui = Tui()
    tui.initialize()
    try:
        test_screen_info = [
            "🀫🀫🀫🀁🀆🀫🀫",
            "[PLAYER 4]  ",
            "            🀐🀑🀒🀓🀔🀕🀖🀗🀘",
            "🀐🀐🀐🀑🀒🀓🀔         🀕🀖🀗 🀘🀘🀘",
            "[PLAYER 3]  ",
            "            🀙🀚🀛🀜🀝🀞🀟🀠🀡",
            "🀙🀙🀙🀚🀛🀜🀝🀞🀟🀠          🀡🀡🀡",
            "[PLAYER 2]  ",
            "            🀇🀈🀉🀊🀋🀌🀍🀎🀎",
            "🀇🀇🀇🀈       🀉🀊🀋 🀌🀍🀎 🀏🀏🀏🀏",
            "[PLAYER 1]  ",
            "            🀀🀁🀂🀃🀆🀅🀄🀄🀄",
            "🀀🀀🀀🀁🀁🀁🀂🀂🀂🀃          🀅🀅🀅",
            " ^             ",
        ]

        for i in range(10):
            tui.draw(test_screen_info)
            time.sleep(1)

        time.sleep(20)
    finally:
        tui.terminate()
