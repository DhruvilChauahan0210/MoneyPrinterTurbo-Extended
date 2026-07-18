import json
import os
import tempfile
import unittest
from types import SimpleNamespace
from unittest.mock import patch

from app.models.schema import VideoParams
from app.services import task
from app.services import voice


class TestTaskOneShotPlumbing(unittest.TestCase):
    def test_script_manifest_excludes_runtime_guard(self):
        params = VideoParams(
            video_subject="test",
            video_script="This supplied script is long enough to represent a complete short story safely.",
            video_terms="test terms",
            voice_name="en-US-EricNeural-Male",
        )
        params._one_shot_guard = object()
        with tempfile.TemporaryDirectory() as directory, patch(
            "app.services.task.utils.task_dir", return_value=directory
        ):
            task.save_script_data("task", params.video_script, ["test terms"], params)
            manifest = os.path.join(directory, "script.json")
            with open(manifest, encoding="utf-8") as handle:
                saved = json.load(handle)
        self.assertEqual(saved["params"]["video_subject"], "test")
        self.assertNotIn("_one_shot_guard", saved["params"])

    def test_voice_volume_is_forwarded_to_tts(self):
        params = VideoParams(
            video_subject="test",
            video_script="A complete supplied script with enough words for this focused unit test.",
            video_terms="test",
            voice_name="en-US-EricNeural-Male",
            voice_volume=1.37,
            one_shot_mode=False,
        )
        fake_submaker = SimpleNamespace(_actual_audio_file=None)
        with tempfile.TemporaryDirectory() as directory, patch(
            "app.services.task.utils.task_dir", return_value=directory
        ), patch("app.services.task.voice.tts", return_value=fake_submaker) as tts, patch(
            "app.services.task.voice.get_audio_duration", return_value=12.0
        ), patch(
            "moviepy.AudioFileClip", side_effect=RuntimeError("no encoded file in unit test")
        ):
            audio_file, duration, _ = task.generate_audio("task", params, params.video_script)

        self.assertEqual(duration, 12)
        self.assertEqual(tts.call_args.kwargs["voice_volume"], 1.37)
        self.assertTrue(audio_file.endswith("audio.mp3"))

    def test_one_shot_planning_uses_precise_encoded_audio_duration(self):
        params = VideoParams(
            video_subject="test",
            video_script="A complete supplied script with enough words for this focused duration test.",
            video_terms="test",
            voice_name="en-US-EricNeural-Male",
            one_shot_mode=True,
        )
        fake_submaker = SimpleNamespace(_actual_audio_file=None)
        fake_audio = SimpleNamespace(duration=18.19, close=lambda: None)
        with tempfile.TemporaryDirectory() as directory, patch(
            "app.services.task.utils.task_dir", return_value=directory
        ), patch("app.services.task.voice.tts", return_value=fake_submaker), patch(
            "moviepy.AudioFileClip", return_value=fake_audio
        ):
            _, duration, _ = task.generate_audio("task", params, params.video_script)

        self.assertEqual(duration, 18.19)

    def test_voice_provider_attempt_limit_blocks_internal_retry(self):
        with patch("app.services.voice.edge_tts.Communicate", side_effect=RuntimeError("boom")) as provider:
            with voice.attempt_limit(1):
                result = voice.azure_tts_v1(
                    "hello world", "en-US-EricNeural-Male", 1.0, "/tmp/never-written.mp3"
                )
        self.assertIsNone(result)
        self.assertEqual(provider.call_count, 1)


if __name__ == "__main__":
    unittest.main()
