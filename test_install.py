import json
from pathlib import Path
import tempfile
import unittest
from configure import apply, merge_hooks, validate_hooks

class InstallerTests(unittest.TestCase):
    def test_preserves_other_hooks_and_metadata(self):
        root = {'description': 'keep', 'hooks': {'PreToolUse': [{'matcher': 'Bash', 'hooks': [{'type': 'command', 'command': 'my-check'}]}], 'CustomEvent': []}}
        out = merge_hooks(root, Path('/tmp/home with spaces/coucou-hook'))
        self.assertEqual(out['description'], 'keep')
        self.assertEqual(out['hooks']['PreToolUse'][0], root['hooks']['PreToolUse'][0])
        self.assertIn('CustomEvent', out['hooks'])
        self.assertTrue(out['hooks']['PreToolUse'][1]['hooks'][0]['command'].startswith("'/tmp/home with spaces/"))

    def test_idempotent_merge_and_old_path_replaced(self):
        a = merge_hooks({}, Path('/old/coucou-hook'))
        b = merge_hooks(a, Path('/new/coucou-hook'))
        self.assertEqual(b, merge_hooks(b, Path('/new/coucou-hook')))
        self.assertEqual(len(b['hooks']['SessionStart']), 1)
        self.assertIn('/new/', b['hooks']['SessionStart'][0]['hooks'][0]['command'])

    def test_rejects_malformed_groups(self):
        with self.assertRaises(ValueError):
            validate_hooks({'hooks': {'Stop': {'hooks': []}}})

    def test_install_backs_up_and_preserves_local_values(self):
        with tempfile.TemporaryDirectory(prefix='coucou test ') as temp:
            home = Path(temp) / 'home'
            settings = home / '.config/coucou/settings.json'
            settings.parent.mkdir(parents=True)
            settings.write_text('{"localSetting": 42, "hooksInstalled": true}')
            relay = Path(temp) / 'relay'
            relay.write_text('relay-fixture')
            profile = Path(temp) / 'profile.json'
            profile.write_text('{"mainPill":"agent_codex", "hooksInstalled":false}')
            backup = apply(home, relay, profile)
            result = json.loads(settings.read_text())
            self.assertEqual(result['localSetting'], 42)
            self.assertTrue(result['hooksInstalled'])
            self.assertIn('localSetting', (backup / '.config/coucou/settings.json').read_text())
            self.assertTrue((home / '.local/share/coucou/bin/coucou-hook').stat().st_mode & 0o111)
            self.assertEqual(len(json.loads((home / '.codex/hooks.json').read_text())['hooks']), 10)
            self.assertFalse((home / '.codex/config.toml').exists())

    def test_invalid_hooks_leave_existing_settings_untouched(self):
        with tempfile.TemporaryDirectory() as temp:
            home = Path(temp)
            hook = home / '.codex/hooks.json'
            hook.parent.mkdir()
            hook.write_text('{"hooks":[] }')
            profile = home / 'profile.json'
            profile.write_text('{}')
            with self.assertRaises(ValueError):
                apply(home, home / 'missing-relay', profile)
            self.assertFalse((home / '.config').exists())

if __name__ == '__main__':
    unittest.main()
