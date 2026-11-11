use crate::{connect, valid_storage_tenant_id, Settings};
use serde::Deserialize;
use std::{
    fs,
    os::unix::fs::{FileTypeExt, MetadataExt},
    path::{Path, PathBuf},
    process::Command,
};

const IMAGE_ROOT: &str = "/var/lib/sentinel/tenant-storage";
const MOUNT_ROOT: &str = "/srv/sentinel/tenants";
const UNIT_ROOT: &str = "/etc/systemd/system";

#[derive(Deserialize)]
struct LoopDevices {
    loopdevices: Vec<LoopDevice>,
}
#[derive(Deserialize)]
struct LoopDevice {
    name: String,
    #[serde(rename = "back-file")]
    back_file: String,
}

fn tenant_paths(tenant: &str) -> Result<(PathBuf, PathBuf, String, PathBuf), &'static str> {
    if !valid_storage_tenant_id(tenant) {
        return Err("invalid_tenant_id");
    }
    let image = Path::new(IMAGE_ROOT).join(format!("{tenant}.ext4"));
    let mount = Path::new(MOUNT_ROOT).join(tenant);
    let escaped = Command::new("/usr/bin/systemd-escape")
        .env_clear()
        .env("PATH", "/usr/bin:/bin")
        .arg("--path")
        .arg("--suffix=mount")
        .arg(&mount)
        .output()
        .map_err(|_| "systemd_escape_unavailable")?;
    if !escaped.status.success() {
        return Err("systemd_escape_failed");
    }
    let unit = String::from_utf8(escaped.stdout)
        .map_err(|_| "invalid_systemd_unit")?
        .trim()
        .to_string();
    if unit.is_empty() || unit.contains('/') || !unit.ends_with(".mount") {
        return Err("invalid_systemd_unit");
    }
    let unit_path = Path::new(UNIT_ROOT).join(&unit);
    Ok((image, mount, unit, unit_path))
}

fn path_has_symlink(path: &Path) -> Result<bool, &'static str> {
    let mut current = PathBuf::from("/");
    for component in path.components().skip(1) {
        current.push(component);
        match fs::symlink_metadata(&current) {
            Ok(metadata) if metadata.file_type().is_symlink() => return Ok(true),
            Ok(_) => (),
            Err(error) if error.kind() == std::io::ErrorKind::NotFound => return Ok(false),
            Err(_) => return Err("path_inspection_failed"),
        }
    }
    Ok(false)
}

fn command_output(binary: &str, args: &[&str]) -> Result<Vec<u8>, &'static str> {
    let output = Command::new(binary)
        .env_clear()
        .env("PATH", "/usr/bin:/bin")
        .args(args)
        .output()
        .map_err(|_| "host_check_unavailable")?;
    if !output.status.success() {
        return Err("host_check_failed");
    }
    Ok(output.stdout)
}

fn mounts_for_tenant(mount: &Path, image: &Path) -> Result<String, &'static str> {
    if path_has_symlink(mount)? || path_has_symlink(image)? {
        return Err("storage_path_symlink");
    }
    let mount_text =
        fs::read_to_string("/proc/self/mountinfo").map_err(|_| "mountinfo_unavailable")?;
    let expected_mount = mount.to_str().ok_or("invalid_mount_path")?;
    let expected_image = image.to_str().ok_or("invalid_image_path")?;
    let mut found: Option<String> = None;
    for line in mount_text.lines() {
        let (left, right) = line.split_once(" - ").ok_or("invalid_mountinfo")?;
        let left: Vec<_> = left.split_whitespace().collect();
        let right: Vec<_> = right.split_whitespace().collect();
        if left.len() < 5 || right.len() < 2 {
            return Err("invalid_mountinfo");
        }
        let point = decode_mount_field(left[4])?;
        if point == expected_mount {
            if found.is_some() || right[0] != "ext4" || !right[1].starts_with("/dev/loop") {
                return Err("unexpected_tenant_mount");
            }
            found = Some(right[1].to_string());
        } else if point.starts_with(&format!("{expected_mount}/")) {
            return Err("nested_tenant_mount");
        }
    }
    let loop_device = found.ok_or("tenant_mount_not_active")?;
    let blkid = command_output(
        "/usr/sbin/blkid",
        &["-p", "-s", "TYPE", "-o", "value", expected_image],
    )?;
    if String::from_utf8_lossy(&blkid).trim() != "ext4" {
        return Err("tenant_image_not_ext4");
    }
    let raw = command_output(
        "/usr/sbin/losetup",
        &["--json", "--output", "NAME,BACK-FILE"],
    )?;
    let devices: LoopDevices = serde_json::from_slice(&raw).map_err(|_| "loop_devices_invalid")?;
    let associated = devices
        .loopdevices
        .iter()
        .any(|device| device.name == loop_device && Path::new(&device.back_file) == image);
    if !associated {
        return Err("tenant_loop_image_mismatch");
    }
    Ok(loop_device)
}

