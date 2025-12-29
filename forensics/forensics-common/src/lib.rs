#![no_std]

#[repr(C)]
#[derive(Copy, Clone)]
pub struct ProcessEvent {
    pub pid: u32,
    pub ppid: u32,
    pub comm: [u8; 16],
}

#[cfg(feature = "user")]
unsafe impl aya::Pod for ProcessEvent {}
