"""
Data models for the l2data_reader package.
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional

from .proto.market_data_pb2 import (
    SecuDepthMarketData,
    TransactionEntrustData,
    TransactionTradeData
)

@dataclass
class Snapshot:
    """数据结构，用于保存单个股票的行情快照"""
    symbol: str
    tick: Optional[SecuDepthMarketData] = None
    orders: List[TransactionEntrustData] = field(default_factory=list)
    transactions: List[TransactionTradeData] = field(default_factory=list)

@dataclass
class Slice:
    """数据结构，用于保存多个股票的行情快照"""
    ticks: Dict[str, Snapshot] = field(default_factory=dict)

@dataclass
class MarketDataResult:
    """市场数据读取结果，包含头部信息和数据内容"""
    header: 'MarketDataHeader'  # 需要在reader.py中导入
    data: object  # 可能是SecuDepthMarketData、TransactionEntrustData或TransactionTradeData
    
    @property
    def is_tick_data(self) -> bool:
        """是否为行情快照数据"""
        return self.header.msg_type == 1001
    
    @property
    def is_order_data(self) -> bool:
        """是否为委托数据"""
        return self.header.msg_type == 1002
    
    @property
    def is_trade_data(self) -> bool:
        """是否为成交数据"""
        return self.header.msg_type == 1003
    
    @property
    def tick_data(self) -> Optional[SecuDepthMarketData]:
        """获取行情快照数据"""
        if self.is_tick_data and hasattr(self.data, 'secu_depth_market_data'):
            return self.data.secu_depth_market_data
        return None
    
    @property
    def order_data(self) -> Optional[TransactionEntrustData]:
        """获取委托数据"""
        if self.is_order_data and hasattr(self.data, 'transaction_entrust_data'):
            return self.data.transaction_entrust_data
        return None
    
    @property
    def trade_data(self) -> Optional[TransactionTradeData]:
        """获取成交数据"""
        if self.is_trade_data and hasattr(self.data, 'transaction_trade_data'):
            return self.data.transaction_trade_data
        return None