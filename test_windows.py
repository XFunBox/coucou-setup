import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from configure import apply, merge_hooks, restore

class WindowsInstallerTests(unittest.TestCase):
    def test_windows_install_roundtrip_and_hooks(self):
        with tempfile.TemporaryDirectory(prefix="coucou O'Neil ") as temp:
            home = Path(temp)/'home'; source = Path(temp)/'source.exe'
            source.write_bytes(b'fixture')
            profile = Path(temp)/'profile.json'; profile.write_text('{"autostart":true}')
            settings = home/'AppData/Roaming/Coucou/settings.json'
            settings.parent.mkdir(parents=True)
            settings.write_text('{"keep":42}')
            backup = apply(home, source, profile, source, platform='windows')
            self.assertEqual(json.loads(settings.read_text())['keep'], 42)
            target = home/'AppData/Local/Coucou-local/bin/coucou.exe'
            self.assertEqual(target.read_bytes(), b'fixture')
            startup = home/'AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Startup/Coucou.vbs'
            self.assertFalse(startup.parent.exists(), 'the native app owns login startup')
            menu = home/'AppData/Roaming/Microsoft/Windows/Start Menu/Programs/Coucou Sendoa.vbs'
            self.assertIn('Run', menu.read_text())
            self.assertTrue(json.loads(settings.read_text())['autostart'])
            self.assertFalse((home/'.config').exists())
            hooks = json.loads((home/'.codex/hooks.json').read_text())
            command = hooks['hooks']['SessionStart'][0]['hooks'][0]['command']
            self.assertIn('-EncodedCommand', command)
            self.assertEqual(len(restore(home, backup, True)), 6)
            restore(home, backup)
            self.assertEqual(settings.read_text(), '{"keep":42}')
            self.assertFalse(target.exists())
            self.assertFalse(startup.exists())
            self.assertFalse(menu.exists())

    def test_optional_bridge_is_backed_up_and_restored(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)/'home'; source = Path(temp)/'source.exe'; source.write_bytes(b'fixture')
            bridge = Path(temp)/'bridge.mjs'; bridge.write_text('// bridge')
            profile = Path(temp)/'profile.json'; profile.write_text('{}')
            backup = apply(home, source, profile, source, platform='windows', bridge=bridge)
            local_bin = home/'AppData/Local/Coucou-local/bin'
            self.assertEqual((local_bin/'codex-bridge.mjs').read_text(), '// bridge')
            self.assertIn('node', (local_bin/'coucou-codex.cmd').read_text())
            self.assertEqual(len(restore(home, backup, True)), 8)
            restore(home, backup)
            self.assertFalse((local_bin/'coucou-codex.cmd').exists())

    def test_windows_merge_idempotent_and_safe_shell_encoding(self):
        import base64
        relay = Path("C:/Users/O'Neil %user% & name/coucou-hook.exe")
        merged = merge_hooks({}, relay, platform='windows')
        self.assertEqual(merged, merge_hooks(merged, relay, platform='windows'))
        command = merged['hooks']['Stop'][0]['hooks'][0]['command']
        script = base64.b64decode(command.split()[-1]).decode('utf-16-le')
        self.assertIn("O''Neil %user% & name", script)
        self.assertIn('--agent codex', script)

    def test_restore_continues_after_locked_relay(self):
        import configure
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)/'home'; source = Path(temp)/'source.exe'; source.write_bytes(b'new')
            binary = home/'AppData/Local/Coucou-local/bin/coucou.exe'
            relay = home/'AppData/Local/Coucou/bin/coucou-hook.exe'
            binary.parent.mkdir(parents=True); binary.write_bytes(b'old-app')
            relay.parent.mkdir(parents=True); relay.write_bytes(b'old-relay')
            profile = Path(temp)/'profile.json'; profile.write_text('{}')
            backup = apply(home, source, profile, source, platform='windows')
            real_copy = configure.atomic_copy
            def fail_relay(source_path, target, mode=0o755):
                if Path(target).resolve() == relay.resolve():
                    raise PermissionError('relay is running')
                return real_copy(source_path, target, mode)
            with patch('configure.atomic_copy', side_effect=fail_relay):
                with self.assertRaises(OSError):
                    restore(home, backup)
            self.assertEqual(binary.read_bytes(), b'old-app')
            self.assertFalse((home/'.codex/hooks.json').exists())
            self.assertEqual(relay.read_bytes(), b'new')

    def test_windows_failed_write_rolls_back(self):
        import configure
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)/'home'; source = Path(temp)/'source.exe'; source.write_bytes(b'new')
            target = home/'AppData/Local/Coucou-local/bin/coucou.exe'
            target.parent.mkdir(parents=True); target.write_bytes(b'old')
            profile = Path(temp)/'profile.json'; profile.write_text('{}')
            real_write = configure.atomic_write
            def fail_settings(path, content, mode=0o600):
                if path.name == 'settings.json':
                    raise OSError('disk failure')
                return real_write(path, content, mode)
            with patch('configure.atomic_write', side_effect=fail_settings):
                with self.assertRaises(OSError):
                    apply(home, source, profile, source, platform='windows')
            self.assertEqual(target.read_bytes(), b'old')
            self.assertFalse((home/'.codex/hooks.json').exists())

if __name__ == '__main__':
    unittest.main()
