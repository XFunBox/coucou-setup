#!/usr/bin/env python3
"""Aplicar los ajustes y fusionar hooks sin copiar secretos ni confianza."""
import argparse
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
    value = json.loads(path.read_text())
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

def merge_hooks(root, relay):
    validate_hooks(root)
    result = json.loads(json.dumps(root))
    hooks = result.setdefault('hooks', {})
    for event, timeout in EVENTS.items():
        kept = []
        for group in hooks.get(event, []):
            handlers = [h for h in group['hooks'] if not (
                'coucou-hook' in h.get('command', '') and '--agent codex' in h.get('command', ''))]
            if handlers or not group['hooks']:
                kept.append({**group, 'hooks': handlers})
        handler = {'type': 'command', 'command': shlex.quote(str(relay)) + ' --agent codex', 'timeout': timeout}
        if event == 'PermissionRequest':
            handler['statusMessage'] = 'Waiting for your answer in the island (Coucou)'
        hooks[event] = kept + [{'hooks': [handler]}]
    return result

def atomic_write(path, content, mode=0o600):
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, name = tempfile.mkstemp(dir=path.parent, prefix='.coucou-setup-')
    try:
        with os.fdopen(fd, 'w') as stream:
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
        if existed and not (backup / path).is_file():
            raise ValueError(f'Falta la copia de {relative}')
    if dry_run:
        return list(manifest)
    for relative, existed in manifest.items():
        target, saved = home / relative, backup / relative
        if existed:
            atomic_copy(saved, target, saved.stat().st_mode & 0o777)
        elif target.is_file() or target.is_symlink():
            target.unlink()
    return list(manifest)

def apply(home, relay, profile, binary=None):
    home = Path(home).resolve()
    settings_path = home / '.config/coucou/settings.json'
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
    target_relay = home / '.local/share/coucou/bin/coucou-hook'
    hooks = merge_hooks(old_hooks, target_relay)
    if not Path(relay).is_file():
        raise ValueError(f'No se encuentra el relé: {relay}')
    local_bin = home / '.local/share/coucou-local/bin'
    binary = Path(binary) if binary else local_bin / 'coucou'
    if not binary.is_file():
        raise ValueError(f'No se encuentra el binario personalizado: {binary}')
    entry = desktop_entry(local_bin / 'coucou')
    backup = home / '.local/share/coucou-setup/backups' / datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup.mkdir(parents=True, mode=0o700)
    targets = [settings_path, hooks_path, home / '.config/autostart/Coucou.desktop',
               home / '.local/share/applications/Coucou.desktop', target_relay,
               local_bin / 'coucou', local_bin / 'coucou-hook']
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
            atomic_copy(staged_binary, local_bin/'coucou')
            atomic_copy(staged_relay, local_bin/'coucou-hook')
            atomic_copy(staged_relay, target_relay)
        atomic_write(settings_path, json.dumps(settings, indent=2) + '\n')
        atomic_write(hooks_path, json.dumps(hooks, indent=2) + '\n')
        atomic_write(home / '.config/autostart/Coucou.desktop', entry, 0o644)
        atomic_write(home / '.local/share/applications/Coucou.desktop', entry, 0o644)
    except Exception:
        restore(home, backup)
        raise
    print(f'Copias previas: {backup}')
    return backup

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', required=True, type=Path)
    parser.add_argument('--relay', type=Path)
    parser.add_argument('--binary', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    profile = Path(__file__).with_name('settings.json')
    read_object(profile)
    read_object(args.home / '.config/coucou/settings.json')
    validate_hooks(read_object(args.home / '.codex/hooks.json'))
    if args.check:
        print('Archivos JSON válidos; no se ha escrito nada.')
    elif not args.relay or not args.binary:
        parser.error('--relay y --binary son necesarios para aplicar')
    else:
        apply(args.home, args.relay, profile, args.binary)

if __name__ == '__main__':
    main()
