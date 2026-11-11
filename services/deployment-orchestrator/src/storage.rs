use serde_json::Value;
use std::{
    ffi::CString,
    fs::{self, OpenOptions},
    io::Write,
    os::unix::{
        fs::{MetadataExt, OpenOptionsExt, PermissionsExt},
        io::AsRawFd,
    },
    path::{Path, PathBuf},
    process::Command,
};

const IMAGE_ROOT: &str = "/var/lib/sentinel/tenant-storage";
const MOUNT_ROOT: &str = "/srv/sentinel/tenants";
const UNIT_ROOT: &str = "/etc/systemd/system";
const BLOCK_BYTES: u64 = 4096;

#[derive(Debug, Clone)]
pub struct StoragePreflight {
    pub mount_path: String,
    pub filesystem_bytes: i64,
    pub host_free_bytes: i64,
}

fn command(binary: &str, args: &[&str]) -> Result<Vec<u8>, &'static str> {
    let output = Command::new(binary)
        .env_clear()
        .env("PATH", "/usr/bin:/bin")
        .args(args)
        .output()
        .map_err(|_| "storage command failed to start")?;
    if output.status.success() {
        Ok(output.stdout)
    } else {
        Err("storage command failed")
    }
}

fn no_symlink(path: &Path) -> Result<(), &'static str> {
    if !path.is_absolute() {
        return Err("storage path is not absolute");
    }
    let mut current = PathBuf::from("/");
    for part in path.components().skip(1) {
        current.push(part);
        match fs::symlink_metadata(&current) {
            Ok(metadata) if metadata.file_type().is_symlink() => {
                return Err("storage path contains a symlink");
            }
            Ok(_) => {}
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(()),
            Err(_) => return Err("storage path cannot be inspected"),
        }
    }
    Ok(())
}

fn secure_directory(path: &Path, mode: u32) -> Result<(), &'static str> {
    no_symlink(path)?;
    fs::create_dir_all(path).map_err(|_| "storage directory cannot be created")?;
    let metadata =
        fs::symlink_metadata(path).map_err(|_| "storage directory cannot be inspected")?;
    if !metadata.is_dir()
        || metadata.uid() != unsafe { libc::geteuid() }
        || metadata.mode() & 0o022 != 0
    {
        return Err("storage directory ownership or mode is unsafe");
    }
    if metadata.mode() & 0o777 != mode {
        fs::set_permissions(path, fs::Permissions::from_mode(mode))
            .map_err(|_| "storage directory mode cannot be set")?;
    }
    Ok(())
}

fn statvfs(path: &Path) -> Result<(u64, u64), &'static str> {
    let name = CString::new(path.to_str().ok_or("storage path is not UTF-8")?)
        .map_err(|_| "storage path contains a NUL byte")?;
    let mut info: libc::statvfs = unsafe { std::mem::zeroed() };
    if unsafe { libc::statvfs(name.as_ptr(), &mut info) } != 0 {
        return Err("storage filesystem statistics unavailable");
    }
    let capacity = (info.f_blocks as u128)
        .checked_mul(info.f_frsize as u128)
        .ok_or("storage capacity overflow")?;
    let available = (info.f_bavail as u128)
        .checked_mul(info.f_frsize as u128)
        .ok_or("storage free-space overflow")?;
    Ok((
        u64::try_from(capacity).map_err(|_| "storage capacity out of range")?,
        u64::try_from(available).map_err(|_| "storage free-space out of range")?,
    ))
}

fn verify_image(path: &Path, size: u64) -> Result<(), &'static str> {
    no_symlink(path)?;
    let metadata = fs::symlink_metadata(path).map_err(|_| "tenant storage image is missing")?;
    if !metadata.is_file()
        || metadata.uid() != unsafe { libc::geteuid() }
        || metadata.mode() & 0o077 != 0
        || metadata.size() != size
        || metadata.blocks().saturating_mul(512) < size
    {
        return Err("tenant storage image size, ownership, mode, or allocation is invalid");
    }
    let image = path.to_str().ok_or("storage image path is not UTF-8")?;
    let kind = String::from_utf8(command(
        "/usr/sbin/blkid",
        &["-p", "-s", "TYPE", "-o", "value", image],
    )?)
    .map_err(|_| "storage image type is not UTF-8")?;
    if kind.trim() != "ext4" {
        return Err("tenant storage image is not ext4");
    }
    Ok(())
}

