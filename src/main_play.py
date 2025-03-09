import time
from utils import DEBUG

from table import Deck, Table, Player
from rule import (
    is_zumo,
    can_ankan,
    can_kakan,
    is_ron,
    can_minkan,
    can_pon,
    can_chi,
)

from game_screen import (
    KEY_LEFT,
    KEY_RIGHT,
    KEY_POSITIVE,
    KEY_NEGATIVE,
    KEY_EXIT,
    GameScreen,
)


def print_deck(deck):
    # print(deck)
    # print("================")
    from tile import TILE_MAP

    for i in deck:
        print(TILE_MAP.get(i, TILE_MAP[0]), end="")

    print("\n")


# 流程完结时的返回值，用于确定下一步该做什么
class PHASE_RESULT:
    DRAW_FRONT = 1
    DRAW_BEHIND = 2
    DROP_TILE = 3
    GAME_END = 4


class Game:
    def play(self):
        """开始一局游戏"""

        # 获取牌组
        deck = Deck.new_yama()
        # print_deck(deck)
        self.game_table = Table.new_game(deck)
        self.ui = GameScreen()

        self.ui.init()

        try:
            # 发牌
            self.game_table.dispatch_tiles()
            self.ui.draw(self.game_table.generate_tui_data())
            time.sleep(1)
            self.game_table.player1.sort_tehai()
            self.game_table.player2.sort_tehai()
            self.game_table.player3.sort_tehai()
            self.game_table.player4.sort_tehai()
            self.ui.draw(self.game_table.generate_tui_data())
            # 先从玩家1开始
            self.current_player_index = 1

            self.game_loop()

        finally:
            self.ui.terminate()

    def game_loop(self):
        """游戏主循环"""
        exit = False
        result = PHASE_RESULT.DRAW_FRONT
        draw_from_front = 1
        while not exit:
            # 先判断能不能起牌(流局)
            if draw_from_front and not self.game_table.can_draw_front():
                exit = True
                break
            DEBUG("current player index is ", self.current_player_index)
            if result == PHASE_RESULT.DRAW_FRONT:
                draw_from_front = 1
                result, player_index = self.player_draw_phase(
                    self.current_player_index, draw_from_front
                )
                DEBUG(f"after player_draw_phase, set player index to {player_index}")
                self.current_player_index = player_index
            elif result == PHASE_RESULT.DRAW_BEHIND:
                draw_from_front = 0
                result, player_index = self.player_draw_phase(
                    self.current_player_index, draw_from_front
                )
                DEBUG(f"after player_draw_phase, set player index to {player_index}")
                self.current_player_index = player_index
            elif result == PHASE_RESULT.DROP_TILE:
                result, player_index = self.player_drop_tile_phase(
                    self.current_player_index
                )
                DEBUG(f"after player_drop_tile_phase, set player index to {player_index}")
                self.current_player_index = player_index
            elif result == PHASE_RESULT.GAME_END:
                exit = True
            else:
                raise Exception("Program Should Never goto here")
            # time.sleep(1)

        # 游戏结束
        DEBUG("game over")

    def player_draw_phase(self, player_index: int, is_from_front=1):
        """玩家起牌环节。返回下一步的任务，以及玩家索引"""
        DEBUG(f"player{player_index} draw phase")
        if is_from_front:
            self.game_table.player_draw(player_index)
        else:
            self.game_table.player_gan_draw(player_index)

        # 查询有哪些动作
        acts = self.player_draw_action(player_index)
        if acts:
            # 获取用户选择结果
            decision, indexs = self.player_select_actions(acts)
            # 依据结果来处理
            if decision == "取消":
                # 退出，进入到出牌环节
                pass
                # return PHASE_RESULT.DROP_TILE, player_index
            elif decision == "カン":
                player = self.game_table.get_player(player_index)
                # 只有一个选择的时候，直接执行
                # 否则，让用户选择用哪些牌执行
                if len(indexs) == 1:
                    if len(indexs[0]) == 1:
                        player.kakan(*indexs[0])
                    else:
                        player.ankan(*indexs[0])
                else:
                    index = self.player_select_action_tiles(indexs)
                    if len(index == 1):
                        player.kakan(*index)
                    else:
                        player.ankan(*index)
                # 杠完后，进入起牌环节
                return PHASE_RESULT.DRAW_BEHIND, player_index

            elif decision == "ツモ":
                return PHASE_RESULT.GAME_END, player_index
                # return self.player_win(player_index)
            else:
                raise Exception("Program Should Never goto here")

        # 没有动作，进入到出牌环节
        return PHASE_RESULT.DROP_TILE, player_index

    def player_drop_tile_phase(self, player_index: int):
        """玩家出牌环节"""
        DEBUG(f"player{player_index} drop tile phase")
        player = self.game_table.get_player(player_index)
        sutehai_index = self.player_select_tehai(player.tehai)
        sutehai = player.suteru(sutehai_index)
        player.sort_tehai()

        # 判断其它玩家能做的动作
        # 按顺序判断每个玩家能做的事情，然后按动作的优先级判断最终做什么动作。

        # 按顺序记录每个玩家选择的动作
        next_player_index_select_action_list = []
        for i in range(3):
            next_player_index = player_index + i + 1
            if next_player_index > 4:
                next_player_index = next_player_index - 4
            acts = self.player_drop_tiles_action(next_player_index, sutehai, player_index)
            if acts:
                decision, indexs = self.player_select_actions(acts)
                next_player_index_select_action_list.append(
                    (next_player_index, decision, indexs)
                )
            else:
                # 没有动作，就当取消
                next_player_index_select_action_list.append(
                    (next_player_index, "取消", None)
                )

        # 裁决执行哪个动作
        # 这里主要是裁决 胡 大于 碰杠，碰杠大于吃
        # 由于麻将游戏的特殊性，不会有抢碰的情况发生。但是会有抢胡的情况发生。
        # 1 先按顺序判断有没有玩家选择胡。
        for info in next_player_index_select_action_list:
            tmp_player_index, decision, indexs = info
            if decision == "ロン":
                player = self.game_table.get_player(tmp_player_index)
                player.ron(sutehai)
                DEBUG(PHASE_RESULT.GAME_END, tmp_player_index)
                return PHASE_RESULT.GAME_END, tmp_player_index
        # 2 判断玩家有没有杠碰
        for info in next_player_index_select_action_list:
            tmp_player_index, decision, indexs = info
            if decision == "カン":
                player = self.game_table.get_player(tmp_player_index)
                player.minkan(*indexs[0], sutehai=sutehai)
                DEBUG(PHASE_RESULT.DRAW_BEHIND, tmp_player_index)
                return PHASE_RESULT.DRAW_BEHIND, tmp_player_index
            elif decision == "ポン":
                player = self.game_table.get_player(tmp_player_index)
                player.pon(*indexs[0], sutehai=sutehai)
                DEBUG(PHASE_RESULT.DROP_TILE, tmp_player_index)
                return PHASE_RESULT.DROP_TILE, tmp_player_index
        # 3 最后判断玩家有没有吃
        for info in next_player_index_select_action_list:
            tmp_player_index, decision, indexs = info
            if decision == "チー":
                player = self.game_table.get_player(tmp_player_index)
                # 吃牌时可能有多种情况可以吃
                if len(indexs) == 1:
                    player.chi(*indexs[0], sutehai=sutehai)
                else:
                    index = self.player_select_action_tiles(indexs)
                    player.chi(*index, sutehai=sutehai)
                DEBUG(PHASE_RESULT.DROP_TILE, tmp_player_index)
                return PHASE_RESULT.DROP_TILE, tmp_player_index

        # 没有动作，进入到下家起牌环节
        DEBUG(PHASE_RESULT.DRAW_FRONT, (player_index) % 4 + 1)
        return PHASE_RESULT.DRAW_FRONT, (player_index) % 4 + 1

    def player_drop_tiles_action(self, player_index: int, sutehai: int, sutehai_player_index: int):
        """弃牌后其它玩家动作。
        player_index: 当前玩家的索引
        sutehai: 当前打出的牌
        sutehai_player_index: 当前打出牌的玩家的索引
        """
        actions = []
        player = self.game_table.get_player(player_index)
        result = is_ron(player.tehai, sutehai)
        if result:
            actions.append(["ロン", result])
        if self.game_table.can_draw_behind():
            result = can_minkan(player.tehai, sutehai)
            if result:
                actions.append(["カン", result])
        result = can_pon(player.tehai, sutehai)
        if result:
            actions.append(["ポン", result])
        # 只有下家可以吃
        if (sutehai_player_index % 4 + 1) == player_index:
            result = can_chi(player.tehai, sutehai)
            if result:
                actions.append(["チー", result])
        # 如果有选项的话，就加上取消按钮
        if actions:
            actions.append(["取消", []])

        return actions

    def player_draw_action(self, player_index: int):
        """起牌后玩家动作"""
        actions = []
        player = self.game_table.get_player(player_index)
        result = is_zumo(player.tehai)
        if result:
            actions.append(["ツモ", []])
        if self.game_table.can_draw_behind():
            result_1 = can_ankan(player.tehai)
            result_2 = can_kakan(player.tehai, player.kuihai)
            result = result_1 + result_2
            if result:
                actions.append(["カン", result])
        # 如果有选项的话，就加上取消按钮
        if actions:
            actions.append(["取消", []])

        return actions

    def player_select_actions(self, actions):
        """绘制动作，并让用户进行选择。返回用户的选择内容值"""
        acts = [x[0] for x in actions]
        arrow_index = 0
        arrow = " >"
        blank = "  "
        act_str = f"{arrow + blank.join(acts):<30}"
        self.ui.draw(self.game_table.generate_tui_data(), act_str)
        decision = None
        while decision is None:
            key = self.ui.get_key()
            if key == KEY_LEFT:
                arrow_index -= 1
                if arrow_index < 0:
                    arrow_index += len(acts)
            elif key == KEY_RIGHT:
                arrow_index += 1
                if arrow_index >= len(acts):
                    arrow_index -= len(acts)
            elif key == KEY_POSITIVE:
                decision = actions[arrow_index]
            elif key == KEY_EXIT:
                raise Exception("User Exit the game")

            # 移动箭头后更新画面
            blank_str_list = [blank] * len(acts)
            blank_str_list[arrow_index] = arrow
            act_str = f'{"".join([blank_str_list[i]+acts[i] for i in range(len(acts))]):<20}'
            self.ui.draw(self.game_table.generate_tui_data(), act_str)

        return decision

    def player_select_action_tiles(self, indexs: list[list[int]]):
        """当吃杠有多个选择的时候，为选项绘制下标，供用户选择"""
        arrow_index = 0
        arrow = "^"
        decision = None

        while decision is None:
            # 绘制第一个选项的箭头
            act_str_list = [" "] * 14
            for index in indexs[arrow_index]:
                act_str_list[index] = arrow
            self.ui.draw(self.game_table.generate_tui_data(), "".join(act_str_list))

            key = self.ui.get_key()
            if key == KEY_LEFT:
                arrow_index -= 1
                if arrow_index < 0:
                    arrow_index += len(indexs)
            elif key == KEY_RIGHT:
                arrow_index += 1
                if arrow_index >= len(indexs):
                    arrow_index -= len(indexs)
            elif key == KEY_POSITIVE:
                decision = indexs[arrow_index]
            elif key == KEY_EXIT:
                raise Exception("User Exit the game")

            # # 移动箭头后更新画面
            # act_str_list = [" "] * 14
            # for index in indexs[arrow_index]:
            #     act_str_list[index] = arrow
            # self.ui.draw(self.game_table.generate_tui_data(), "".join(act_str_list))

        return decision

    def player_select_tehai(self, tehai: list[int]):
        """绘制手牌的下标索引，并让玩家选择。返回选择的索引"""
        DEBUG(tehai, f" {len(tehai)=}")
        arrow_index = len(tehai) - 1
        arrow = "^"
        decision = None
        while decision is None:
            # 绘制箭头
            act_str_list = [" "] * 14
            act_str_list[arrow_index] = arrow
            self.ui.draw(self.game_table.generate_tui_data(), "".join(act_str_list))

            key = self.ui.get_key()
            if key == KEY_LEFT:
                arrow_index -= 1
                if arrow_index < 0:
                    arrow_index += len(tehai)
            elif key == KEY_RIGHT:
                arrow_index += 1
                if arrow_index >= len(tehai):
                    arrow_index -= len(tehai)
            elif key == KEY_POSITIVE:
                decision = arrow_index
            elif key == KEY_EXIT:
                raise Exception("User Exit the game")

        return decision

    def player_win(self, player_index):
        """玩家获胜，绘制获胜页面"""


if __name__ == "__main__":
    Game().play()
