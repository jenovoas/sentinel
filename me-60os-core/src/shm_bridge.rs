// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛡️ SHARED MEMORY BRIDGE (ANCHOR) 🛡️
//!
//! Provides `PySharedBuffer` to anchor the Python Liquid Lattice to host RAM.
//! The POSIX shared-memory implementation is always available to native Rust
//! binaries; Python bindings are enabled only with the `extension-module`
//! feature.

use libc::{close, ftruncate, mmap, munmap, shm_open, shm_unlink};
use libc::{MAP_FAILED, MAP_SHARED, O_CREAT, O_RDWR, PROT_READ, PROT_WRITE};
use std::ffi::CString;
use std::ptr;

#[cfg(feature = "extension-module")]
use pyo3::prelude::*;
#[cfg(feature = "extension-module")]
use pyo3::types::{PyAny, PyBytes};

#[cfg_attr(feature = "extension-module", pyclass)]
pub struct PySharedBuffer {
    pub(crate) name: String,
    pub(crate) size: usize,
    pub(crate) ptr: *mut u8,
    pub(crate) fd: i32,
    pub(crate) is_owner: bool,
}

// SAFETY: synchronization is owned by the application; the mmap pointer is
// valid for the lifetime of the mapping and can be shared across threads.
unsafe impl Send for PySharedBuffer {}
unsafe impl Sync for PySharedBuffer {}

impl PySharedBuffer {
    /// Open or create a POSIX shared-memory mapping.
    pub fn new(name: String, size: usize, create: bool) -> Result<Self, String> {
        let c_name = CString::new(name.clone()).map_err(|e| format!("Invalid name: {}", e))?;

        // SAFETY: c_name is NUL-terminated; all file descriptors and mappings
        // are released on error and in Drop.
        unsafe {
            let fd = if create {
                let fd = shm_open(c_name.as_ptr(), O_CREAT | O_RDWR, 0o666);
                if fd == -1 {
                    return Err("Failed to shm_open (create)".to_string());
                }
                if ftruncate(fd, size as i64) == -1 {
                    close(fd);
                    return Err("Failed to ftruncate".to_string());
                }
                fd
            } else {
                let fd = shm_open(c_name.as_ptr(), O_RDWR, 0o666);
                if fd == -1 {
                    return Err("Failed to shm_open (open)".to_string());
                }
                fd
            };

            let mapped = mmap(
                ptr::null_mut(),
                size,
                PROT_READ | PROT_WRITE,
                MAP_SHARED,
                fd,
                0,
            );
            if mapped == MAP_FAILED {
                close(fd);
                return Err("Failed to mmap".to_string());
            }

            Ok(Self {
                name,
                size,
                ptr: mapped as *mut u8,
                fd,
                is_owner: create,
            })
        }
    }

    pub fn close(&mut self) {
        // SAFETY: fields are checked before releasing the mapping and fd.
        unsafe {
            if !self.ptr.is_null() && self.ptr != MAP_FAILED as *mut u8 {
                munmap(self.ptr as *mut libc::c_void, self.size);
                self.ptr = ptr::null_mut();
            }
            if self.fd != -1 {
                close(self.fd);
                self.fd = -1;
            }
        }
    }

    pub fn unlink(&self) {
        if self.is_owner {
            if let Ok(c_name) = CString::new(self.name.clone()) {
                // SAFETY: c_name is a valid POSIX shared-memory name.
                unsafe {
                    shm_unlink(c_name.as_ptr());
                }
            }
        }
    }
}

#[cfg(feature = "extension-module")]
#[pymethods]
impl PySharedBuffer {
    #[new]
    fn py_new(name: String, size: usize, create: bool) -> PyResult<Self> {
        Self::new(name, size, create)
            .map_err(pyo3::exceptions::PyOSError::new_err)
    }

    pub fn write(&self, offset: usize, data: &[u8]) -> PyResult<usize> {
        if offset.checked_add(data.len()).is_none_or(|end| end > self.size) {
            return Err(pyo3::exceptions::PyIndexError::new_err("Write out of bounds"));
        }
        // SAFETY: bounds are checked above and source/destination do not overlap.
        unsafe {
            ptr::copy_nonoverlapping(data.as_ptr(), self.ptr.add(offset), data.len());
        }
        Ok(data.len())
    }

    pub fn read<'py>(&self, py: Python<'py>, offset: usize, length: usize) -> PyResult<Py<PyAny>> {
        if offset.checked_add(length).is_none_or(|end| end > self.size) {
            return Err(pyo3::exceptions::PyIndexError::new_err("Read out of bounds"));
        }
        // SAFETY: bounds are checked above and the mapping is valid.
        unsafe {
            let slice = std::slice::from_raw_parts(self.ptr.add(offset), length);
            Ok(PyBytes::new(py, slice).into_any().unbind())
        }
    }

    #[pyo3(name = "close")]
    fn close_py(&mut self) {
        self.close();
    }

    #[pyo3(name = "unlink")]
    fn unlink_py(&self) {
        self.unlink();
    }
}

impl Drop for PySharedBuffer {
    fn drop(&mut self) {
        self.close();
    }
}
