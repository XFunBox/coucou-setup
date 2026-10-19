import hashlib
import io
import json
import os
from pathlib import Path
import shutil
import tarfile
import tempfile
import unittest
from unittest.mock import patch
import windows_build

class BuildValidationTests(unittest.TestCase):
    @unittest.skipUnless(shutil.which('git'), 'Git is required for source preparation')
    def test_preparation_preserves_bytes_with_global_autocrlf(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            (root/'patches').mkdir()
            archive = root/'source.tar.gz'
            with tarfile.open(archive, 'w:gz') as tar:
                member = tarfile.TarInfo('source/file.txt')
                member.size = len(b'original\n')
                tar.addfile(member, io.BytesIO(b'original\n'))
            for name, before, after in [('sendoa.patch', 'original', 'middle'), ('desktop.patch', 'middle', 'final')]:
                (root/'patches'/name).write_bytes(f'--- a/file.txt\n+++ b/file.txt\n@@ -1 +1 @@\n-{before}\n+{after}\n'.encode())
            git_config = root/'global.gitconfig'
            git_config.write_bytes(b'[core]\n\tautocrlf = true\n')
            lock = {'version': 'test', 'sourceSha256': windows_build.digest(archive)}
            with patch.dict(os.environ, {'GIT_CONFIG_GLOBAL': str(git_config)}):
                source = windows_build.prepare(root, lock, archive)
            self.assertEqual((source/'file.txt').read_bytes(), b'final\n')

    def test_rejects_archive_paths_and_links(self):
        for name, symlink in [('root/../../escape', False), ('root/link', True)]:
            with self.subTest(name=name), tempfile.TemporaryDirectory() as temp:
                archive = Path(temp)/'bad.tar.gz'
                with tarfile.open(archive, 'w:gz') as tar:
                    member = tarfile.TarInfo(name)
                    if symlink:
                        member.type = tarfile.SYMTYPE; member.linkname = '../../escape'
                        tar.addfile(member)
                    else:
                        member.size = 1; tar.addfile(member, io.BytesIO(b'x'))
                with self.assertRaises(ValueError):
                    windows_build.extract_source(archive, Path(temp)/'source')
                self.assertFalse((Path(temp)/'escape').exists())

    def test_release_verification_rejects_missing_and_duplicate_hashes(self):
        with tempfile.TemporaryDirectory() as temp:
            release = Path(temp); lock = {'version':'test'}
            (release/'VERSION').write_text('test')
            (release/'source-lock.json').write_text(json.dumps(lock))
            for name in ('coucou.exe', 'coucou-hook.exe'):
                (release/name).write_bytes(name.encode())
            lines = [hashlib.sha256((release/name).read_bytes()).hexdigest()+'  '+name for name in ('coucou.exe','coucou-hook.exe')]
            (release/'SHA256SUMS').write_text('\n'.join(lines))
            windows_build.verify_release(release, lock)
            (release/'SHA256SUMS').write_text('\n'.join([lines[0],lines[0],lines[1]]))
            with self.assertRaises(ValueError): windows_build.verify_release(release, lock)
            (release/'SHA256SUMS').write_text(lines[0])
            with self.assertRaises(ValueError): windows_build.verify_release(release, lock)

if __name__ == '__main__': unittest.main()