fn make_image(path: &Path, size: u64, min_free: u64) -> Result<(), &'static str> {
    if path.exists() {
        return verify_image(path, size);
    }
    let parent = path.parent().ok_or("storage image has no parent")?;
    let (_, available) = statvfs(parent)?;
    if available < size.saturating_add(min_free) {
        return Err("insufficient host storage headroom");
    }

    let temporary = parent.join(format!(".tenant-storage-{}", uuid::Uuid::new_v4()));
    let temporary_text = temporary
        .to_str()
        .ok_or("temporary storage path is not UTF-8")?;
    let file = OpenOptions::new()
        .write(true)
        .create_new(true)
        .mode(0o600)
        .open(&temporary)
        .map_err(|_| "temporary storage image cannot be created")?;
    drop(file);

    let result = (|| {
        command(
            "/usr/bin/fallocate",
            &["--length", &size.to_string(), temporary_text],
        )?;
        let metadata = fs::symlink_metadata(&temporary)
            .map_err(|_| "temporary storage image cannot be inspected")?;
        if metadata.size() != size || metadata.blocks().saturating_mul(512) < size {
            return Err("temporary storage image is sparse");
        }
        command(
            "/usr/sbin/mkfs.ext4",
            &["-F", "-m", "0", "-E", "nodiscard", temporary_text],
        )?;
        command(
            "/usr/bin/fallocate",
            &["--length", &size.to_string(), temporary_text],
        )?;
        let file = OpenOptions::new()
            .read(true)
            .open(&temporary)
            .map_err(|_| "temporary storage image cannot be opened")?;
        if unsafe { libc::fsync(file.as_raw_fd()) } != 0 {
            return Err("temporary storage image cannot be synced");
        }
        verify_image(&temporary, size)?;
        fs::hard_link(&temporary, path).map_err(|_| "tenant storage image already exists")?;
        let directory = OpenOptions::new()
            .read(true)
            .open(parent)
            .map_err(|_| "storage directory cannot be opened")?;
        if unsafe { libc::fsync(directory.as_raw_fd()) } != 0 {
            return Err("storage directory cannot be synced");
        }
        verify_image(path, size)
    })();
    let cleanup =
        fs::remove_file(&temporary).map_err(|_| "temporary storage image cannot be removed");
    result?;
    cleanup?;
    Ok(())
}