fn decode_mount_field(field: &str) -> Result<String, &'static str> {
    let mut decoded = Vec::with_capacity(field.len());
    let bytes = field.as_bytes();
    let mut index = 0;
    while index < bytes.len() {
        if bytes[index] == b'\\' {
            if index + 3 >= bytes.len() {
                return Err("invalid_mount_escape");
            }
            let escape = &bytes[index + 1..index + 4];
            let value = match escape {
                b"040" => b' ',
                b"011" => b'\t',
                b"012" => b'\n',
                b"134" => b'\\',
                _ => return Err("invalid_mount_escape"),
            };
            decoded.push(value);
            index += 4;
        } else {
            decoded.push(bytes[index]);
            index += 1;
        }
    }
    String::from_utf8(decoded).map_err(|_| "invalid_mount_path")
}

async fn check_no_docker_references(settings: &Settings, mount: &Path) -> Result<(), &'static str> {
    let socket =
        fs::symlink_metadata(&settings.docker_socket).map_err(|_| "docker_socket_unavailable")?;
    if socket.file_type().is_symlink() || !socket.file_type().is_socket() {
        return Err("docker_socket_invalid");
    }
    let host = format!("unix://{}", settings.docker_socket.display());
    let list = Command::new("/usr/bin/docker")
        .env_clear()
        .env("PATH", "/usr/bin:/bin")
        .env("DOCKER_HOST", &host)
        .arg("container")
        .arg("ls")
        .arg("--all")
        .arg("--quiet")
        .arg("--no-trunc")
        .output()
        .map_err(|_| "docker_daemon_unavailable")?;
    if !list.status.success() {
        return Err("docker_daemon_unavailable");
    }
    let ids = String::from_utf8(list.stdout).map_err(|_| "docker_ids_invalid")?;
    let ids: Vec<_> = ids.lines().filter(|id| !id.is_empty()).collect();
    if ids
        .iter()
        .any(|id| id.len() < 12 || id.len() > 64 || !id.bytes().all(|b| b.is_ascii_hexdigit()))
    {
        return Err("docker_ids_invalid");
    }
    if ids.is_empty() {
        return Ok(());
    }
    let inspect = Command::new("/usr/bin/docker")
        .env_clear()
        .env("PATH", "/usr/bin:/bin")
        .env("DOCKER_HOST", &host)
        .arg("container")
        .arg("inspect")
        .arg("--format={{json .Mounts}}")
        .args(&ids)
        .output()
        .map_err(|_| "docker_inspect_unavailable")?;
    if !inspect.status.success() {
        return Err("docker_inspect_unavailable");
    }
    let expected = mount.to_str().ok_or("invalid_mount_path")?;
    let reports = String::from_utf8(inspect.stdout).map_err(|_| "docker_mounts_invalid")?;
    for report in reports.lines() {
        let mounts: serde_json::Value =
            serde_json::from_str(report).map_err(|_| "docker_mounts_invalid")?;
        let Some(mounts) = mounts.as_array() else {
            if mounts.is_null() {
                continue;
            }
            return Err("docker_mounts_invalid");
        };
        for entry in mounts {
            if let Some(source) = entry.get("Source").and_then(serde_json::Value::as_str) {
                if source == expected || source.starts_with(&format!("{expected}/")) {
                    return Err("tenant_storage_in_use_by_container");
                }
            }
        }
    }
    Ok(())
}

fn verify_generated_unit(
    tenant: &str,
    image: &Path,
    mount: &Path,
    unit_path: &Path,
) -> Result<(), &'static str> {
    if path_has_symlink(unit_path)? {
        return Err("tenant_unit_symlink");
    }
    let metadata = fs::symlink_metadata(unit_path).map_err(|_| "tenant_unit_missing")?;
    if !metadata.is_file() || metadata.uid() != 0 || metadata.mode() & 0o022 != 0 {
        return Err("tenant_unit_untrusted");
    }
    let image = image.to_str().ok_or("invalid_image_path")?;
    let mount = mount.to_str().ok_or("invalid_mount_path")?;
    let expected = format!("[Unit]\nDescription=Almacenamiento tenant {tenant}\n\n[Mount]\nWhat={image}\nWhere={mount}\nType=ext4\nOptions=loop,nodev,nosuid\n\n[Install]\nWantedBy=local-fs.target\n");
    if fs::read_to_string(unit_path).map_err(|_| "tenant_unit_unreadable")? != expected {
        return Err("tenant_unit_mismatch");
    }
    Ok(())
}

