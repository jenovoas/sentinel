mod scanner;

use scanner::MemoryScanner;
use std::time::{Instant, Duration};
use std::sync::Arc;
use aya::programs::TracePoint;
use aya::{Bpf, include_bytes_aligned};
use aya::maps::ring_buf::RingBuf;
use forensics_common::ProcessEvent;

#[tokio::main]
async fn main() -> Result<(), Box<dyn std::error::Error>> {
    println!("🧠 [Sentinel Forensics] Starting Memory Scanner (Rayon + eBPF)");

    // 1. Load eBPF program
    let bpf_data = include_bytes_aligned!("../forensics-ebpf/target/bpfel-unknown-none/release/forensics-ebpf");

    let mut bpf = Bpf::load(bpf_data)?;
    
    // Aya identifies programs by their function name in the ELF
    let program: &mut TracePoint = bpf.program_mut("forensics")
        .expect("Program 'forensics' not found in ELF")
        .try_into()?;
        
    program.load()?;
    
    // Attach to the specific tracepoint
    // Category: syscalls, Name: sys_enter_execve
    program.attach("syscalls", "sys_enter_execve")?;

    println!("🔭 eBPF Tracepoint attached to sys_enter_execve");

    // 2. Initialize Scanner
    let patterns = vec![
        "\x31\xc0\x48\xbb\xd1\x9d\x96\x91\xd0\x8c\x97\xff\x48\xf7\xdb",
        "/bin/sh",
        "chmod +x",
    ];
    let scanner = Arc::new(MemoryScanner::new(patterns));

    // 3. Handle eBPF events via Ring Buffer
    let mut events: RingBuf<_> = bpf.map_mut("EVENTS").unwrap().try_into()?;
    
    println!("🛡️ Monitoring system for suspicious process activities...");

    loop {
        // Poll RingBuffer for events
        if let Some(event) = events.next() {
            let event: ProcessEvent = unsafe { std::ptr::read(event.as_ptr() as *const _) };
            let pid = event.pid as i32;
            let comm = String::from_utf8_lossy(&event.comm).trim_matches(char::from(0)).to_string();
            
            // Trigger parallel scan with Rayon
            let scanner_clone = scanner.clone();
            tokio::spawn(async move {
                let start = Instant::now();
                match scanner_clone.scan_process(pid) {
                    Ok(findings) if !findings.is_empty() => {
                        println!("⚠️ [ALERT] Suspicious activity detected in PID {} ({}):", pid, comm);
                        for finding in findings {
                            println!("  - {}", finding);
                        }
                        println!("⏱️ Scan completed in {:?}", start.elapsed());
                    },
                    _ => {} // Clean process or error (process might have exited)
                }
            });
        }
        
        tokio::task::yield_now().await;
    }
}