fn mount_unit(tenant: &str, image: &Path, mount: &Path) -> Result<String, &'static str> {
    let mount_text = mount.to_str().ok_or("mount path is not UTF-8")?;
    let escaped = String::from_utf8(command(
        "/usr/bin/systemd-escape",
        &["--path", "--suffix=mount", mount_text],
    )?)
    .map_err(|_| "systemd unit name is not UTF-8")?;
    let unit = escaped.trim();
    if unit.is_empty() || unit.contains('/') || !unit.ends_with(".mount") {
        return Err("invalid tenant mount unit name");
    }
    let unit_path = Path::new(UNIT_ROOT).join(unit);
    let content = format!(
        "[Unit]\nDescription=Almacenamiento tenant {tenant}\n\n[Mount]\nWhat={}\nWhere={mount_text}\nType=ext4\nOptions=loop,nodev,nosuid\n\n[Install]\nWantedBy=local-fs.target\n",
        image.display()
    );
    if unit_path.exists() {
        no_symlink(&unit_path)?;
        let metadata = fs::symlink_metadata(&unit_path)
            .map_err(|_| "tenant mount unit cannot be inspected")?;
        if !metadata.is_file()
            || metadata.uid() != unsafe { libc::geteuid() }
            || metadata.mode() & 0o022 != 0
            || fs::read_to_string(&unit_path).map_err(|_| "tenant mount unit cannot be read")?
                != content
        {
            return Err("tenant mount unit differs from the fixed configuration");
        }
    } else {
        let temporary =
            Path::new(UNIT_ROOT).join(format!(".tenant-mount-{}", uuid::Uuid::new_v4()));
        let mut file = OpenOptions::new()
            .write(true)
            .create_new(true)
            .mode(0o644)
            .open(&temporary)
            .map_err(|_| "tenant mount unit cannot be created")?;
        file.write_all(content.as_bytes())
            .map_err(|_| "tenant mount unit cannot be written")?;
        file.sync_all()
            .map_err(|_| "tenant mount unit cannot be synced")?;
        fs::hard_link(&temporary, &unit_path).map_err(|_| "tenant mount unit already exists")?;
        fs::remove_file(&temporary).map_err(|_| "temporary mount unit cannot be removed")?;
        let directory = OpenOptions::new()
            .read(true)
            .open(UNIT_ROOT)
            .map_err(|_| "systemd unit directory cannot be opened")?;
        directory
            .sync_all()
            .map_err(|_| "systemd unit directory cannot be synced")?;
    }
    Ok(unit.to_owned())
}

fn mounted_at(path: &str) -> Result<usize, &'static str> {
    let mountinfo =
        fs::read_to_string("/proc/self/mountinfo").map_err(|_| "mount table cannot be read")?;
    Ok(mountinfo
        .lines()
        .filter(|line| line.split_whitespace().nth(4) == Some(path))
        .count())
}
fn verify_active_mount(mount_text: &str, image: &Path) -> Result<(), &'static str> {
    let mount_info = String::from_utf8(command(
        "/usr/bin/findmnt",
        &[
            "--raw",
            "--noheadings",
            "--output",
            "FSTYPE,SOURCE",
            "--target",
            mount_text,
        ],
    )?)
    .map_err(|_| "mounted filesystem information is not UTF-8")?;
    let fields: Vec<_> = mount_info.split_whitespace().collect();
    if fields.len() != 2 || fields[0] != "ext4" || !fields[1].starts_with("/dev/loop") {
        return Err("tenant filesystem is not the required ext4 loop mount");
    }
    let loops: Value = serde_json::from_slice(&command(
        "/usr/sbin/losetup",
        &["--json", "--output", "NAME,BACK-FILE"],
    )?)
    .map_err(|_| "loop device inventory is invalid")?;
    let linked = loops
        .get("loopdevices")
        .and_then(Value::as_array)
        .is_some_and(|devices| {
            devices.iter().any(|device| {
                device.get("name").and_then(Value::as_str) == Some(fields[1])
                    && device.get("back-file").and_then(Value::as_str) == image.to_str()
            })
        });
    if !linked {
        return Err("tenant loop device does not reference its fixed image");
    }
    Ok(())
}

