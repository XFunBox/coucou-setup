#!/usr/bin/env python3
"""Aplicar los ajustes y fusionar hooks sin copiar secretos ni confianza."""
import argparse
import base64
import datetime
import json
import os
from pathlib import Path
import shlex
import shutil
import tempfile

EVENTS = {'SessionStart': 10, 'UserPromptSubmit': 10, 'PreToolUse': 10,
          'PermissionRequest': 120, 'PostToolUse': 10, 'Stop': 10,
          'SubagentStart': 10, 'SubagentStop': 10, 'Interrupt': 3, 'SessionEnd': 3}

def read_object(path):
    if not path.exists():
        return {}
    value = json.loads(path.read_text(encoding='utf-8-sig'))
    if not isinstance(value, dict):
        raise ValueError(f'{path}: debe contener un objeto JSON')
    return value

def validate_hooks(root):
    hooks = root.get('hooks', {})
    if not isinstance(hooks, dict):
        raise ValueError('hooks debe ser un objeto')
    for event, groups in hooks.items():
        if not isinstance(groups, list):
            raise ValueError(f'{event}: se esperaba una lista de grupos')
        for group in groups:
            if not isinstance(group, dict) or not isinstance(group.get('hooks'), list):
                raise ValueError(f'{event}: grupo inesperado; no se modificará')
            if any(not isinstance(handler, dict) for handler in group['hooks']):
                raise ValueError(f'{event}: handler inesperado')

def windows_hook_command(relay):
    # Codex uses cmd on Windows. Base64 keeps %, &, spaces and apostrophes out
    # of cmd's expansion rules; Windows PowerShell is part of Windows itself.
    script = "$OutputEncoding = [Console]::InputEncoding = [Console]::OutputEncoding = [System.Text.UTF8Encoding]::new(); & '" + str(relay).replace("'", "''") + "' --agent codex"
    encoded = base64.b64encode(script.encode('utf-16-le')).decode('ascii')
    return 'powershell.exe -NoLogo -NoProfile -NonInteractive -EncodedCommand ' + encoded


def is_codex_hook(command):
    if not isinstance(command, str):
        return False
    if command.startswith('powershell.exe -NoLogo -NoProfile -NonInteractive -EncodedCommand '):
        try:
            command = base64.b64decode(command.split()[-1], validate=True).decode('utf-16-le')
        except (ValueError, UnicodeError):
            return False
    return 'coucou-hook' in command and '--agent codex' in command


def merge_hooks(root, relay, platform='linux'):
    validate_hooks(root)
    result = json.loads(json.dumps(root))
    hooks = result.setdefault('hooks', {})
    for event, timeout in EVENTS.items():
        kept = []
        for group in hooks.get(event, []):
            handlers = [h for h in group['hooks'] if not (
                is_codex_hook(h.get('command', '')))]
            if handlers or not group['hooks']:
                kept.append({**group, 'hooks': handlers})
        command = windows_hook_command(relay) if platform == 'windows' else shlex.quote(str(relay)) + ' --agent codex'
        handler = {'type': 'command', 'command': command, 'timeout': timeout}
        if event == 'PermissionRequest':
            handler['statusMessage'] = 'Waiting for your answer in the island (Coucou)'
        hooks[event] = kept + [{'hooks': [handler]}]
    return result

def atomic_write(path, content, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.coucou-setup-')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8', newline='\n') as stream:
            stream.write(content)
        os.chmod(name, mode)
        os.replace(name, path)
    finally:
        if os.path.exists(name):
            os.unlink(name)

def atomic_copy(source, target, mode=0o755):
    target.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=target.parent, prefix='.coucou-setup-')
    os.close(fd)
    try:
        shutil.copyfile(source, name)
        os.chmod(name, mode)
        os.replace(name, target)
    finally:
        if os.path.exists(name):
            os.unlink(name)

def desktop_entry(binary):
    # Exec usa comillas dobles según Desktop Entry; no es Bash.
    escaped = str(binary).replace('\\', '\\\\').replace('"', '\\"')
    escaped = escaped.replace('`', '\\`').replace('$', '\\$').replace('%', '%%')
    return ('[Desktop Entry]\nType=Application\nVersion=1.0\nName=Coucou\n'
            'Comment=Coucou con Codex y GitHub\n'
            f'Exec="{escaped}"\nIcon=applications-other\n'
            'StartupNotify=false\nTerminal=false\nCategories=Utility;\n')

