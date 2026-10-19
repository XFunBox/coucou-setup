import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from configure import windows_hook_command

POWERSHELL = shutil.which('powershell.exe') or shutil.which('pwsh')
ROOT = Path(__file__).resolve().parent

@unittest.skipUnless(POWERSHELL, 'PowerShell is required for script runtime tests')
class WindowsScriptTests(unittest.TestCase):
    @unittest.skipUnless(os.name == 'nt', 'Uses the Windows .NET compiler')
    def test_encoded_hook_preserves_stdin_stdout_and_unicode(self):
        compiler = Path(os.environ['SystemRoot'])/'Microsoft.NET/Framework64/v4.0.30319/csc.exe'
        if not compiler.is_file():
            self.skipTest('Windows .NET Framework compiler is unavailable')
        with tempfile.TemporaryDirectory(prefix="coucou O'Neil % & ") as temp:
            source, executable = Path(temp)/'hook.cs', Path(temp)/'coucou-hook.exe'
            source.write_text('using System; class Hook { static void Main(string[] args) { '
                'if(args.Length != 2 || args[0] != "--agent" || args[1] != "codex") Environment.Exit(2); '
                'Console.OutputEncoding = new System.Text.UTF8Encoding(false); '
                'Console.Write(Console.In.ReadToEnd()); } }', encoding='utf-8')
            subprocess.run([str(compiler), '/nologo', '/out:'+str(executable), str(source)], capture_output=True, check=True)
            payload = '{"question":"\u00bfQu\u00e9 acci\u00f3n? PostgreSQL \u2713"}'
            result = subprocess.run(windows_hook_command(executable).split(), input=payload,
                capture_output=True, text=True, encoding='utf-8', timeout=20)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(result.stdout, payload)

    def invoke(self, home, *modes):
        return subprocess.run([POWERSHELL, '-NoProfile', '-ExecutionPolicy', 'Bypass',
                               '-File', str(ROOT/'install.ps1'), *modes,
                               '-TargetHome', str(home), '-Python', sys.executable],
                              cwd=ROOT, capture_output=True, text=True, errors='replace', timeout=30)

    def test_dry_run_executes_without_creating_profile(self):
        with tempfile.TemporaryDirectory(prefix='coucou script ') as temp:
            home = Path(temp)/'untouched profile'
            result = self.invoke(home, '-DryRun')
            self.assertEqual(result.returncode, 0, result.stdout+'\n'+result.stderr)
            self.assertIn('Would verify/download', result.stdout)
            self.assertIn('Would back up and install', result.stdout)
            self.assertFalse(home.exists())
            self.assertEqual(list(Path(temp).iterdir()), [])

    def test_incompatible_modes_fail_before_configuration(self):
        for modes in [('-DryRun','-ConfigureOnly'), ('-DryRun','-BuildOnly'), ('-ConfigureOnly','-BuildOnly')]:
            with self.subTest(modes=modes), tempfile.TemporaryDirectory(prefix='coucou script ') as temp:
                home = Path(temp)/'untouched profile'
                result = self.invoke(home, *modes)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn('Choose one mode', result.stderr)
                self.assertFalse(home.exists())
                self.assertEqual(list(Path(temp).iterdir()), [])

if __name__ == '__main__': unittest.main()
