from enum import Enum
from dataclasses import dataclass, field
import random
from utils import DEBUG

from tile import TILE_MAP, B


@dataclass
class Deck:
    yama: list[int] = field(default_factory=list)
    index: int = 0
    gang_index: int = 135
    # 最后留14张牌作为宝牌指示牌与杠牌。
    gap_index: int = 135 - 14
    # 宝牌为倒数第5,7,9,11,13张牌。
    # 里宝牌为倒数第6,8,10,12,14张牌。
    # 列表直接保存了宝牌在yama中的索引。
    dora_index_list: list[int] = field(default_factory=list)
    uradora_index_list: list[int] = field(default_factory=list)

    @staticmethod
    def new_yama() -> "Deck":
        """新牌"""
        # 用 1~9表示万子，用11~19表示饼子，用21~29表示索子，用31~37表示东南西北白发中
        # 一共136张牌
        deck = (
            list(range(1, 10))
            + list(range(11, 20))
            + list(range(21, 30))
            + list(range(31, 38))
        ) * 4
        # 洗牌
        for i in range(4):
            splitter = random.randint(0, 136)
            deck = deck[splitter:] + deck[:splitter]
            random.shuffle(deck)
        return deck

    def dispatch_tile(self, num: int = 1) -> list[int]:
        """发牌"""
        tiles = self.yama[self.index : self.index + num]
        self.index += num
        return tiles

    def dispatch_gang_tile(self) -> list[int]:
        """发杠牌"""
        tiles = self.yama[self.gang_index - 1 : self.gang_index]
        self.gang_index -= 1
        return tiles

    def add_dora_index(self):
        """添加一张宝牌指示牌"""
        match len(self.dora_index_list):
            case 0:
                self.dora_index_list.append(135 - 5)
                self.uradora_index_list.append(135 - 6)
            case 1:
                self.dora_index_list.append(135 - 7)
                self.uradora_index_list.append(135 - 8)
            case 2:
                self.dora_index_list.append(135 - 9)
                self.uradora_index_list.append(135 - 10)
            case 3:
                self.dora_index_list.append(135 - 11)
                self.uradora_index_list.append(135 - 12)
            case 4:
                self.dora_index_list.append(135 - 13)
                self.uradora_index_list.append(135 - 14)

    def get_dora_info(self):
        """获取宝牌信息(不是索引)"""
        return (self.dora_index_list, self.uradora_index_list)

    def can_dispatch_tile(self) -> bool:
        """判断是否能继续摸牌"""
        return self.index < 122  # 136 - 14

    def can_dispatch_gang_tile(self) -> bool:
        """判断是否能继续发杠牌"""
        # 如果4杠了，或者没有牌可以起了。就不能再杠了。
        return any(
            (
                self.gang_index > 131,  # 135 - 4
                self.index >= 122,  # 136 - 14
            )
        )


@dataclass
class Player:
    tehai: list[int] = field(default_factory=list)
    tedashi: list[int] = field(default_factory=list)
    kuihai: list[list[int]] = field(default_factory=list)

    def draw(self, tiles: list[int]):
        """摸牌"""
        self.tehai += tiles

    def sort_tehai(self):
        """整理手牌"""
        self.tehai.sort()

    def suteru(self, tehai_index: int):
        """打一张牌,将牌放进弃牌牌堆里。返回要打的牌"""
        tile = self.tehai.pop(tehai_index)
        self.tedashi.append(tile)
        return tile

    def chi(self, tehai_index_1: int, tehai_index_2: int, sutehai: int):
        """吃"""
        # 先pop大的索引，再pop小的索引
        tile2 = self.tehai.pop(tehai_index_2)
        tile1 = self.tehai.pop(tehai_index_1)
        self.kuihai.append([tile1, tile2, sutehai])

    def pon(self, tehai_index_1: int, tehai_index_2: int, sutehai: int):
        """碰"""
        tile2 = self.tehai.pop(tehai_index_2)
        tile1 = self.tehai.pop(tehai_index_1)
        self.kuihai.append([tile1, tile2, sutehai])

    def ankan(
        self,
        tehai_index_1: int,
        tehai_index_2: int,
        tehai_index_3: int,
        tehai_index_4: int,
    ):
        """暗杠"""
        tile4 = self.tehai.pop(tehai_index_4)
        tile3 = self.tehai.pop(tehai_index_3)
        tile2 = self.tehai.pop(tehai_index_2)
        tile1 = self.tehai.pop(tehai_index_1)
        self.kuihai.append([tile1, tile2, tile3, tile4])

    def minkan(
        self,
        tehai_index_1: int,
        tehai_index_2: int,
        tehai_index_3: int,
        sutehai: int,
    ):
        """明杠"""
        tile3 = self.tehai.pop(tehai_index_3)
        tile2 = self.tehai.pop(tehai_index_2)
        tile1 = self.tehai.pop(tehai_index_1)
        self.kuihai.append([tile1, tile2, tile3, sutehai])

    def kakan(self, tehai_index, kuihai_index=-1):
        """加杠"""
        tile = self.tehai.pop(tehai_index)
        if kuihai_index < 0:
            for idx in range(self.kuihai):
                if self.kuihai[idx][0] == self.kuihai[idx][1] == tile:
                    self.kuihai[kuihai_index].append(tile)
                    break
        else:
            self.kuihai[kuihai_index].append(tile)

    def ron(self, sutehai: int):
        """送和"""
        self.tehai.append(sutehai)

    def tumo(self):
        """自摸"""
        # 自摸目前什么也不用做
        pass


