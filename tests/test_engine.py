from __future__ import annotations

import json
import os
import tempfile
import time
import unittest
from pathlib import Path

from relaypilot.browser import BrowserProfile
from relaypilot.config import RelaySettings, default_settings_path
from relaypilot.engine import RelayEngine
from relaypilot.executor import LocalExecutor, StopRequested
from relaypilot.history import RunHistory
from relaypilot.models import Action, RunState
from relaypilot.policy import Policy, PolicyDenied
from relaypilot.planner import PlannerRouter
from relaypilot.reliability import retry_after_reconciliation
from relaypilot.webapp import RelayService, _ui_bytes


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

    def test_reads_allowed_browser_status_with_mocked_network(self) -> None:
        engine = RelayEngine(
            self.downloads,
            self.documents,
            page_fetcher=lambda _url: "<html><body><h1>Heat Signal</h1><p>Status: Data loaded</p></body></html>",
        )
        result = engine.run("Open Heat-Signal and report the visible status")
        self.assertEqual(result.state, RunState.COMPLETED)
        self.assertIn("Status: Data loaded", result.events[-1].evidence)

    def test_browser_connectivity_failure_is_clear_and_does_not_retry(self) -> None:
        attempts = 0

        def offline(_url: str) -> str:
            nonlocal attempts
            attempts += 1
            raise OSError("network disabled")

        engine = RelayEngine(self.downloads, self.documents, page_fetcher=offline)
        result = engine.run("Open Heat-Signal and report the visible status")
        self.assertEqual(result.state, RunState.BLOCKED)
        self.assertIn("Connectivity is required", result.reason or "")
        self.assertEqual(attempts, 1)

    def test_browser_read_rejects_ungranted_site(self) -> None:
        policy = Policy((self.downloads,), (self.documents,))
        with self.assertRaises(PolicyDenied):
            policy.authorize(Action("browser_read_status", {"url": "https://example.invalid/status"}))

    def test_counts_pdfs_in_downloads_from_natural_command(self) -> None:
        result = self.engine.run("I just want you to identify how many PDFs are saved in my downloads folder")
        self.assertEqual(result.state, RunState.COMPLETED)
        self.assertIn("Counted 2 PDFs", result.events[-1].message)

    def test_finds_and_opens_oldest_pdf_from_natural_command(self) -> None:
        result = self.engine.run("Open my oldest PDF on my PC")
        self.assertEqual(result.state, RunState.COMPLETED)
        self.assertEqual(self.opened, [(self.downloads / "old.pdf").resolve()])

    def test_opens_an_approved_folder_from_natural_command(self) -> None:
        result = self.engine.run("Open my Downloads folder")
        self.assertEqual(result.state, RunState.COMPLETED)
        self.assertEqual(len(self.opened), 1)
        self.assertTrue(self.opened[0].samefile(self.downloads))

    def test_open_path_never_escapes_an_explicit_file_scope(self) -> None:
        policy = Policy((self.downloads,), (self.documents,))
        with self.assertRaises(PolicyDenied):
            policy.authorize(Action("open_path", {"path": Path.cwd()}))

    def test_form_submission_remains_outside_a_standing_read_grant(self) -> None:
        policy = Policy((self.downloads,), (self.documents,))
        with self.assertRaises(PolicyDenied):
            policy.authorize(Action("browser_fill_form", {"url": "https://perumal100.github.io/test"}, external_effect=True))

    def test_settings_round_trip_and_scoped_policy(self) -> None:
        settings_file = Path(self.temp.name) / "settings.json"
        settings = RelaySettings.defaults(self.downloads, self.documents)
        settings.save(settings_file)
        restored = RelaySettings.load(settings_file, RelaySettings.defaults(Path("missing"), Path("missing")))
        self.assertEqual(restored.allowed_sites, ["perumal100.github.io"])
        self.assertEqual(restored.policy().writable_roots, (self.documents,))

    def test_engine_uses_the_configured_folder_scopes(self) -> None:
        alternate_downloads = Path(self.temp.name) / "ApprovedDownloads"
        alternate_documents = Path(self.temp.name) / "ApprovedDocuments"
        alternate_downloads.mkdir()
        alternate_documents.mkdir()
        (alternate_downloads / "daily.pdf").write_bytes(b"daily")
        settings = RelaySettings.defaults(alternate_downloads, alternate_documents)
        result = RelayEngine(self.downloads, self.documents, opener=self.opened.append, settings=settings).run(COMMAND)
        self.assertEqual(result.state, RunState.COMPLETED)
        self.assertTrue((alternate_documents / "daily.pdf").exists())

    def test_history_is_local_and_redacts_secrets(self) -> None:
        history = RunHistory(Path(self.temp.name) / "history.jsonl")
        engine = RelayEngine(self.downloads, self.documents, opener=self.opened.append, history=history)
        engine.run(COMMAND + " token=secret-value")
        record = history.recent()[0]
        self.assertIn("token=[redacted]", str(record["command"]))
        self.assertNotIn("secret-value", str(record))

    def test_timeout_is_reconciled_before_any_retry(self) -> None:
        attempts = 0

        def uncertain_action() -> str:
            nonlocal attempts
            attempts += 1
            raise TimeoutError("result unknown")

        result = retry_after_reconciliation(uncertain_action, lambda: "already completed")
        self.assertEqual(result.value, "already completed")
        self.assertTrue(result.recovered_after_timeout)
        self.assertEqual(attempts, 1)

    def test_timeout_retries_only_when_no_prior_completion_is_found(self) -> None:
        attempts = 0

        def eventually_works() -> str:
            nonlocal attempts
            attempts += 1
            if attempts == 1:
                raise TimeoutError("result unknown")
            return "completed now"

        result = retry_after_reconciliation(eventually_works, lambda: None)
        self.assertEqual(result.value, "completed now")
        self.assertEqual(result.attempts, 2)

    def test_browser_handoff_uses_a_separate_local_profile(self) -> None:
        profile = BrowserProfile(Path(self.temp.name) / "profile")
        handoff = profile.handoff_for_authentication("https://example.test/login", "sign in directly")
        self.assertTrue(handoff.profile_path.exists())
        self.assertEqual(handoff.reason, "sign in directly")

    def test_configured_local_model_extension_has_no_executor_access(self) -> None:
        class LocalProvider:
            def plan(self, _command: str) -> list[Action]:
                return [Action("browser_read_status", {"url": "https://perumal100.github.io/Heat-Signal/"})]

        plan = PlannerRouter(local_model=LocalProvider()).plan("use my local model", self.downloads, self.documents)
        self.assertEqual(plan[0].kind, "browser_read_status")

    def test_modern_local_ui_service_exposes_only_local_scopes(self) -> None:
        service = RelayService(Path(self.temp.name) / "settings.json")
        snapshot = service.snapshot()
        self.assertIn("downloads", snapshot["folders"])
        self.assertEqual(snapshot["sites"], ["perumal100.github.io"])
        self.assertIn(b"Speak naturally", _ui_bytes())

    def test_data_directory_override_is_explicit(self) -> None:
        original = os.environ.get("RELAYPILOT_DATA_DIR")
        os.environ["RELAYPILOT_DATA_DIR"] = self.temp.name
        try:
            self.assertEqual(default_settings_path(), Path(self.temp.name) / "settings.json")
        finally:
            if original is None:
                os.environ.pop("RELAYPILOT_DATA_DIR", None)
            else:
                os.environ["RELAYPILOT_DATA_DIR"] = original

    def test_legacy_settings_gain_new_routine_actions_once(self) -> None:
        settings_file = Path(self.temp.name) / "legacy-settings.json"
        settings_file.write_text(
            json.dumps({"downloads": str(self.downloads), "documents": str(self.documents), "allowed_actions": ["find_newest_pdf"]}),
            encoding="utf-8",
        )
        restored = RelaySettings.load(settings_file, RelaySettings.defaults(self.downloads, self.documents))
        self.assertEqual(restored.schema_version, 2)
        self.assertIn("count_pdfs", restored.allowed_actions)
        self.assertIn(str(self.documents), restored.readable_folders)

    def test_extension_has_active_tab_scope_not_unrestricted_site_access(self) -> None:
        manifest_path = Path(__file__).parents[1] / "extension" / "manifest.json"
        manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
        self.assertIn("activeTab", manifest["permissions"])
        self.assertNotIn("<all_urls>", manifest.get("host_permissions", []))
        self.assertIn("http://127.0.0.1:8721/*", manifest["host_permissions"])

