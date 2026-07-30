import subprocess

print("--- Deteniendo servicios dependientes y desvinculando programas eBPF antiguos ---")
subprocess.run(["ssh", "fan", "sudo systemctl stop sentinel-cortex sentinel-gamma-watchdog sentinel-pai-neural"], capture_output=True)

# Remove old pins in /sys/fs/bpf/
subprocess.run(["ssh", "fan", "sudo rm -rf /sys/fs/bpf/guardian_alpha /sys/fs/bpf/ai_guardian /sys/fs/bpf/sentinel/god_mode_uids"], capture_output=True)

print("--- Cargando nuevo objeto guardian_alpha_lsm.o con BPF_MAP_TYPE_ARRAY en Ring-0 ---")
res_load = subprocess.run(["ssh", "fan", "cd /home/jnovoas/Proyectos/sentinel/ebpf && sudo ./lsm_attach guardian_alpha_lsm.o guardian_execve /sys/fs/bpf/guardian_alpha"], capture_output=True, text=True)
print("Output lsm_attach:", res_load.stdout, res_load.stderr)

print("--- Verificando la estructura del nuevo mapa god_mode_uids en Kernel ---")
res_map = subprocess.run(["ssh", "fan", "sudo bpftool map show name god_mode_uids"], capture_output=True, text=True)
print("Map Show:\n", res_map.stdout)

