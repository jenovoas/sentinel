use memmap2::{MmapMut, MmapOptions};
use std::fs::OpenOptions;

/// Message header structure
#[repr(C)]
struct MessageHeader {
    magic: u32,      // 0xDEADBEEF for validation
    msg_type: u16,   // Message type
    length: u32,     // Payload length
}

/// Message types
#[allow(dead_code)]
pub mod message_type {
    pub const PROCESS_TEXT: u16 = 0x01;
    pub const GET_RESULTS: u16 = 0x02;
    pub const CONFIGURE: u16 = 0x03;
    pub const HEALTH_CHECK: u16 = 0x04;
    pub const SHUTDOWN: u16 = 0xFF;
}

const MAGIC: u32 = 0xDEADBEEF;
const HEADER_SIZE: usize = std::mem::size_of::<MessageHeader>();
const CONTROL_SIZE: usize = 64; // Cache line aligned

pub struct SharedBuffer {
    mmap: MmapMut,
    capacity: usize,
}

impl SharedBuffer {
    pub fn create(name: &str, size: usize) -> Result<Self, String> {
        let shm_path = format!("/var/run/sentinel/{}", name);
        let file = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .truncate(true)
            .open(&shm_path)
            .map_err(|e| e.to_string())?;
        
        file.set_len((size + CONTROL_SIZE) as u64).map_err(|e| e.to_string())?;
        
        let mmap = unsafe { MmapOptions::new().map_mut(&file).map_err(|e| e.to_string())? };
        
        Ok(Self {
            mmap,
            capacity: size,
        })
    }
    
    pub fn open(name: &str) -> Result<Self, String> {
        let shm_path = format!("/var/run/sentinel/{}", name);
        let file = OpenOptions::new()
            .read(true)
            .write(true)
            .open(&shm_path)
            .map_err(|e| e.to_string())?;
        
        let mmap = unsafe { MmapOptions::new().map_mut(&file).map_err(|e| e.to_string())? };
        let capacity = mmap.len() - CONTROL_SIZE;
        
        Ok(Self {
            mmap,
            capacity,
        })
    }
    
    pub fn write(&mut self, msg_type: u16, data: &[u8]) -> Result<(), String> {
        if data.len() + HEADER_SIZE > self.capacity {
            return Err("Data too large for buffer".to_string());
        }
        
        let header = MessageHeader {
            magic: MAGIC,
            msg_type,
            length: data.len() as u32,
        };
        
        let header_bytes = unsafe {
            std::slice::from_raw_parts(
                &header as *const MessageHeader as *const u8,
                HEADER_SIZE,
            )
        };
        
        self.mmap[CONTROL_SIZE..CONTROL_SIZE + HEADER_SIZE].copy_from_slice(header_bytes);
        self.mmap[CONTROL_SIZE + HEADER_SIZE..CONTROL_SIZE + HEADER_SIZE + data.len()].copy_from_slice(data);
        
        Ok(())
    }
    
    pub fn read(&self) -> Result<(u16, Vec<u8>), String> {
        let header = unsafe {
            std::ptr::read(
                self.mmap[CONTROL_SIZE..].as_ptr() as *const MessageHeader
            )
        };
        
        if header.magic != MAGIC {
            return Err("Invalid magic number".to_string());
        }
        
        let data_start = CONTROL_SIZE + HEADER_SIZE;
        let data_end = data_start + header.length as usize;
        let data = self.mmap[data_start..data_end].to_vec();
        
        Ok((header.msg_type, data))
    }
    
    pub fn consume(&mut self) -> Result<(u16, Vec<u8>), String> {
        let (msg_type, data) = self.read()?;
        let zero: [u8; 4] = [0; 4];
        self.mmap[CONTROL_SIZE..CONTROL_SIZE + 4].copy_from_slice(&zero);
        Ok((msg_type, data))
    }

    pub fn name(&self) -> &str { "truthsync_shm" }
    pub fn capacity(&self) -> usize { self.capacity }
}
