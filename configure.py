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

def apply(home, relay, profile):
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
    backup = home / '.local/share/coucou-setup/backups' / datetime.datetime.now().strftime('%Y%m%d-%H%M%S-%f')
    backup.mkdir(parents=True, mode=0o700)
    targets = [settings_path, hooks_path, home / '.config/autostart/Coucou.desktop', target_relay]
    manifest = {}
    for target in targets:
        relative = target.relative_to(home)
        manifest[str(relative)] = target.exists()
        if target.exists():
            saved = backup / relative
            saved.parent.mkdir(parents=True, exist_ok=True)
            shutil.copy2(target, saved)
    atomic_write(backup / 'manifest.json', json.dumps(manifest, indent=2) + '\n')
    target_relay.parent.mkdir(parents=True, exist_ok=True)
    if Path(relay).resolve() != target_relay.resolve():
        shutil.copy2(relay, target_relay)
    target_relay.chmod(0o755)
    atomic_write(settings_path, json.dumps(settings, indent=2) + '\n')
    atomic_write(hooks_path, json.dumps(hooks, indent=2) + '\n')
    atomic_write(home / '.config/autostart/Coucou.desktop',
        '[Desktop Entry]\nType=Application\nVersion=1.0\nName=Coucou\n'
        'Comment=Coucou startup\nExec=/usr/bin/coucou\nStartupNotify=false\nTerminal=false\n', 0o644)
    print(f'Copias previas: {backup}')
    return backup

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--home', required=True, type=Path)
    parser.add_argument('--relay', type=Path)
    parser.add_argument('--check', action='store_true')
    args = parser.parse_args()
    profile = Path(__file__).with_name('settings.json')
    read_object(profile)
    read_object(args.home / '.config/coucou/settings.json')
    validate_hooks(read_object(args.home / '.codex/hooks.json'))
    if args.check:
        print('Archivos JSON válidos; no se ha escrito nada.')
    elif not args.relay:
        parser.error('--relay es necesario para aplicar')
    else:
        apply(args.home, args.relay, profile)

if __name__ == '__main__':
    main()
