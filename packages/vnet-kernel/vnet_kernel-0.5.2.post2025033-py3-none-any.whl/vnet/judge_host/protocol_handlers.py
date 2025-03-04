from abc import ABC, abstractmethod
from typing import Any


class ProtocolHandler(ABC):
    """协议处理器抽象基类"""

    @abstractmethod
    def process_packet(self, data: bytes, addr: tuple[str, int], send_callback):
        """处理接收到的数据包"""
        pass

    @abstractmethod
    def create_connection(self, socket_fd: int, peer_addr: tuple[str, int], **kwargs) -> Any:
        """创建连接对象"""
        pass