fn exists_lstat(path: &Path) -> Result<bool, &'static str> {
    match fs::symlink_metadata(path) {
        Ok(_) => Ok(true),
        Err(error) if error.kind() == std::io::ErrorKind::NotFound => Ok(false),
        Err(_) => Err("path_inspection_failed"),
    }
}

fn ensure_no_mount_at_or_below(mount: &Path) -> Result<(), &'static str> {
    let mountinfo =
        fs::read_to_string("/proc/self/mountinfo").map_err(|_| "mountinfo_unavailable")?;
    let expected = mount.to_str().ok_or("invalid_mount_path")?;
    for line in mountinfo.lines() {
        let (left, _) = line.split_once(" - ").ok_or("invalid_mountinfo")?;
        let fields: Vec<_> = left.split_whitespace().collect();
        if fields.len() < 5 {
            return Err("invalid_mountinfo");
        }
        let point = decode_mount_field(fields[4])?;
        if point == expected || point.starts_with(&format!("{expected}/")) {
            return Err("tenant_mount_still_active");
        }
    }
    Ok(())
}
fn is_mount_at_or_below(mount: &Path) -> Result<bool, &'static str> {
    let mountinfo =
        fs::read_to_string("/proc/self/mountinfo").map_err(|_| "mountinfo_unavailable")?;
    let expected = mount.to_str().ok_or("invalid_mount_path")?;
    for line in mountinfo.lines() {
        let (left, _) = line.split_once(" - ").ok_or("invalid_mountinfo")?;
        let fields: Vec<_> = left.split_whitespace().collect();
        if fields.len() < 5 {
            return Err("invalid_mountinfo");
        }
        let point = decode_mount_field(fields[4])?;
        if point == expected || point.starts_with(&format!("{expected}/")) {
            return Ok(true);
        }
    }
    Ok(false)
}

fn image_has_loop_reference(image: &Path) -> Result<bool, &'static str> {
    let loops: LoopDevices = serde_json::from_slice(&command_output(
        "/usr/sbin/losetup",
        &["--json", "--output", "NAME,BACK-FILE"],
    )?)
    .map_err(|_| "loop_devices_invalid")?;
    let expected = image.to_str().ok_or("invalid_image_path")?;
    Ok(loops.loopdevices.iter().any(|device| {
        device.back_file == expected || device.back_file == format!("{expected} (deleted)")
    }))
}

fn verify_image_file(image: &Path) -> Result<(), &'static str> {
    let metadata = fs::symlink_metadata(image).map_err(|_| "tenant_image_missing")?;
    if !metadata.is_file() || metadata.uid() != 0 || metadata.mode() & 0o077 != 0 {
        return Err("tenant_image_untrusted");
    }
    let path = image.to_str().ok_or("invalid_image_path")?;
    let kind = command_output(
        "/usr/sbin/blkid",
        &["-p", "-s", "TYPE", "-o", "value", path],
    )?;
    if String::from_utf8_lossy(&kind).trim() != "ext4" {
        return Err("tenant_image_not_ext4");
    }
    Ok(())
}

