from graphics import Tui


KEY_LEFT = "A"
KEY_RIGHT = "D"
KEY_POSITIVE = "J"
KEY_NEGATIVE = "I"
KEY_EXIT = "Q"

class GameScreen:

    def __init__(self):
        self.tui = Tui()
        self.screen_info = []
        self.user_input_info = ""

    def init(self):
        self.tui.initialize()

    def draw(self, screen_info: list[str], user_action_info: str = ""):
        """绘制游戏界面，
        screen_info: 牌信息
        user_action_info: 用户可控制的信息
        """
        self.screen_info = screen_info
        self.user_action_info = user_action_info
        self._draw_table()

    def _draw_table(self):
        """绘制桌面"""
        self.tui.draw(self.screen_info + [self.user_action_info])

    def terminate(self):
        self.tui.terminate()

    def get_key(self):
        """由于curses也处理按键控制，所以将获取用户输入的函数放这里"""
        key = None
        # 只返回需要的key，如果输入别的则忽略
        while key not in (
            KEY_LEFT,
            KEY_RIGHT,
            KEY_POSITIVE,
            KEY_NEGATIVE,
        ):
            key = self.tui.stdscr.getkey()
            key = key.upper()

        return key
