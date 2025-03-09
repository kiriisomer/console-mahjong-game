# 规则

__all__ = ["can_chi", "can_pon", "can_minkan", "can_ankan", "can_kakan", "is_agari"],
############
# 游戏流程规则
rule_doc = """
游戏的流程描述：
找一个玩家A
1 抓牌流程（从前，从后抓牌都是抓牌）
1.1 判断玩家能做的动作（胡，杠）
    做动作吗？
    - 杠
        判断其它玩家能做的动作（胡）
        其它玩家做动作吗？
        - 执行动作
            游戏结束
        - 不做动作
            切换到玩家的抓牌流程（从后面抓）
    - 胡
        游戏结束
    - 不做动作
    进入玩家A的弃牌流程

找一个玩家A
2 弃牌流程
2.1 判断其它玩家能做的动作（胡，杠，碰，吃）
    其它玩家做动作吗？
    - 胡
        游戏结束
    - 杠
        切换到其它玩家的抓牌流程（从后面抓）
    - 碰
        切换到其它玩家的弃牌流程
    - 吃
        切换到其它玩家的弃牌流程
    - 不执行动作
       切换到玩家A的下一个玩家抓牌流程

"""


def can_chi(tehai, sutehai) -> list[list[int]]:
    """判断手牌里能否吃目标牌，返回所有的可能吃的牌的索引列表。"""
    # 手牌不够两张无法判断，肯定不能吃。
    if len(tehai) < 2:
        return []

    # 字风牌不能吃
    if sutehai >= 30:
        return []

    result = []
    for i in range(len(tehai) - 1):
        if tehai[i] + 1 == tehai[i + 1] and (
            tehai[i] + 2 == sutehai or tehai[i] - 1 == sutehai
        ):
            result.append([i, i + 1])
        elif tehai[i] + 1 == sutehai and tehai[i] + 2 == tehai[i + 1]:
            result.append([i, i + 1])
    return result


def can_pon(tehai, sutehai) -> list[list[int]]:
    """判断手牌里能否碰目标牌，返回所有的可能碰的牌的索引列表。（一般只有一种）"""
    # 手牌不够两张无法判断，肯定不能碰。
    if len(tehai) < 2:
        return []

    result = []
    for i in range(len(tehai) - 1):
        if tehai[i] == tehai[i + 1] == sutehai:
            result.append([i, i + 1])
    return result


def can_minkan(tehai, sutehai) -> list[list[int]]:
    """判断手牌里能否明杠目标牌，返回所有的可能明杠的牌的索引列表。（一般只有一种）"""
    # 手牌不够三张无法判断，肯定不能明杠。
    if len(tehai) < 3:
        return []

    result = []
    for i in range(len(tehai) - 2):
        if tehai[i] == tehai[i + 1] == tehai[i + 2] == sutehai:
            result.append([i, i + 1, i + 2])
    return result


def can_ankan(tehai) -> list[list[int]]:
    """判断手牌里能否暗杠，返回所有的可能暗杠的牌的索引列表。"""
    # 手牌不够四张无法判断，肯定不能暗杠。
    if len(tehai) < 4:
        return []

    # 由于手牌的最右一张是新进张，没有排序，所以需要特别处理。
    new_tehai = tehai[-1]
    result = []
    for i in range(len(tehai) - 4):
        if tehai[i] == tehai[i + 1] == tehai[i + 2] == tehai[i + 3]:
            result.append([i, i + 1, i + 2, i + 3])
        elif tehai[i] == tehai[i + 1] == tehai[i + 2] == new_tehai:
            result.append([i, i + 1, i + 2, i + 3])
    return result


def can_kakan(tehai, kuihai: list) -> list[list[int]]:
    """判断手牌里能否加杠，返回所有的可能加杠的牌的索引列表。"""
    result = []

    for pat in kuihai:
        # 副露里三张是一样的刻子才能判断能否加杠
        if pat[0] == pat[1] == pat[2]:
            for i in range(len(tehai)):
                if tehai[i] == pat[0]:
                    result.append([i])
    return result


############
# 牌的组合规则
def check_pat_count_overflow(pat: str):
    """检查模式里是不是有牌超过了4张"""
    from collections import Counter

    stat = Counter(pat)
    for i in stat.values():
        if i > 4:
            return True
    return False