pub fn ensure_tenant_storage(
    tenant: &str,
    size: i64,
    min_free: i64,
) -> Result<StoragePreflight, &'static str> {
    if !crate::valid_storage_tenant_id(tenant)
        || unsafe { libc::geteuid() } != 0
        || size <= 0
        || min_free < 0
        || !(size as u64).is_multiple_of(BLOCK_BYTES)
    {
        return Err("invalid tenant storage request or runner is not root");
    }

    let image_root = Path::new(IMAGE_ROOT);
    let mount_root = Path::new(MOUNT_ROOT);
    secure_directory(image_root, 0o750)?;
    secure_directory(mount_root, 0o750)?;
    secure_directory(Path::new(UNIT_ROOT), 0o755)?;

    let image = image_root.join(format!("{tenant}.ext4"));
    let mount = mount_root.join(tenant);
    let mount_text = mount.to_str().ok_or("mount path is not UTF-8")?;
    no_symlink(&image)?;
    no_symlink(&mount)?;
    let active_mounts = mounted_at(mount_text)?;
    if active_mounts > 1 || (active_mounts == 1 && !image.exists()) {
        return Err("tenant mount state is ambiguous");
    }
    if active_mounts == 0 {
        match fs::symlink_metadata(&mount) {
            Ok(metadata) => {
                if !metadata.is_dir()
                    || metadata.uid() != unsafe { libc::geteuid() }
                    || metadata.mode() & 0o022 != 0
                    || fs::read_dir(&mount)
                        .map_err(|_| "tenant mount directory cannot be read")?
                        .next()
                        .is_some()
                {
                    return Err("unmounted tenant directory is not empty and safe");
                }
            }
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => {
                fs::create_dir(&mount).map_err(|_| "tenant mount directory cannot be created")?;
                fs::set_permissions(&mount, fs::Permissions::from_mode(0o750))
                    .map_err(|_| "tenant mount directory mode cannot be set")?;
            }
            Err(_) => return Err("tenant mount directory cannot be inspected"),
        }
    } else {
        let metadata = fs::symlink_metadata(&mount)
            .map_err(|_| "active tenant mount directory cannot be inspected")?;
        if !metadata.is_dir() || metadata.uid() != unsafe { libc::geteuid() } {
            return Err("active tenant mount directory ownership is unsafe");
        }
    }

    make_image(&image, size as u64, min_free as u64)?;
    if active_mounts == 1 {
        verify_active_mount(mount_text, &image)?;
    }
    let unit = mount_unit(tenant, &image, &mount)?;
    command("/usr/bin/systemctl", &["daemon-reload"])?;
    command("/usr/bin/systemctl", &["enable", "--now", &unit])?;

    verify_active_mount(mount_text, &image)?;

    let (filesystem_bytes, _) = statvfs(&mount)?;
    let (_, host_free_bytes) = statvfs(image_root)?;
    if filesystem_bytes == 0 || filesystem_bytes > size as u64 || host_free_bytes < min_free as u64
    {
        return Err("tenant storage capacity or host headroom is outside its limit");
    }
    Ok(StoragePreflight {
        mount_path: mount_text.to_owned(),
        filesystem_bytes: i64::try_from(filesystem_bytes)
            .map_err(|_| "tenant filesystem size is out of range")?,
        host_free_bytes: i64::try_from(host_free_bytes)
            .map_err(|_| "host free space is out of range")?,
    })
}

#[cfg(test)]
mod tests {
    use super::{make_image, verify_image};
    use std::{fs, os::unix::fs::MetadataExt, path::PathBuf};

    fn image_path(label: &str) -> PathBuf {
        std::env::temp_dir().join(format!(
            "tenant-compute-{label}-{}.ext4",
            uuid::Uuid::new_v4()
        ))
    }

    #[test]
    fn creates_a_preallocated_ext4_image_and_reuses_only_exact_size() {
        let image = image_path("storage-test");
        let size = 32 * 1024 * 1024;
        make_image(&image, size, 0).expect("create ext4 image");
        let metadata = fs::symlink_metadata(&image).expect("inspect ext4 image");
        assert_eq!(metadata.size(), size);
        assert!(metadata.blocks().saturating_mul(512) >= size);
        verify_image(&image, size).expect("verify ext4 image");
        make_image(&image, size, 0).expect("idempotent image check");
        assert!(make_image(&image, size + 4096, 0).is_err());
        fs::remove_file(image).expect("remove test image");
    }

    #[test]
    fn rejects_sparse_storage_image() {
        let image = image_path("sparse-test");
        let file = fs::File::create(&image).expect("create sparse image");
        file.set_len(32 * 1024 * 1024).expect("size sparse image");
        assert!(verify_image(&image, 32 * 1024 * 1024).is_err());
        fs::remove_file(image).expect("remove sparse image");
    }
}
