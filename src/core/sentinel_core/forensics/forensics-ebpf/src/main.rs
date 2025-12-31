#![no_std]
#![no_main]

use aya_ebpf::{
    macros::{tracepoint, map},
    maps::RingBuf,
    programs::TracePointContext,
    EbpfContext,
};
use forensics_common::ProcessEvent;

#[map]
static EVENTS: RingBuf = RingBuf::with_byte_size(256 * 1024, 0);

#[tracepoint]
pub fn forensics(ctx: TracePointContext) -> u32 {
    match try_forensics(ctx) {
        Ok(ret) => ret,
        Err(ret) => ret,
    }
}

fn try_forensics(ctx: TracePointContext) -> Result<u32, u32> {
    if let Some(mut event_buf) = EVENTS.reserve::<ProcessEvent>(0) {
        let event_ptr = event_buf.as_mut_ptr();
        
        unsafe {
            (*event_ptr).pid = ctx.pid();
            (*event_ptr).ppid = 0; // Simplified
            (*event_ptr).comm = ctx.command().unwrap_or([0u8; 16]);
        }
        
        event_buf.submit(0);
    }

    Ok(0)
}

#[panic_handler]
fn panic(_info: &core::panic::PanicInfo) -> ! {
    loop {}
}