def compose_2_patterns(pat1_list: list[str], pat2_list: list[str]):
    """组合两个模式"""
    pattern = []
    for i in pat1_list:
        for j in pat2_list:
            result = "".join(sorted((i + j)))
            if check_pat_count_overflow(result):
                continue
            else:
                pattern.append(result)
    return pattern


def compose_3_patterns(
    pat1_list: list[str], pat2_list: list[str], pat3_list: list[str]
):
    """组合三个模式"""
    pattern = []
    for i in pat1_list:
        for j in pat2_list:
            for k in pat3_list:
                result = "".join(sorted((i + j + k)))
                if check_pat_count_overflow(result):
                    continue
                else:
                    pattern.append(result)
    return pattern


def compose_4_patterns(
    pat1_list: list[str],
    pat2_list: list[str],
    pat3_list: list[str],
    pat4_list: list[str],
):
    """组合四个模式"""
    pattern = []
    for i in pat1_list:
        for j in pat2_list:
            for k in pat3_list:
                for m in pat4_list:
                    result = "".join(sorted((i + j + k + m)))
                    if check_pat_count_overflow(result):
                        continue
                    else:
                        pattern.append(result)
    return pattern


shunzi = [
    "123",
    "234",
    "345",
    "456",
    "567",
    "678",
    "789",
]
kezi = [
    "111",
    "222",
    "333",
    "444",
    "555",
    "666",
    "777",
    "888",
    "999",
]
wind_kezi = [
    "111",
    "222",
    "333",
    "444",
    "555",
    "666",
    "777",
]

# 模式列表
# 数字牌
# 1 顺子+刻子
PATTERN_NUMBER_LIST = []
# 2 纯刻子(用于字牌)
PATTERN_WIND_LIST = []

# 1组顺子,刻子
PATTERN_NUMBER_LIST += shunzi
PATTERN_NUMBER_LIST += kezi
# 2组顺子,刻子
PATTERN_NUMBER_LIST += compose_2_patterns(shunzi, shunzi)
PATTERN_NUMBER_LIST += compose_2_patterns(shunzi, kezi)
PATTERN_NUMBER_LIST += compose_2_patterns(kezi, kezi)
# 3组顺子,刻子
PATTERN_NUMBER_LIST += compose_3_patterns(shunzi, shunzi, shunzi)
PATTERN_NUMBER_LIST += compose_3_patterns(shunzi, shunzi, kezi)
PATTERN_NUMBER_LIST += compose_3_patterns(shunzi, kezi, kezi)
PATTERN_NUMBER_LIST += compose_3_patterns(kezi, kezi, kezi)
# 4组顺子,刻子
PATTERN_NUMBER_LIST += compose_4_patterns(shunzi, shunzi, shunzi, shunzi)
PATTERN_NUMBER_LIST += compose_4_patterns(shunzi, shunzi, shunzi, kezi)
PATTERN_NUMBER_LIST += compose_4_patterns(shunzi, shunzi, kezi, kezi)
PATTERN_NUMBER_LIST += compose_4_patterns(shunzi, kezi, kezi, kezi)
PATTERN_NUMBER_LIST += compose_4_patterns(kezi, kezi, kezi, kezi)

# 风牌和三元牌
# 纯刻子
PATTERN_WIND_LIST += wind_kezi
PATTERN_WIND_LIST += compose_2_patterns(wind_kezi, wind_kezi)
PATTERN_WIND_LIST += compose_3_patterns(wind_kezi, wind_kezi, wind_kezi)
PATTERN_WIND_LIST += compose_4_patterns(
    wind_kezi, wind_kezi, wind_kezi, wind_kezi
)

# 把模式列表从字符串转换成数字列表
for i in range(len(PATTERN_NUMBER_LIST)):
    PATTERN_NUMBER_LIST[i] = list(map(int, PATTERN_NUMBER_LIST[i]))

for i in range(len(PATTERN_WIND_LIST)):
    PATTERN_WIND_LIST[i] = list(map(int, PATTERN_WIND_LIST[i]))


# def is_kokushimusou(tehai):
#     """是否是国士无双"""


# def is_qiduizi(tehai):
#     """是否是七对子"""


