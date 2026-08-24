// Autor: Jaime Novoa Sepulveda — Todos los derechos reservados.
// Licencia: Apache 2.0 + Cláusula No Comercial (ver LICENSE).
// Colaboración abierta con atribución. Uso comercial PROHIBIDO sin autorización.
//! # 🛡️ SHARED MEMORY BRIDGE (ANCHOR) 🛡️
//!
//! Provides `PySharedBuffer` to anchor Python Liquid Lattice to Host RAM.
//! Uses POSIX shared memory (shm_open/mmap) via libc.
//! Reference: Posix IPC for ME-60OS.

use libc::{close, ftruncate, mmap, munmap, shm_open, shm_unlink};
use libc::{MAP_FAILED, MAP_SHARED, O_CREAT, O_RDWR, PROT_READ, PROT_WRITE};
#[cfg(feature = "extension-module")]
use pyo3::prelude::*;
use pyo3::types::{PyAny, PyBytes};
use std::ffi::CString;
use std::ptr;

#[cfg_attr(feature = "extension-module", pyclass)]
pub struct PySharedBuffer {
    pub(crate) name: String,
    pub(crate) size: usize,
    pub(crate) ptr: *mut u8,
    pub(crate) fd: i32,
    pub(crate) is_owner: bool,
}

// SAFETY: We are responsible for synchronization at the application level.
// mmap pointers are valid across threads.
unsafe impl Send for PySharedBuffer {}
unsafe impl Sync for PySharedBuffer {}

#[cfg_attr(feature = "extension-module", pymethods)]
impl PySharedBuffer {
    #[new]
    pub fn new(name: String, size: usize, create: bool) -> PyResult<Self> {
        let c_name = CString::new(name.clone()).map_err(|e| {
            PyErr::new::<pyo3::exceptions::PyValueError, _>(format!("Invalid name: {}", e))
        })?;

        // SAFETY: POSIX shm_open/ftruncate/mmap on a freshly-constructed
        // CString (null-terminated, no NUL bytes) pointed-to by
        // c_name.as_ptr(). fd leaks are prevented by close() on each
        // error path before return. mmap result is checked against
        // MAP_FAILED and the failing fd is closed. The pointer is
        // stored on Self and freed in Drop via close().
        unsafe {
            let fd;
            if create {
                fd = shm_open(c_name.as_ptr(), O_CREAT | O_RDWR, 0o666);
                if fd == -1 {
                    return Err(PyErr::new::<pyo3::exceptions::PyOSError, _>(
                        "Failed to shm_open (create)",
                    ));
                }
                if ftruncate(fd, size as i64) == -1 {
                    close(fd);
                    return Err(PyErr::new::<pyo3::exceptions::PyOSError, _>(
                        "Failed to ftruncate",
                    ));
                }
            } else {
                fd = shm_open(c_name.as_ptr(), O_RDWR, 0o666);
                if fd == -1 {
                    return Err(PyErr::new::<pyo3::exceptions::PyOSError, _>(
                        "Failed to shm_open (open)",
                    ));
                }
            }

            let ptr = mmap(
                ptr::null_mut(),
                size,
                PROT_READ | PROT_WRITE,
                MAP_SHARED,
                fd,
                0,
            );

            if ptr == MAP_FAILED {
                close(fd);
                return Err(PyErr::new::<pyo3::exceptions::PyOSError, _>(
                    "Failed to mmap",
                ));
            }

            Ok(PySharedBuffer {
                name,
                size,
                ptr: ptr as *mut u8,
                fd,
                is_owner: create,
            })
        }
    }

    pub fn write(&self, offset: usize, data: &[u8]) -> PyResult<usize> {
        if offset + data.len() > self.size {
            return Err(PyErr::new::<pyo3::exceptions::PyIndexError, _>(
                "Write out of bounds",
            ));
        }
        // SAFETY: offset+len validated against self.size above; src/dst non-overlapping; len is exact byte count
        unsafe {
            ptr::copy_nonoverlapping(data.as_ptr(), self.ptr.add(offset), data.len());
        }
        Ok(data.len())
    }

    pub fn read<'py>(&self, py: Python<'py>, offset: usize, length: usize) -> PyResult<Py<PyAny>> {
        if offset + length > self.size {
            return Err(PyErr::new::<pyo3::exceptions::PyIndexError, _>(
                "Read out of bounds",
            ));
        }
        // SAFETY: offset+length validated against self.size above; ptr.add(offset) within mapped region
        unsafe {
            let slice = std::slice::from_raw_parts(self.ptr.add(offset), length);
            let bytes = PyBytes::new(py, slice);
            Ok(bytes.into_any().unbind())
        }
    }

    pub fn close(&mut self) {
        // SAFETY: munmap and close are idempotent; null/MAP_FAILED checks guard against double-free
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
                // SAFETY: shm_unlink is idempotent POSIX; called only when is_owner=true
                unsafe {
                    shm_unlink(c_name.as_ptr());
                }
            }
        }
    }
}

impl Drop for PySharedBuffer {
    fn drop(&mut self) {
        self.close();
    }
}
