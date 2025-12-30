use procfs::process::Process;
use rayon::prelude::*;
use aho_corasick::AhoCorasick;
// use std::io::Read; // Unused
use std::fs::File;
use std::os::unix::fs::FileExt;

pub struct MemoryScanner {
    matcher: AhoCorasick,
}

impl MemoryScanner {
    pub fn new<P, T>(patterns: P) -> Self 
    where 
        P: IntoIterator<Item = T>,
        T: AsRef<[u8]>,
    {
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
        let mem_file = File::open(&mem_file_path).map_err(|e| format!("Failed to open mem for {}: {}", pid, e))?;

        // Parallelize region scanning with Rayon
        let results: Vec<String> = maps.iter().par_bridge().filter_map(|map| {
            use procfs::process::{MMPermissions, MMapPath};
            
            let mut local_findings = Vec::new();
            
            // Heuristic 1: W^X Violation (Writable + Executable) - High Risk
            if map.perms.contains(MMPermissions::WRITE) && map.perms.contains(MMPermissions::EXECUTE) {
                local_findings.push(format!("W^X Violation in map {:x}-{:x}", map.address.0, map.address.1));
            }

            // Heuristic 2: Anonymous Executable memory (Common for Shellcode)
            let is_anon_exec = map.perms.contains(MMPermissions::EXECUTE) && matches!(map.pathname, MMapPath::Anonymous);
            if is_anon_exec {
                // Potential shellcode staging area
            }

            // Heuristic 3: Suspicious permission combinations
            let is_suspicious_perm = map.perms.contains(MMPermissions::EXECUTE) || 
                                    (map.perms.contains(MMPermissions::WRITE) && map.perms.contains(MMPermissions::PRIVATE));

            if is_suspicious_perm {
                // Skip standard library/system paths
                if let MMapPath::Path(path) = &map.pathname {
                    let path_str = path.to_string_lossy();
                    if path_str.contains("/usr/") || path_str.contains("/lib/") {
                        return if local_findings.is_empty() { None } else { Some(local_findings.join("|")) };
                    }
                }

                let size = (map.address.1 - map.address.0) as usize;
                if size > 20 * 1024 * 1024 { return if local_findings.is_empty() { None } else { Some(local_findings.join("|")) }; } // 20MB limit

                let mut buffer = vec![0u8; size];
                if mem_file.read_at(&mut buffer, map.address.0).is_ok() {
                    // Heuristic 4: Process Hollowing (Mismatch between file header and memory)
                    if let MMapPath::Path(_path) = &map.pathname {
                        if map.perms.contains(MMPermissions::EXECUTE) && buffer.len() > 4 {
                            // Basic check: file-backed executable mapping should start with ELF magic
                            if &buffer[0..4] != b"\x7fELF" {
                                local_findings.push(format!("Potential Process Hollowing: Non-ELF magic in executable map {:x}", map.address.0));
                            }
                        }
                    }

                    // Aho-Corasick Shellcode scanning
                    if self.matcher.find_iter(&buffer).next().is_some() {
                        local_findings.push(format!("Malicious Pattern found in {:x}-{:x} ({:?})", 
                            map.address.0, map.address.1, map.pathname));
                    }
                }
            }

            if local_findings.is_empty() {
                None
            } else {
                Some(local_findings.join("|"))
            }
        }).collect();

        for result in results {
            let split_results: Vec<&str> = result.split('|').collect();
            for finding in split_results {
                findings.push(finding.to_string());
            }
        }

        Ok(findings)
    }

    /// Scan multiple processes in parallel using Rayon
    #[allow(dead_code)]
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
