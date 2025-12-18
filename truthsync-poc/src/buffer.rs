use std::sync::atomic::{AtomicU64, AtomicU8, Ordering};
use std::sync::Arc;
use shared_memory::{Shmem, ShmemConf};

/// Shared memory buffer for Rust-Python communication
pub struct SharedBuffer {
    shmem: Shmem,
    capacity: usize,
}

/// Message header structure
#[repr(C)]
struct MessageHeader {
    magic: u32,      // 0xDEADBEEF for validation
    msg_type: u16,   // Message type
    length: u32,     // Payload length
}

/// Message types
#[allow(dead_code)]
pub mod MessageType {
    pub const PROCESS_TEXT: u16 = 0x01;
    pub const GET_RESULTS: u16 = 0x02;
    pub const CONFIGURE: u16 = 0x03;
    pub const HEALTH_CHECK: u16 = 0x04;
    pub const SHUTDOWN: u16 = 0xFF;
}

const MAGIC: u32 = 0xDEADBEEF;
const HEADER_SIZE: usize = std::mem::size_of::<MessageHeader>();
const CONTROL_SIZE: usize = 64; // Cache line aligned

impl SharedBuffer {
    /// Create a new shared memory buffer
    pub fn create(name: &str, size: usize) -> Result<Self, String> {
        let shmem = ShmemConf::new()
            .size(size + CONTROL_SIZE)
            .flink(name)
            .create()
            .map_err(|e| format!("Failed to create shared memory: {}", e))?;
        
        Ok(Self {
            shmem,
            capacity: size,
        })
    }
    
    /// Open existing shared memory buffer
    pub fn open(name: &str) -> Result<Self, String> {
        let shmem = ShmemConf::new()
            .flink(name)
            .open()
            .map_err(|e| format!("Failed to open shared memory: {}", e))?;
        
        let capacity = shmem.len() - CONTROL_SIZE;
        
        Ok(Self {
            shmem,
            capacity,
        })
    }
    
    /// Write data to buffer
    pub fn write(&mut self, msg_type: u16, data: &[u8]) -> Result<(), String> {
        if data.len() + HEADER_SIZE > self.capacity {
            return Err("Data too large for buffer".to_string());
        }
        
        // Create header
        let header = MessageHeader {
            magic: MAGIC,
            msg_type,
            length: data.len() as u32,
        };
        
        // Write header
        let header_bytes = unsafe {
            std::slice::from_raw_parts(
                &header as *const MessageHeader as *const u8,
                HEADER_SIZE,
            )
        };
        
        let buffer = unsafe { self.shmem.as_slice_mut() };
        buffer[CONTROL_SIZE..CONTROL_SIZE + HEADER_SIZE].copy_from_slice(header_bytes);
        
        // Write data
        buffer[CONTROL_SIZE + HEADER_SIZE..CONTROL_SIZE + HEADER_SIZE + data.len()]
            .copy_from_slice(data);
        
        Ok(())
    }
    
    /// Read data from buffer
    pub fn read(&self) -> Result<(u16, Vec<u8>), String> {
        let buffer = unsafe { self.shmem.as_slice() };
        
        // Read header
        let header = unsafe {
            std::ptr::read(
                buffer[CONTROL_SIZE..].as_ptr() as *const MessageHeader
            )
        };
        
        // Validate magic
        if header.magic != MAGIC {
            return Err("Invalid magic number".to_string());
        }
        
        // Read data
        let data_start = CONTROL_SIZE + HEADER_SIZE;
        let data_end = data_start + header.length as usize;
        let data = buffer[data_start..data_end].to_vec();
        
        Ok((header.msg_type, data))
    }
    
    /// Get buffer name
    pub fn name(&self) -> &str {
        self.shmem.get_flink_path()
            .and_then(|p| p.to_str())
            .unwrap_or("unknown")
    }
    
    /// Get buffer capacity
    pub fn capacity(&self) -> usize {
        self.capacity
    }
}

impl Drop for SharedBuffer {
    fn drop(&mut self) {
        // Cleanup is automatic with shared_memory crate
    }
}

#[cfg(test)]
mod tests {
    use super::*;
    
    #[test]
    fn test_buffer_create_write_read() {
        let buffer_name = "test_buffer";
        
        // Create and write
        {
            let mut buffer = SharedBuffer::create(buffer_name, 1024 * 1024)
                .expect("Failed to create buffer");
            
            let test_data = b"Hello from Rust!";
            buffer.write(MessageType::PROCESS_TEXT, test_data)
                .expect("Failed to write");
        }
        
        // Open and read
        {
            let buffer = SharedBuffer::open(buffer_name)
                .expect("Failed to open buffer");
            
            let (msg_type, data) = buffer.read()
                .expect("Failed to read");
            
            assert_eq!(msg_type, MessageType::PROCESS_TEXT);
            assert_eq!(data, b"Hello from Rust!");
        }
    }
}
