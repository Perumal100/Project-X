from __future__ import annotations

import os
import tempfile
import time
import unittest
from pathlib import Path

from relaypilot.engine import RelayEngine
from relaypilot.executor import LocalExecutor, StopRequested
from relaypilot.models import Action, RunState
from relaypilot.policy import Policy, PolicyDenied


COMMAND = "Find the newest PDF in Downloads, copy it to Documents, open the copy, and tell me where you saved it."


class RelayEngineTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        root = Path(self.temp.name)
        self.downloads, self.documents = root / "Downloads", root / "Documents"
        self.downloads.mkdir()
        self.documents.mkdir()
        (self.downloads / "old.pdf").write_bytes(b"old")
        time.sleep(0.01)
        (self.downloads / "newest.pdf").write_bytes(b"newest content")
        self.opened: list[Path] = []
        self.engine = RelayEngine(self.downloads, self.documents, opener=self.opened.append)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_copies_verifies_and_reports_newest_pdf_offline(self) -> None:
        result = self.engine.run(COMMAND)
        copied = self.documents / "newest.pdf"
        self.assertEqual(result.state, RunState.COMPLETED)
        self.assertEqual(result.saved_path, copied.resolve())
        self.assertEqual(copied.read_bytes(), b"newest content")
        self.assertEqual((self.downloads / "newest.pdf").read_bytes(), b"newest content")
        self.assertEqual(self.opened, [copied.resolve()])
        self.assertIn(str(copied.resolve()), result.events[-1].evidence)

    def test_no_network_call_is_needed(self) -> None:
        original = os.environ.get("HTTP_PROXY")
        os.environ["HTTP_PROXY"] = "http://offline.invalid:9"
        try:
            self.assertEqual(self.engine.run(COMMAND).state, RunState.COMPLETED)
        finally:
            if original is None:
                os.environ.pop("HTTP_PROXY", None)
            else:
                os.environ["HTTP_PROXY"] = original

    def test_stop_prevents_actions(self) -> None:
        executor = LocalExecutor(self.engine.policy, stop_requested=lambda: True)
        with self.assertRaises(StopRequested):
            executor.execute(Action("find_newest_pdf", {"folder": self.downloads}), {})

    def test_untrusted_page_text_cannot_authorize_upload(self) -> None:
        policy = Policy((self.downloads,), (self.documents,))
        with self.assertRaises(PolicyDenied):
            policy.authorize(Action("upload_local_file", {"path": self.downloads / "newest.pdf"}, external_effect=True))

    def test_disallowed_path_is_blocked(self) -> None:
        policy = Policy((self.downloads,), (self.documents,))
        with self.assertRaises(PolicyDenied):
            policy.authorize(Action("copy_file", {"source": self.downloads / "newest.pdf", "destination": Path.cwd() / "nope.pdf"}))