def is_general_pattern(tehai) -> bool:
    """是否普通模式和牌"""
    # 判断是否和牌，此时手牌已经有14张
    # 1 拆分牌，将牌按万子，饼子，索子，字风牌分开，并且都缩小到1到9的范围
    m_list = []
    p_list = []
    s_list = []
    z_list = []
    for i in tehai:
        if 1 <= i <= 9:
            m_list.append(i)
        elif 11 <= i <= 19:
            p_list.append(i - 10)
        elif 21 <= i <= 29:
            s_list.append(i - 20)
        else:
            z_list.append(i - 30)

    # 2 寻找雀头，拆分雀头出来
    # 3 撇开雀头，对于每种类型的牌的组合，判断是否匹配模式
    # 可以优化的地方: 连续的3张，4张牌会计算多次雀头，可以优化成只计算一次
    if m_list:
        for idx in range(len(m_list) - 1):
            if m_list[idx] == m_list[idx + 1]:
                # 找到了雀头，用剩下的牌判断模式
                tmp_list = m_list[:i] + m_list[i + 2 :]
                if all(
                    (
                        tmp_list == [] or tmp_list in PATTERN_NUMBER_LIST,
                        p_list == [] or p_list in PATTERN_NUMBER_LIST,
                        s_list == [] or s_list in PATTERN_NUMBER_LIST,
                        z_list == [] or z_list in PATTERN_WIND_LIST,
                    )
                ):
                    return True
    if p_list:
        for idx in range(len(p_list) - 1):
            if p_list[idx] == p_list[idx + 1]:
                # 找到了雀头，用剩下的牌判断模式
                tmp_list = p_list[:idx] + p_list[idx + 2 :]
                if all(
                    (
                        tmp_list == [] or tmp_list in PATTERN_NUMBER_LIST,
                        m_list == [] or m_list in PATTERN_NUMBER_LIST,
                        s_list == [] or s_list in PATTERN_NUMBER_LIST,
                        z_list == [] or z_list in PATTERN_WIND_LIST,
                    )
                ):
                    return True
    if s_list:
        for idx in range(len(s_list) - 1):
            if s_list[idx] == s_list[idx + 1]:
                # 找到了雀头，用剩下的牌判断模式
                tmp_list = s_list[:idx] + s_list[idx + 2 :]
                if all(
                    (
                        tmp_list == [] or tmp_list in PATTERN_NUMBER_LIST,
                        m_list == [] or m_list in PATTERN_NUMBER_LIST,
                        p_list == [] or p_list in PATTERN_NUMBER_LIST,
                        z_list == [] or z_list in PATTERN_WIND_LIST,
                    )
                ):
                    return True
    if z_list:
        for idx in range(len(z_list) - 1):
            if z_list[idx] == z_list[idx + 1]:
                # 找到了雀头，用剩下的牌判断模式
                tmp_list = z_list[:idx] + z_list[idx + 2 :]
                if all(
                    (
                        tmp_list == [] or tmp_list in PATTERN_WIND_LIST,
                        m_list == [] or m_list in PATTERN_NUMBER_LIST,
                        p_list == [] or p_list in PATTERN_NUMBER_LIST,
                        s_list == [] or s_list in PATTERN_NUMBER_LIST,
                    )
                ):
                    return True

    return False


def is_zumo(tehai) -> bool:
    tehai2 = sorted(tehai)
    return any([
        is_general_pattern(tehai2)
    ])

def is_ron(tehai, sutehai) -> bool:
    tehai2 = sorted(tehai + [sutehai])
    return any([
        is_general_pattern(tehai2)
    ])

def test_print_pattern():
    """测试输出模式列表"""
    # print(len(PATTERN_NUMBER_LIST))
    with open("pattern.txt", "w") as f:
        for i in PATTERN_NUMBER_LIST:
            f.write(str(i) + "\n")


def test_check_win():
    tehai = [1, 2, 3, 11, 12, 13, 21, 22, 23, 29, 29, 33, 33, 33]
    print(f"tehai: {tehai}")
    print(f"is_win: {is_general_pattern(tehai)}")

    tehai = [21, 21, 21, 21, 22, 22, 22, 22, 23, 23, 23, 23, 24, 24]
    print(f"tehai: {tehai}")
    print(f"is_win: {is_general_pattern(tehai)}")


# test_check_win()
