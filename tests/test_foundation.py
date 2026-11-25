import re
import subprocess
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class FoundationTests(unittest.TestCase):
    def git(self, *args):
        return subprocess.run(
            ["git", *args], cwd=ROOT, capture_output=True, text=True
        )

    def test_repository_is_independent(self):
        result = self.git("rev-parse", "--show-toplevel")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(Path(result.stdout.strip()).resolve(), ROOT)

    def test_local_markdown_links_resolve(self):
        for document in ROOT.rglob("*.md"):
            excluded = {".git", "node_modules", "dist", "__pycache__"}
            if excluded.intersection(document.relative_to(ROOT).parts):
                continue
            for target in re.findall(r"\]\(([^)]+)\)", document.read_text()):
                if "://" in target or target.startswith("#"):
                    continue
                with self.subTest(document=document.name, target=target):
                    self.assertTrue((document.parent / target.split("#")[0]).exists())

    def test_sensitive_paths_ignored_and_templates_available(self):
        for path in (".env", ".env.local", ".secrets/db", "terraform/prod.tfvars",
                     "terraform/default.tfstate", "kubernetes/kubeconfig-local"):
            with self.subTest(path=path):
                self.assertEqual(self.git("check-ignore", "-q", "--", path).returncode, 0)
        for path in (".env.example", "terraform/dev.example.tfvars", ".terraform.lock.hcl"):
            with self.subTest(path=path):
                self.assertEqual(self.git("check-ignore", "-q", "--", path).returncode, 1)