def restore(home, backup, dry_run=False):
    home, backup = Path(home).resolve(), Path(backup).resolve()
    manifest = read_object(backup / 'manifest.json')
    if not manifest:
        raise ValueError('No hay manifiesto de copias para restaurar')
    for relative, existed in manifest.items():
        path = Path(relative)
        if path.is_absolute() or '..' in path.parts or not isinstance(existed, bool):
            raise ValueError('Ruta o valor inesperado en manifest.json')
        target = home / path
        if not target.resolve().is_relative_to(home):
            raise ValueError('La ruta de restauración sale del directorio personal')
        if existed and not (backup/path).resolve().is_relative_to(backup):
            raise ValueError('La copia sale del directorio de respaldo')
        if existed and not (backup / path).is_file():
            raise ValueError(f'Falta la copia de {relative}')
    if dry_run:
        return list(manifest)
    failures = []
    for relative, existed in manifest.items():
        target, saved = home / relative, backup / relative
        try:
            if existed:
                atomic_copy(saved, target, saved.stat().st_mode & 0o777)
            elif target.is_file() or target.is_symlink():
                target.unlink()
        except OSError as error:
            # Windows may have one executable locked. Restore every other file
            # instead of leaving the main binary/config at the failed version.
            failures.append(f'{relative}: {error}')
    if failures:
        raise OSError('Restauración incompleta; conserva la copia ' + str(backup) + ': ' + '; '.join(failures))
    return list(manifest)

def windows_paths(home):
    # --home supports isolated test profiles. Use redirected environment paths
    # only for the actual current profile, never when configuring another home.
    current = home == Path.home().resolve()
    roaming = Path(os.environ.get('APPDATA', home/'AppData/Roaming')) if current else home/'AppData/Roaming'
    local = Path(os.environ.get('LOCALAPPDATA', home/'AppData/Local')) if current else home/'AppData/Local'
    for path in (roaming, local):
        if not path.resolve().is_relative_to(home):
            raise ValueError('AppData redirigido fuera de --home: no se puede respaldar de forma segura')
    return roaming, local


def settings_file(home, platform='linux'):
    home = Path(home).resolve()
    return windows_paths(home)[0]/'Coucou/settings.json' if platform == 'windows' else home/'.config/coucou/settings.json'


def windows_startup(binary):
    # VBScript Run accepts a quoted executable and starts without a console.
    command = '"' + str(binary) + '"'
    # WScript reads UTF-8 without BOM as ANSI. Keep the script ASCII and express
    # Unicode UTF-16 code units explicitly, including surrogate pairs.
    units = command.encode('utf-16-le')
    expression = '"'
    for offset in range(0, len(units), 2):
        unit = int.from_bytes(units[offset:offset+2], 'little')
        if unit >= 128:
            expression += '" & ChrW(' + str(unit if unit < 32768 else unit-65536) + ') & "'
        else:
            char = chr(unit)
            expression += '""' if char == '"' else char
    expression += '"'
    return 'CreateObject("WScript.Shell").Run ' + expression + ', 0, False\n'


