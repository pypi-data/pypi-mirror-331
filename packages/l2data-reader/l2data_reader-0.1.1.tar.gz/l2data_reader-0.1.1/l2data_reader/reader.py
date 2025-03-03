"""
Core functionality for reading market data.
"""

import os
import time
import struct
import mmap
import ctypes
import platform
from dataclasses import dataclass
from typing import Optional, Tuple, Any, Dict, List, Union, BinaryIO
import logging
from google.protobuf.message import Message

# 使用 utils.py 中的功能
from .utils import get_allocation_granularity, time_to_milliseconds, get_total_count
# 使用 exceptions.py 中的异常类
from .exceptions import NoDataException, DataFormatException, FileAccessException, ProtobufParseException

from .proto.market_data_pb2 import (
    SecuDepthMarketData,
    TransactionEntrustData,
    TransactionTradeData
)
from .proto.global_pb2 import Envelope
from .models import MarketDataResult

ALLOCATION_GRANULARITY = get_allocation_granularity()

@dataclass
class MarketDataHeader:
    sequence_no: int
    timestamp: int
    msg_type: int
    body_length: int

    @classmethod
    def from_bytes(cls, data: bytes) -> 'MarketDataHeader':
        if len(data) < cls.size():
            raise ValueError("Insufficient data for MarketDataHeader")
        # C++ 端的 MarketDataHeader 结构：int64_t, int64_t, uint32_t, uint32_t
        sequence_no, timestamp, msg_type, body_length = struct.unpack('=qqII', data)
        return cls(sequence_no, timestamp, msg_type, body_length)

    @staticmethod
    def size() -> int:
        return struct.calcsize('=qqII')  # 8 + 8 + 4 + 4 = 24 字节

@dataclass
class IndexEntry:
    sequence_no: int
    offset: int

    @classmethod
    def from_bytes(cls, data: bytes) -> 'IndexEntry':
        if len(data) < cls.size():
            raise ValueError("Insufficient data for IndexEntry")
        # C++ 端的 IndexEntry 结构：int64_t, uint64_t
        sequence_no, offset = struct.unpack('=qQ', data)
        return cls(sequence_no, offset)

    @staticmethod
    def size() -> int:
        return struct.calcsize('=qQ')  # 8 + 8 = 16 字节

