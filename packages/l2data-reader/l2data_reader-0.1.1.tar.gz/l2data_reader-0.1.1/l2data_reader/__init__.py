"""
L2Data Reader - A package for reading level 2 market data.
"""

__version__ = '0.1.0'

from .reader import MarketDataReader, MarketDataHeader, IndexEntry
from .models import Snapshot, Slice, MarketDataResult
from .exceptions import NoDataException, DataFormatException

# 导出枚举类型
from .enums import (
    TransFlag, TrdType, Direction, OrdAction, TickStatusFlag,
    TRANS_FLAG_MAP, TRD_TYPE_MAP, DIRECTION_MAP, ORD_ACTION_MAP, TICK_STATUS_FLAG_MAP
)

__all__ = [
    'MarketDataReader',
    'MarketDataHeader',
    'IndexEntry',
    'Snapshot',
    'Slice',
    'MarketDataResult',
    'NoDataException',
    'DataFormatException',
    # 枚举类型
    'TransFlag',
    'TrdType',
    'Direction',
    'OrdAction',
    'TickStatusFlag',
    # 枚举映射
    'TRANS_FLAG_MAP',
    'TRD_TYPE_MAP',
    'DIRECTION_MAP',
    'ORD_ACTION_MAP',
    'TICK_STATUS_FLAG_MAP',
]