pub async fn purge_tenant(tenant: &str, settings: &Settings) -> Result<(), &'static str> {
    if unsafe { libc::geteuid() } != 0 {
        return Err("purge_requires_root");
    }
    let (image, mount, unit, unit_path) = tenant_paths(tenant)?;
    if path_has_symlink(&image)? || path_has_symlink(&mount)? || path_has_symlink(&unit_path)? {
        return Err("storage_path_symlink");
    }

    let mut db = connect(settings)
        .await
        .map_err(|_| "database_unavailable")?;
    let tx = db.transaction().await.map_err(|_| "database_unavailable")?;
    tx.query_one(
        "SELECT pg_advisory_xact_lock(hashtextextended($1,0))",
        &[&tenant],
    )
    .await
    .map_err(|_| "database_unavailable")?;
    let references: i64 = tx.query_one(
        "SELECT count(*) FROM deployment_operations WHERE tenant_id=$1 AND destroyed_at IS NULL AND status IN ('preparing','deploying','verifying','available','failed')",
        &[&tenant],
    ).await.map_err(|_| "database_unavailable")?.get(0);
    if references != 0 {
        return Err("tenant_has_active_operation_references");
    }

    let purge_state: Option<bool> = tx
        .query_opt(
            "SELECT purged_at IS NOT NULL FROM tenant_storage_purges WHERE tenant_id=$1",
            &[&tenant],
        )
        .await
        .map_err(|_| "database_unavailable")?
        .map(|row| row.get(0));
    let pending = purge_state == Some(false);
    let completed = purge_state == Some(true);
    let image_exists = exists_lstat(&image)?;
    let mount_exists = exists_lstat(&mount)?;
    let unit_exists = exists_lstat(&unit_path)?;

    if completed {
        if image_exists || mount_exists || unit_exists {
            return Err("tenant_purge_record_conflicts_with_artifacts");
        }
        ensure_no_mount_at_or_below(&mount)?;
        if image_has_loop_reference(&image)? {
            return Err("tenant_loop_still_active");
        }
        check_no_docker_references(settings, &mount).await?;
        tx.commit().await.map_err(|_| "database_unavailable")?;
        return Ok(());
    }

    if !pending && !(image_exists && mount_exists && unit_exists) {
        return Err("tenant_storage_artifacts_incomplete");
    }
    if image_exists {
        verify_image_file(&image)?;
    }
    if mount_exists {
        let metadata = fs::symlink_metadata(&mount).map_err(|_| "tenant_mount_untrusted")?;
        if !metadata.is_dir() || metadata.uid() != 0 || metadata.mode() & 0o022 != 0 {
            return Err("tenant_mount_untrusted");
        }
    }
    if unit_exists {
        verify_generated_unit(tenant, &image, &mount, &unit_path)?;
    }

    let mounted = is_mount_at_or_below(&mount)?;
    if mounted {
        if !(image_exists && mount_exists && unit_exists) {
            return Err("tenant_mount_state_ambiguous");
        }
        mounts_for_tenant(&mount, &image)?;
    } else if image_exists && image_has_loop_reference(&image)? {
        return Err("tenant_loop_still_active");
    }
    if !pending && !mounted {
        return Err("tenant_mount_not_active");
    }
    check_no_docker_references(settings, &mount).await?;

    if purge_state.is_none() {
        tx.execute(
            "INSERT INTO tenant_storage_purges(tenant_id) VALUES($1)",
            &[&tenant],
        )
        .await
        .map_err(|_| "database_unavailable")?;
    }
    tx.commit().await.map_err(|_| "database_unavailable")?;

    if unit_exists {
        let stopped = Command::new("/usr/bin/systemctl")
            .env_clear()
            .env("PATH", "/usr/bin:/bin")
            .arg("stop")
            .arg(&unit)
            .output()
            .map_err(|_| "systemd_unavailable")?;
        if !stopped.status.success() {
            return Err("tenant_unit_stop_failed");
        }
    }
    ensure_no_mount_at_or_below(&mount)?;
    if image_has_loop_reference(&image)? {
        return Err("tenant_loop_still_active");
    }
    if mount_exists
        && fs::read_dir(&mount)
            .map_err(|_| "tenant_mountpoint_unreadable")?
            .next()
            .is_some()
    {
        return Err("tenant_mountpoint_not_empty");
    }

    if unit_exists {
        let disabled = Command::new("/usr/bin/systemctl")
            .env_clear()
            .env("PATH", "/usr/bin:/bin")
            .arg("disable")
            .arg(&unit)
            .output()
            .map_err(|_| "systemd_unavailable")?;
        if !disabled.status.success() {
            return Err("tenant_unit_disable_failed");
        }
        if path_has_symlink(&unit_path)? {
            return Err("tenant_unit_symlink");
        }
        fs::remove_file(&unit_path).map_err(|_| "tenant_unit_remove_failed")?;
    }
    if exists_lstat(&image)? {
        verify_image_file(&image)?;
        fs::remove_file(&image).map_err(|_| "tenant_image_remove_failed")?;
    }
    if exists_lstat(&mount)? {
        if path_has_symlink(&mount)?
            || fs::read_dir(&mount)
                .map_err(|_| "tenant_mountpoint_unreadable")?
                .next()
                .is_some()
        {
            return Err("tenant_mountpoint_not_empty");
        }
        fs::remove_dir(&mount).map_err(|_| "tenant_mountpoint_remove_failed")?;
    }
    let reload = Command::new("/usr/bin/systemctl")
        .env_clear()
        .env("PATH", "/usr/bin:/bin")
        .arg("daemon-reload")
        .output()
        .map_err(|_| "systemd_unavailable")?;
    if !reload.status.success() {
        return Err("systemd_reload_failed");
    }
    let updated = db.execute(
        "UPDATE tenant_storage_purges SET purged_at=now() WHERE tenant_id=$1 AND purged_at IS NULL",
        &[&tenant],
    ).await.map_err(|_| "database_unavailable")?;
    if updated != 1 {
        return Err("tenant_purge_record_update_failed");
    }
    Ok(())
}

#[cfg(test)]
mod tests {
    use super::*;
    #[test]
    fn purge_tenant_id_validation_is_deterministic() {
        assert!(!valid_storage_tenant_id("../tenant"));
        assert!(!valid_storage_tenant_id("tenant_with_underscore"));
        assert!(valid_storage_tenant_id("tenant-a"));
    }
}
