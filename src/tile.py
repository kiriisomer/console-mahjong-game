# define the tile

# 骰子点数，0为骰子符号
T = "🎲⚀⚁⚂⚃⚄⚅"

# 万子，饼子，索子
M = "🀇🀈🀉🀊🀋🀌🀍🀎🀏"
P = "🀙🀚🀛🀜🀝🀞🀟🀠🀡"
S = "🀐🀑🀒🀓🀔🀕🀖🀗🀘"
Z = "🀀🀁🀂🀃🀆🀅🀄"

# 牌背面
B = "🀫"

# 日麻用不到的牌
OTHER = "🀪🀢🀣🀤🀥🀦🀧🀨🀩"

# 用0表示牌背
# 用 1~9表示万子，
# 用11~19表示饼子，
# 用21~29表示索子，
# 用31~37表示东南西北白发中
TILE_MAP = {}


def init_tile():
    """初始化136张牌"""
    global TILE_MAP
    if not TILE_MAP:
        TILE_MAP[0] = B[0]
        for idx, char in enumerate(M):
            TILE_MAP[idx+1] = char

        for idx, char in enumerate(P):
            TILE_MAP[idx+1+10] = char

        for idx, char in enumerate(S):
            TILE_MAP[idx+1+20] = char

        for idx, char in enumerate(Z):
            TILE_MAP[idx+1+30] = char


init_tile()
