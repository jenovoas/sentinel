use memmap2::{MmapMut, MmapOptions};
use std::fs::OpenOptions;

/// Shared Buffer Implementation for Zero-Copy IPC
/// Adapted from truthsync-poc for Sentinel Core.

const CONTROL_SIZE: usize = 64; // Header / Control area size

pub struct SharedBuffer {
    mmap: MmapMut,
    pub capacity: usize,
}

impl SharedBuffer {
    /// Creates a new shared memory segment.
    pub fn create(name: &str, size: usize) -> Result<Self, String> {
        let shm_path = format!("/dev/shm/{}", name);
        let file = OpenOptions::new()
            .read(true)
            .write(true)
            .create(true)
            .truncate(true)
            .open(&shm_path)
            .map_err(|e| e.to_string())?;

        // Resize file to requested size + control header
        file.set_len((size + CONTROL_SIZE) as u64)
            .map_err(|e| e.to_string())?;

        let mmap = unsafe {
            MmapOptions::new()
                .map_mut(&file)
                .map_err(|e| e.to_string())?
        };

        Ok(Self {
            mmap,
            capacity: size,
        })
    }

    /// Opens an existing shared memory segment.
    pub fn open(name: &str) -> Result<Self, String> {
        let shm_path = format!("/dev/shm/{}", name);
        let file = OpenOptions::new()
            .read(true)
            .write(true)
            .open(&shm_path)
            .map_err(|e| e.to_string())?;

        let mmap = unsafe {
            MmapOptions::new()
                .map_mut(&file)
                .map_err(|e| e.to_string())?
        };

        let capacity = mmap.len() - CONTROL_SIZE;

        Ok(Self { mmap, capacity })
    }

    /// Writes raw bytes to the buffer at offset (skipping control header).
    pub fn write_bytes(&mut self, offset: usize, data: &[u8]) -> Result<(), String> {
        if offset + data.len() > self.capacity {
            return Err("Write out of bounds".to_string());
        }

        let target = &mut self.mmap[CONTROL_SIZE + offset..CONTROL_SIZE + offset + data.len()];
        target.copy_from_slice(data);
        Ok(())
    }

    /// Reads raw bytes from the buffer.
    pub fn read_bytes(&self, offset: usize, length: usize) -> Result<Vec<u8>, String> {
        if offset + length > self.capacity {
            return Err("Read out of bounds".to_string());
        }

        let slice = &self.mmap[CONTROL_SIZE + offset..CONTROL_SIZE + offset + length];
        Ok(slice.to_vec())
    }

    /// Zeroes out the entire buffer (Control + Data).
    pub fn clear(&mut self) {
        self.mmap.fill(0);
    }

    /// Returns raw pointer to the data section (Unsafe!).
    /// Used for FFI / CUDA Memcpy.
    pub fn as_ptr(&self) -> *const u8 {
        unsafe { self.mmap.as_ptr().add(CONTROL_SIZE) }
    }

    pub fn as_mut_ptr(&mut self) -> *mut u8 {
        unsafe { self.mmap.as_mut_ptr().add(CONTROL_SIZE) }
    }
}
