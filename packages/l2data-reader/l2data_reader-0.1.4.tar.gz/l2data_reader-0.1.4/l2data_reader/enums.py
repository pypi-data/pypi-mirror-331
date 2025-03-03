"""
枚举类型定义，从 market_data.proto 中导出
"""

from enum import Enum, IntEnum

# 从 proto 文件中导入枚举类型
from .proto.market_data_pb2 import (
    TransFlagEnum,
    TrdBSFlag,
    DirectionEnum,
    OrdActionEnum,
    TickStatusFlagEnum
)

# 交易标志枚举
class TransFlag(IntEnum):
    """逐笔行情数据标识"""
    ALONE = TransFlagEnum.TF_Alone    # 逐笔独立编号
    UNIFIED = TransFlagEnum.TF_Unified  # 逐笔统一编号

# 交易类型枚举
class TrdType(IntEnum):
    """交易类型"""
    UNKNOWN = TrdBSFlag.TT_UNKNOWN  # 未知
    BUY = TrdBSFlag.TT_BUY          # SH.主动买
    SELL = TrdBSFlag.TT_SELL        # SH.主动卖
    CANCEL = TrdBSFlag.TT_CANCEL    # SZ.撤单
    DEAL = TrdBSFlag.TT_DEAL        # SZ.成交

# 交易方向枚举
class Direction(IntEnum):
    """交易方向"""
    UNKNOWN = DirectionEnum.DIR_UNKNOWN  # 未知
    BUY = DirectionEnum.DIR_BUY          # 买单
    SELL = DirectionEnum.DIR_SELL        # 卖单

# 订单操作枚举
class OrdAction(IntEnum):
    """订单操作类型"""
    UNKNOWN = OrdActionEnum.OT_UNKNOWN  # 未知
    ADD = OrdActionEnum.OT_ADD          # SH.增加订单
    DELETE = OrdActionEnum.OT_DELETE    # SH.删除订单
    STATUS = OrdActionEnum.OT_STATUS    # SH.产品状态订单
    MARKET = OrdActionEnum.OT_MARKET    # SZ.市价委托
    LIMIT = OrdActionEnum.OT_LIMIT      # SZ.限价委托
    BFZY = OrdActionEnum.OT_BFZY        # SZ.本方最优

# 行情状态标志枚举
class TickStatusFlag(IntEnum):
    """行情状态标志"""
    UNKNOWN = TickStatusFlagEnum.TSF_UNKNOWN  # 未知
    ADD = TickStatusFlagEnum.TSF_ADD          # 产品未上市
    START = TickStatusFlagEnum.TSF_START      # 启动
    OCALL = TickStatusFlagEnum.TSF_OCALL      # 开市集合竞价
    TRADE = TickStatusFlagEnum.TSF_TRADE      # 连续自动撮合
    SUSP = TickStatusFlagEnum.TSF_SUSP        # 停牌
    CCALL = TickStatusFlagEnum.TSF_CCALL      # 收盘集合竞价
    CLOSE = TickStatusFlagEnum.TSF_CLOSE      # 闭市
    ENDTR = TickStatusFlagEnum.TSF_ENDTR      # 交易结束

# 提供枚举名称到枚举值的映射
TRANS_FLAG_MAP = {
    "ALONE": TransFlag.ALONE,
    "UNIFIED": TransFlag.UNIFIED
}

TRD_TYPE_MAP = {
    "UNKNOWN": TrdType.UNKNOWN,
    "BUY": TrdType.BUY,
    "SELL": TrdType.SELL,
    "CANCEL": TrdType.CANCEL,
    "DEAL": TrdType.DEAL
}

DIRECTION_MAP = {
    "UNKNOWN": Direction.UNKNOWN,
    "BUY": Direction.BUY,
    "SELL": Direction.SELL
}

ORD_ACTION_MAP = {
    "UNKNOWN": OrdAction.UNKNOWN,
    "ADD": OrdAction.ADD,
    "DELETE": OrdAction.DELETE,
    "STATUS": OrdAction.STATUS,
    "LIMIT": OrdAction.LIMIT,
    "MARKET": OrdAction.MARKET,
    "BFZY": OrdAction.BFZY,
}

TICK_STATUS_FLAG_MAP = {
    "UNKNOWN": TickStatusFlag.UNKNOWN,
    "ADD": TickStatusFlag.ADD,
    "START": TickStatusFlag.START,
    "OCALL": TickStatusFlag.OCALL,
    "TRADE": TickStatusFlag.TRADE,
    "SUSP": TickStatusFlag.SUSP,
    "CCALL": TickStatusFlag.CCALL,
    "CLOSE": TickStatusFlag.CLOSE,
    "ENDTR": TickStatusFlag.ENDTR
}