def apply(home, relay, profile, binary=None, platform='linux', bridge=None):
    home = Path(home).resolve()
    settings_path = settings_file(home, platform)
    hooks_path = home / '.codex/hooks.json'
    current = read_object(settings_path)
    old_hooks = read_object(hooks_path)
    validate_hooks(old_hooks)
    profile = read_object(profile)
    # Estos indicadores se refieren a Claude Code, que no instalamos.
    profile.pop('hooksInstalled', None)
    profile.pop('planRelayInstalled', None)
    settings = {**current, **profile}
    settings.setdefault('hooksInstalled', False)
    settings.setdefault('planRelayInstalled', False)
    if platform == 'windows':
        roaming, local = windows_paths(home)
        local_bin = local/'Coucou-local/bin'
        exe, relay_exe = 'coucou.exe', 'coucou-hook.exe'
        target_relay = local/'Coucou/bin'/relay_exe
        entries = {roaming/'Microsoft/Windows/Start Menu/Programs/Startup/Coucou.vbs': windows_startup(local_bin/exe),
                   roaming/'Microsoft/Windows/Start Menu/Programs/Coucou.vbs': windows_startup(local_bin/exe)}
        backup_root = local/'Coucou-setup/backups'
    else:
        local_bin = home / '.local/share/coucou-local/bin'
        exe, relay_exe = 'coucou', 'coucou-hook'
        target_relay = home / '.local/share/coucou/bin/coucou-hook'
        entries = {home/'.config/autostart/Coucou.desktop': desktop_entry(local_bin/exe),
                   home/'.local/share/applications/Coucou.desktop': desktop_entry(local_bin/exe)}
        backup_root = home/'.local/share/coucou-setup/backups'
    if bridge is not None:
        bridge = Path(bridge)
        if not bridge.is_file():
            raise ValueError(f'No se encuentra el puente Codex: {bridge}')
        launcher = local_bin/('coucou-codex.cmd' if platform == 'windows' else 'coucou-codex')
        entries[launcher] = ('@echo off\nnode "%~dp0codex-bridge.mjs" --hook "%~dp0coucou-hook.exe" %*\n' if platform == 'windows'
                             else '#!/bin/sh\nexec node ' + shlex.quote(str(local_bin/'codex-bridge.mjs')) + ' --hook ' + shlex.quote(str(local_bin/relay_exe)) + ' "$@"\n')
    hooks = merge_hooks(old_hooks, target_relay, platform)
    if not Path(relay).is_file():
        raise ValueError(f'No se encuentra el relé: {relay}')
    binary = Path(binary) if binary else local_bin / exe
    if not binary.is_file():
        raise ValueError(f'No se encuentra el binario personalizado: {binary}')
    targets = [settings_path, hooks_path, *entries, target_relay, local_bin/exe, local_bin/relay_exe]
    if bridge is not None:
        targets.append(local_bin/'codex-bridge.mjs')
    for target in targets:
        if not target.resolve().is_relative_to(home):
            raise ValueError(f'La ruta sale del directorio personal: {target}')
        if target.is_symlink():
            raise ValueError(f'No se sobrescriben enlaces simbólicos: {target}')
        if target.exists() and not target.is_file():
            raise ValueError(f'No es un archivo: {target}')
    backup = backup_root / datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup.mkdir(parents=True, mode=0o700)
    manifest = {}
    for target in targets:
        relative = target.relative_to(home)
        manifest[str(relative)] = target.exists()
        if target.exists():
            saved = backup / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, saved)
    atomic_write(backup / 'manifest.json', json.dumps(manifest, indent=2) + '\n')
    try:
        with tempfile.TemporaryDirectory(prefix='coucou-setup-inputs-') as temp:
            staged_binary, staged_relay = Path(temp)/'coucou', Path(temp)/'coucou-hook'
            shutil.copy2(binary, staged_binary)
            shutil.copy2(relay, staged_relay)
            atomic_copy(staged_binary, local_bin/exe)
            atomic_copy(staged_relay, local_bin/relay_exe)
            atomic_copy(staged_relay, target_relay)
        if bridge is not None:
            atomic_copy(bridge, local_bin/'codex-bridge.mjs', 0o644)
        atomic_write(settings_path, json.dumps(settings, indent=2) + '\n')
        atomic_write(hooks_path, json.dumps(hooks, indent=2) + '\n')
        for path, content in entries.items():
            atomic_write(path, content, 0o755 if path.name == 'coucou-codex' else 0o644)
    except Exception as install_error:
        try:
            restore(home, backup)
        except Exception as restore_error:
            raise RuntimeError(f'Falló la instalación: {install_error}. {restore_error}') from install_error
        raise
    print(f'Copias previas: {backup}')
    return backup

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', required=True, type=Path)
    parser.add_argument('--relay', type=Path)
    parser.add_argument('--binary', type=Path)
    parser.add_argument('--bridge', type=Path)
    parser.add_argument('--check', '--dry-run', action='store_true')
    parser.add_argument('--platform', choices=['linux', 'windows'], default='windows' if os.name == 'nt' else 'linux')
    args = parser.parse_args()
    profile = Path(__file__).with_name('settings.json')
    read_object(profile)
    read_object(settings_file(args.home, args.platform))
    validate_hooks(read_object(args.home / '.codex/hooks.json'))
    if args.check:
        print('Archivos JSON válidos; no se ha escrito nada.')
    elif not args.relay or not args.binary:
        parser.error('--relay y --binary son necesarios para aplicar')
    else:
        apply(args.home, args.relay, profile, args.binary, args.platform, args.bridge)

if __name__ == '__main__':
    main()
