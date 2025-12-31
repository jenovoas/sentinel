use std::fs::File;
use std::io;
use std::os::unix::fs::FileExt;
use rayon::prelude::*;
use procfs::process::{Process, MMPermissions, MMapPath};
use std::sync::Arc;
use aho_corasick::AhoCorasick;

#[derive(Debug, Clone)]
pub struct MemoryRegion {
    pub start: u64,
    pub end: u64,
    pub perms: MMPermissions,
    pub pathname: MMapPath,
}

impl MemoryRegion {
    fn is_suspicious(&self) -> bool {
        // Suspicious: Writable + Executable OR Anonymous Executable (common for shellcode)
        self.perms.contains(MMPermissions::WRITE) && self.perms.contains(MMPermissions::EXECUTE) ||
        (self.perms.contains(MMPermissions::EXECUTE) && matches!(self.pathname, MMapPath::Anonymous))
    }
}

pub struct HuntResult {
    pub pid: u32,
    pub threats: Vec<MemoryRegion>,
    pub score: f32,
}

pub struct MemoryScanner {
    matcher: Arc<AhoCorasick>,
    threat_threshold: f32,
}

impl MemoryScanner {
    pub fn new() -> Self {
        let signatures = vec![
            b"AIOpsDoom".to_vec(),
            b"/bin/sh".to_vec(),
            b"execve".to_vec(),
            vec![0x90, 0x90, 0x90], // NOP sled
            b"curl.*bash".to_vec(),
        ];
        Self {
            matcher: Arc::new(AhoCorasick::new(signatures).unwrap()),
            threat_threshold: 2.0,
        }
    }

    pub fn hunt_pid(&self, pid: u32) -> Result<HuntResult, io::Error> {
        let process = Process::new(pid as i32).map_err(|e| io::Error::new(io::ErrorKind::Other, e.to_string()))?;
        let maps = process.maps().map_err(|e| io::Error::new(io::ErrorKind::Other, e.to_string()))?;
        
        let mem_path = format!("/proc/{}/mem", pid);
        let mem_file = File::open(&mem_path)?;

        // Parallel scan danger zones
        let threats: Vec<MemoryRegion> = maps.iter().par_bridge()
            .filter_map(|map| {
                let region = MemoryRegion {
                    start: map.address.0,
                    end: map.address.1,
                    perms: map.perms,
                    pathname: map.pathname.clone(),
                };

                if region.is_suspicious() {
                    if let Ok(count) = self.scan_region(&mem_file, &region) {
                        if count >= 1 { // Any match in suspicious region is a threat
                            return Some(region);
                        }
                    }
                }
                None
            })
            .collect();

        let score = threats.len() as f32;

        Ok(HuntResult {
            pid,
            threats,
            score,
        })
    }

    fn scan_region(&self, mem_file: &File, region: &MemoryRegion) -> io::Result<usize> {
        let size = (region.end - region.start) as usize;
        // Limit scan size to 20MB per region for performance
        if size > 20 * 1024 * 1024 { return Ok(0); }

        let mut buffer = vec![0u8; size];
        use std::os::unix::fs::FileExt;
        mem_file.read_at(&mut buffer, region.start)?;

        let matches = self.matcher.find_iter(&buffer).count();
        Ok(matches)
    }
}