class MappedFileReader:
    def __init__(self, logger, filename: str, window_size: int = 1024*1024*4):
        self.logger = logger
        self.filename = filename
        self.alignment = ALLOCATION_GRANULARITY
        # 确保窗口大小是分配粒度的整数倍，且至少是分配粒度
        self.window_size = max(
            (window_size // self.alignment) * self.alignment,
            self.alignment
        )
        
        self.file = open(filename, 'rb')
        self.file_size = os.path.getsize(filename)
        self.current_pos = 0
        self.window_start = 0
        self.mapped_data = None
        self._map_window()

    def _align_offset(self, offset: int) -> Tuple[int, int]:
        """
        对齐偏移量，返回(对齐的起始位置，需要跳过的字节数)
        """
        aligned_start = (offset // self.alignment) * self.alignment
        skip_bytes = offset - aligned_start
        return aligned_start, skip_bytes

    def _map_window(self):
        """映射新的文件窗口，确保偏移量对齐"""
        try:
            if self.mapped_data:
                self.mapped_data.close()
                self.mapped_data = None

            # 获取对齐的起始位置和需要跳过的字节数
            aligned_start, skip_bytes = self._align_offset(self.window_start)
            
            # 计算需要映射的大小（包括对齐补偿）
            mapping_size = self.window_size + skip_bytes
            # 确保映射大小也是分配粒度的整数倍
            mapping_size = ((mapping_size + self.alignment - 1) // self.alignment) * self.alignment
            
            # 确保不超过文件大小
            if aligned_start + mapping_size > self.file_size:
                mapping_size = self.file_size - aligned_start
                # 确保映射大小仍然是分配粒度的整数倍
                mapping_size = (mapping_size // self.alignment) * self.alignment
            
            # 如果映射大小太小，就不映射了
            if mapping_size < self.alignment:
                self.mapped_data = None
                return

            self.logger.debug(f"映射窗口 - 起始: {aligned_start}, 大小: {mapping_size}, "
                          f"跳过字节: {skip_bytes}, 当前指针: {self.current_pos}")

            # 创建内存映射
            self.mapped_data = mmap.mmap(
                self.file.fileno(),
                mapping_size,
                offset=aligned_start,
                access=mmap.ACCESS_READ
            )
            
            # 更新实际的窗口参数
            self.window_start = aligned_start
            self.window_size = mapping_size

        except Exception as e:
            self.logger.error(f"映射文件窗口失败: 偏移量={self.window_start}, "
                          f"对齐起始位置={aligned_start}, 映射大小={mapping_size}, "
                          f"文件大小={self.file_size}, 错误={str(e)}")
            self.mapped_data = None
            raise

    def read(self, size: int) -> Optional[bytes]:
        """读取指定大小的数据"""
        if size <= 0:
            return None

        try:
            # 动态更新文件大小
            self.get_size()

            if self.current_pos >= self.file_size:
                return None

            # 检查是否需要重新映射窗口
            window_offset = self.current_pos - self.window_start
            if (not self.mapped_data or 
                window_offset < 0 or 
                window_offset + size > self.window_size):
                
                # 设置新的窗口起始位置
                self.window_start = (self.current_pos // self.alignment) * self.alignment
                self._map_window()
                window_offset = self.current_pos - self.window_start

            if not self.mapped_data:
                return None

            read_size = min(size, self.file_size - self.current_pos)
            self.mapped_data.seek(window_offset)
            data = self.mapped_data.read(read_size)

            if data:
                self.current_pos += len(data)

            return data

        except PermissionError:
            self.logger.warning(f"文件被锁定，暂时无法读取: {self.filename}. 尝试稍后重试.")
            time.sleep(0.1)  # 延时100ms后重试
            return self.read(size)  # 递归重试
        except Exception as e:
            self.logger.error(f"读取映射文件失败: 当前位置={self.current_pos}, "
                          f"窗口起始={self.window_start}, 窗口大小={self.window_size}, "
                          f"请求大小={size}, 错误={str(e)}")
            return None

    def seek(self, pos: int):
        """设置文件指针位置"""
        try:
            # 动态更新文件大小
            self.get_size()
            
            if pos < 0:
                pos = 0
            elif pos > self.file_size:
                pos = self.file_size

            self.current_pos = pos
            
            # 检查新位置是否在当前窗口内
            window_offset = pos - self.window_start
            if (not self.mapped_data or 
                window_offset < 0 or 
                window_offset >= self.window_size):
                
                # 对齐到分配粒度
                self.window_start = (pos // self.alignment) * self.alignment
                self._map_window()
                
        except Exception as e:
            self.logger.error(f"设置文件指针位置失败: 目标位置={pos}, "
                          f"当前位置={self.current_pos}, 错误={str(e)}")
            raise

    def get_size(self) -> int:
        """获取最新的文件大小"""
        try:
            self.file_size = os.path.getsize(self.filename)
            return self.file_size
        except Exception as e:
            self.logger.error(f"获取文件大小失败: {str(e)}")
            raise

    def close(self):
        """关闭文件和映射"""
        try:
            if self.mapped_data:
                self.mapped_data.close()
                self.mapped_data = None
            if self.file:
                self.file.close()
                self.file = None
        except Exception as e:
            self.logger.error(f"关闭文件失败: {str(e)}")
            raise

class MarketDataReader:
    def __init__(self, logger, index_file: str, data_file: str, header_file: str):
        self.logger = logger
        self.index_file = index_file
        self.data_file = data_file
        self.header_file = header_file
        self.index_reader = MappedFileReader(self.logger, index_file)
        self.data_reader = MappedFileReader(self.logger, data_file)
        self.last_index_size = 0    # 初始化为0，表示从头开始
        self.current_sequence = -1  # 初始序列号

    def get_count(self) -> int:
        """获取最新的文件大小"""
        try:
            return get_total_count(self.header_file)
        except Exception as e:
            self.logger.error(f"获取文件大小失败: {str(e)}")
            raise

    def read_next(self) -> tuple[MarketDataHeader, Envelope]:
        """读取下一条市场数据"""
        try:
            # 获取最新的索引文件大小
            current_index_size = self.index_reader.get_size()
            if current_index_size == self.last_index_size:
                return None  # 无新数据
            
            while self.last_index_size + IndexEntry.size() <= current_index_size and len(data := self.index_reader.read(IndexEntry.size())) == IndexEntry.size():
                # 读取索引项
                self.index_reader.seek(self.last_index_size)
                index_data = self.index_reader.read(IndexEntry.size())
                if not index_data or len(index_data) < IndexEntry.size():
                    self.logger.warning("读取到不完整的索引数据，等待更多数据...")
                    break  # 数据不完整，等待新数据

                index_entry = IndexEntry.from_bytes(index_data)
                # 检查序列号，避免重复读取
                if index_entry.sequence_no <= self.current_sequence:
                    self.logger.debug(f"跳过旧的序列号: {index_entry.sequence_no}")
                    # 使用return而非continue避免死循环
                    return None  # 跳过旧数据
                self.last_index_size += IndexEntry.size()

                # 读取数据头
                self.data_reader.seek(index_entry.offset)
                header_data = self.data_reader.read(MarketDataHeader.size())
                if not header_data or len(header_data) < MarketDataHeader.size():
                    self.logger.error("无法读取市场数据头部")
                    # 使用return而非continue避免死循环
                    return None  # 数据不完整，跳过

                header = MarketDataHeader.from_bytes(header_data)
                if header.body_length == 0:
                    return None # 数据不完整，跳过

                # 读取数据体
                body_data = self.data_reader.read(header.body_length)
                if not body_data or len(body_data) < header.body_length:
                    self.logger.error("无法读取市场数据体")
                    # 使用return而非continue避免死循环
                    return None  # 数据不完整，跳过

                # 解析市场数据 Protobuf 消息
                market_data = Envelope()
                if not market_data.ParseFromString(body_data):
                    self.logger.error("Failed to parse market Envelope from data.")
                    # 使用return而非continue避免死循环
                    return None  # 解析失败，跳过

                self.current_sequence = header.sequence_no

                return [header, market_data]

            return None

        except Exception as e:
            self.logger.error(f"读取市场数据失败: {e}")
            return None

    def close(self):
        """关闭读取器"""
        self.index_reader.close()
        self.data_reader.close()
