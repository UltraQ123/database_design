from enum import Enum,unique


@unique
class envs(Enum):
    OCG = "OCG"
    TCG = "TCG"

@unique
class attribute(Enum):
    Indeterminate = "N/A"
    earth = "地"
    water = "水"
    fire = "炎"
    windy = "风"
    light = "光"
    dark = "暗"
    god = "神"

@unique
class race(Enum):
    Indeterminate = "N/A"
    warrior ="战士族"
    magician ="魔法师族"
    angel ="天使族"
    devil ="恶魔族"
    undead ="不死族"
    machine	 ="机械族"
    water ="水族"
    fire ="炎族"
    rock ="岩石族"
    bird ="鸟兽族"
    plant ="植物族"
    insect ="昆虫族"
    thunder	="雷族"
    dragon ="龙族"
    monster	 ="兽族"
    monster_warrior ="兽战士族"
    dinosaur ="恐龙族"
    fish ="鱼族"
    sea_dragon	 ="海龙族"
    Reptile ="爬虫类族"
    telekinesis ="念动力族"
    phantom_god ="幻神兽族"
    create_god	 ="创造神族"
    phantom_dragon	 ="幻龙族"
    Cyberse = "电子界族"

@unique
class card_type(Enum):
    monster = "怪兽"
    magic = "魔法"
    trap = "陷阱"

@unique
class magic_type(Enum):
    normal = "通常"
    quick = "速攻"
    field = "场地"
    ceremony = "仪式"
    equipment = "装备"
    sustainable = "永续"

@unique
class trap_type(Enum):
    normal = "通常"
    sustainable = "永续"
    counter = "反击"

@unique
class monster_type(Enum):
    normal = "通常"
    effect = "效果"
    fusion = "融合"
    ceremony = "仪式"
    sync = "同调"
    xyz = "超量"
    link = "连接"

@unique
class monster_special(Enum):
    normal = "通常"
    effect = "效果"
    tuner = "调整"
    reversal = "反转"
    soul = "灵魂"
    double = "二重"
    alliance = "同盟"
    cartoon = "卡通"
    token = "衍生物"
    special = "特殊召唤"


@unique
class linkmark(Enum):
    left_up = 0x40
    up = 0x80
    right_up = 0x100
    left = 0x8
    right = 0x20
    left_down = 0x1
    down = 0x2
    right_down = 0x4

"""
↖ 0x40
↑ 0x80
↗0x100
← 0x8
→ 0x20
↙0x1
↓ 0x2
↘ 0x4
"""