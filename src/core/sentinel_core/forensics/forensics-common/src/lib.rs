#![no_std]

#[repr(C)]
#[derive(Copy, Clone)]
pub struct ProcessEvent {
    pub pid: u32,
    pub _pad: u32, // Match C padding for 8-byte alignment
    pub ts: u64,
    pub comm: [u8; 16],
}

#[cfg(feature = "user")]
unsafe impl aya::Pod for ProcessEvent {}
