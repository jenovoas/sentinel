use procfs::process::Process;
use rayon::prelude::*;
use aho_corasick::AhoCorasick;
use std::io::Read;
use std::fs::File;
use std::os::unix::fs::FileExt;

pub struct MemoryScanner {
    matcher: AhoCorasick,
}

impl MemoryScanner {
    pub fn new(patterns: Vec<&str>) -> Self {
        Self {
            matcher: AhoCorasick::new(patterns).unwrap(),
        }
    }

    /// Scan a single process for patterns in its memory
    pub fn scan_process(&self, pid: i32) -> Result<Vec<String>, String> {
        let process = Process::new(pid).map_err(|e| format!("Failed to open process {}: {}", pid, e))?;
        
        // Get executable memory maps
        let maps = process.maps().map_err(|e| format!("Failed to get maps for {}: {}", pid, e))?;
        
        let mut findings = Vec::new();
        let mem_file_path = format!("/proc/{}/mem", pid);
        let mut mem_file = File::open(&mem_file_path).map_err(|e| format!("Failed to open mem for {}: {}", pid, e))?;

        for map in maps {
            // Focus on executable or writable/private regions (common for injections)
            if map.perms.contains('x') || (map.perms.contains('w') && map.perms.contains('p')) {
                let size = (map.address.1 - map.address.0) as usize;
                if size > 10 * 1024 * 1024 { continue; } // Skip very large regions for MVP

                let mut buffer = vec![0u8; size];
                if mem_file.read_at(&mut buffer, map.address.0).is_ok() {
                    for mat in self.matcher.find_iter(&buffer) {
                        findings.push(format!("Pattern found at 0x{:x} in map {:x}-{:x}", 
                            map.address.0 + mat.start() as u64, map.address.0, map.address.1));
                    }
                }
            }
        }

        Ok(findings)
    }

    /// Scan multiple processes in parallel using Rayon
    pub fn scan_multiple(&self, pids: Vec<i32>) -> Vec<(i32, Vec<String>)> {
        pids.into_par_iter()
            .map(|pid| {
                match self.scan_process(pid) {
                    Ok(f) if !f.is_empty() => (pid, f),
                    _ => (pid, Vec::new()),
                }
            })
            .filter(|(_, f)| !f.is_empty())
            .collect()
    }
}