@dataclass
class Table:
    deck: Deck
    player1: Player = field(default_factory=Player)
    player2: Player = field(default_factory=Player)
    player3: Player = field(default_factory=Player)
    player4: Player = field(default_factory=Player)

    @classmethod
    def new_game(cls, new_yama):
        """开新局"""
        table = cls(
            Deck(yama=new_yama),
        )
        return table

    def get_player(self, player_index: int) -> Player:
        return getattr(self, f"player{player_index}")

    def dispatch_tiles(self):
        """开局发牌"""
        self.player1.draw(self.deck.dispatch_tile(4))
        self.player2.draw(self.deck.dispatch_tile(4))
        self.player3.draw(self.deck.dispatch_tile(4))
        self.player4.draw(self.deck.dispatch_tile(4))
        self.player1.draw(self.deck.dispatch_tile(4))
        self.player2.draw(self.deck.dispatch_tile(4))
        self.player3.draw(self.deck.dispatch_tile(4))
        self.player4.draw(self.deck.dispatch_tile(4))
        self.player1.draw(self.deck.dispatch_tile(4))
        self.player2.draw(self.deck.dispatch_tile(4))
        self.player3.draw(self.deck.dispatch_tile(4))
        self.player4.draw(self.deck.dispatch_tile(4))
        self.player1.draw(self.deck.dispatch_tile(1))
        self.player2.draw(self.deck.dispatch_tile(1))
        self.player3.draw(self.deck.dispatch_tile(1))
        self.player4.draw(self.deck.dispatch_tile(1))
        # 第一个玩家应该多起一张，放到循环流程里去
        # self.player1.draw(self.deck.dispatch_tile(1))
        # 翻第一张宝牌
        self.deck.add_dora_index()

    def player_draw(self, player_index: int):
        player: Player = getattr(self, f"player{player_index}")
        # DEBUG(f"player{player_index} draw before")
        # DEBUG(f"player tehai: {player.tehai}")
        player.draw(self.deck.dispatch_tile(1))
        # DEBUG(f"player{player_index} draw after")
        # DEBUG(f"player tehai: {player.tehai}")

    def player_gan_draw(self, player_index: int):
        # DEBUG(f"player{player_index} gan_draw")
        player: Player = getattr(self, f"player{player_index}")
        player.draw(self.deck.dispatch_gang_tile())

    def can_draw_front(self):
        """是否可以从前面摸牌"""
        return self.deck.can_dispatch_tile()

    def can_draw_behind(self):
        """是否可以从后面摸牌"""
        return self.deck.can_dispatch_gang_tile()

    def generate_tui_data(self) -> list[str]:
        """返回tui界面绘制需要的字符串信息"""
        result = []
        # 绘制宝牌牌山
        tmp = [B] * 7
        for idx, val in enumerate(self.deck.dora_index_list):
            tmp[4 - idx] = TILE_MAP[self.deck.yama[val]]

        result.append("".join(tmp))
        # result.append("")   # 里宝牌

        # 绘制玩家牌信息
        for idx, player in enumerate(
            (self.player4, self.player3, self.player2, self.player1)
        ):
            tedashi_str = "".join(
                [TILE_MAP.get(i, TILE_MAP[0]) for i in player.tedashi]
            )
            result.append(f"[{4-idx}P]  {tedashi_str[12:]}")
            result.append(f"      {tedashi_str[:12]}")
            tehai_str = "".join(
                [TILE_MAP.get(i, TILE_MAP[0]) for i in player.tehai]
            )
            kuihai_str = ""
            for i in player.kuihai:
                for j in i:
                    kuihai_str += TILE_MAP.get(j, TILE_MAP[0])

            if len(player.kuihai) == 4:
                result.append(f"{tehai_str:<4} {kuihai_str:>16}")
            elif len(player.kuihai) == 3:
                result.append(f"{tehai_str:<8} {kuihai_str:>12}")
            elif len(player.kuihai) == 2:
                result.append(f"{tehai_str:<12} {kuihai_str:>8}")
            elif len(player.kuihai) == 1:
                result.append(f"{tehai_str:<16} {kuihai_str:>4}")
            else:
                result.append(f"{tehai_str:<20}")

        return result
