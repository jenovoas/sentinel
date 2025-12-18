#!/usr/bin/env python3
"""
Python wrapper for TruthSync shared memory buffer.
Provides high-level interface for Rust-Python communication.
"""

import struct
import mmap
import time
from pathlib import Path
from typing import Optional, Tuple
from multiprocessing import shared_memory


class MessageType:
    """Message type constants"""
    PROCESS_TEXT = 0x01
    GET_RESULTS = 0x02
    CONFIGURE = 0x03
    HEALTH_CHECK = 0x04
    SHUTDOWN = 0xFF


class SharedBuffer:
    """Shared memory buffer for Rust-Python communication"""
    
    MAGIC = 0xDEADBEEF
    HEADER_FORMAT = '<IHI'  # magic (4), msg_type (2), length (4)
    HEADER_SIZE = struct.calcsize(HEADER_FORMAT)
    CONTROL_SIZE = 64  # Cache line aligned
    
    def __init__(self, name: str, size: int = 1024 * 1024, create: bool = True):
        """
        Initialize shared buffer.
        
        Args:
            name: Buffer name
            size: Buffer size in bytes (excluding control section)
            create: If True, create new buffer; if False, open existing
        """
        self.name = name
        self.capacity = size
        
        if create:
            # Create new shared memory
            self.shm = shared_memory.SharedMemory(
                name=name,
                create=True,
                size=size + self.CONTROL_SIZE
            )
        else:
            # Open existing shared memory
            self.shm = shared_memory.SharedMemory(name=name)
            self.capacity = self.shm.size - self.CONTROL_SIZE
    
    def write(self, msg_type: int, data: bytes) -> None:
        """
        Write message to buffer.
        
        Args:
            msg_type: Message type constant
            data: Payload data
        """
        if len(data) + self.HEADER_SIZE > self.capacity:
            raise ValueError(f"Data too large: {len(data)} bytes (max: {self.capacity - self.HEADER_SIZE})")
        
        # Pack header
        header = struct.pack(
            self.HEADER_FORMAT,
            self.MAGIC,
            msg_type,
            len(data)
        )
        
        # Write to shared memory
        offset = self.CONTROL_SIZE
        self.shm.buf[offset:offset + self.HEADER_SIZE] = header
        self.shm.buf[offset + self.HEADER_SIZE:offset + self.HEADER_SIZE + len(data)] = data
    
    def read(self) -> Tuple[int, bytes]:
        """
        Read message from buffer.
        
        Returns:
            Tuple of (msg_type, data)
        """
        # Read header
        offset = self.CONTROL_SIZE
        header_bytes = bytes(self.shm.buf[offset:offset + self.HEADER_SIZE])
        magic, msg_type, length = struct.unpack(self.HEADER_FORMAT, header_bytes)
        
        # Validate magic
        if magic != self.MAGIC:
            raise ValueError(f"Invalid magic: 0x{magic:08X} (expected: 0x{self.MAGIC:08X})")
        
        # Read data
        data_start = offset + self.HEADER_SIZE
        data_end = data_start + length
        data = bytes(self.shm.buf[data_start:data_end])
        
        return msg_type, data
    
    def close(self):
        """Close shared memory"""
        if hasattr(self, 'shm'):
            self.shm.close()
    
    def unlink(self):
        """Unlink (delete) shared memory"""
        if hasattr(self, 'shm'):
            self.shm.unlink()
    
    def __enter__(self):
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.close()
        if exc_type is None:
            self.unlink()


def benchmark_buffer_overhead():
    """Benchmark shared memory buffer overhead"""
    buffer_name = "benchmark_buffer"
    test_data = b"The unemployment rate is 3.5%"
    iterations = 10000
    
    print("="*60)
    print("SHARED MEMORY BUFFER OVERHEAD BENCHMARK")
    print("="*60)
    
    # Test write performance
    with SharedBuffer(buffer_name, create=True) as buffer:
        # Warmup
        for _ in range(100):
            buffer.write(MessageType.PROCESS_TEXT, test_data)
        
        # Benchmark write
        start = time.perf_counter()
        for _ in range(iterations):
            buffer.write(MessageType.PROCESS_TEXT, test_data)
        end = time.perf_counter()
        
        write_time = (end - start) / iterations * 1_000_000  # microseconds
        
        # Benchmark read
        start = time.perf_counter()
        for _ in range(iterations):
            msg_type, data = buffer.read()
        end = time.perf_counter()
        
        read_time = (end - start) / iterations * 1_000_000  # microseconds
        
        total_time = write_time + read_time
    
    print(f"Data size:       {len(test_data)} bytes")
    print(f"Iterations:      {iterations:,}")
    print(f"\nWrite time:      {write_time:.2f}μs")
    print(f"Read time:       {read_time:.2f}μs")
    print(f"Total overhead:  {total_time:.2f}μs")
    print(f"\nThroughput:      {iterations / (total_time / 1_000_000):.0f} ops/sec")
    
    return total_time


def test_basic_communication():
    """Test basic Rust-Python communication"""
    buffer_name = "test_comm_buffer"
    
    print("\n" + "="*60)
    print("BASIC COMMUNICATION TEST")
    print("="*60)
    
    with SharedBuffer(buffer_name, create=True) as buffer:
        # Write test message
        test_msg = b"Hello from Python!"
        buffer.write(MessageType.PROCESS_TEXT, test_msg)
        print(f"✓ Wrote: {test_msg.decode()}")
        
        # Read back
        msg_type, data = buffer.read()
        print(f"✓ Read:  {data.decode()}")
        print(f"✓ Type:  0x{msg_type:02X}")
        
        assert msg_type == MessageType.PROCESS_TEXT
        assert data == test_msg
        print("\n✅ Communication test PASSED")


if __name__ == '__main__':
    # Run tests
    test_basic_communication()
    overhead = benchmark_buffer_overhead()
    
    print("\n" + "="*60)
    print("SUMMARY")
    print("="*60)
    print(f"Buffer overhead: {overhead:.2f}μs")
    print(f"Target:          < 5.00μs")
    
    if overhead < 5.0:
        print("✅ PASS - Overhead acceptable")
    else:
        print("⚠️  WARN - Overhead higher than target")
