import os
import tempfile
import unittest
from unittest.mock import patch

from app.models.schema import VideoParams
from app.services import one_shot


def valid_params(**overrides):
    data = {
        "video_subject": "Cristiano Ronaldo returned after a personal tragedy",
        "video_script": (
            "Ronaldo faced a devastating family tragedy in 2022. Days later, "
            "he returned to the pitch while carrying grief nobody could see."
        ),
        "video_terms": "Cristiano Ronaldo emotional close up",
        "video_aspect": "9:16",
        "video_source": "image_search",
        "voice_name": "en-US-EricNeural-Male",
        "font_name": "MicrosoftYaHeiBold.ttc",
        "hook_text": "HE PLAYED THROUGH GRIEF",
        "hook_cover_term": "Cristiano Ronaldo emotional close up",
        "video_count": 1,
        "one_shot_mode": True,
    }
    data.update(overrides)
    return VideoParams(**data)


class TestOneShotPreflight(unittest.TestCase):
    def test_valid_request_passes_without_consuming_attempt(self):
        report = one_shot.preflight(valid_params())
        self.assertTrue(report["ok"])
        self.assertEqual(len(report["fingerprint"]), 64)

    def test_missing_script_is_blocked_before_generation(self):
        with self.assertRaisesRegex(one_shot.OneShotError, "video_script must be supplied"):
            one_shot.preflight(valid_params(video_script=""))

    def test_multiple_outputs_are_blocked(self):
        with self.assertRaisesRegex(one_shot.OneShotError, "video_count=1"):
            one_shot.preflight(valid_params(video_count=2))

    def test_parallel_generation_is_rejected_without_waiting(self):
        with one_shot.generation_slot():
            with self.assertRaisesRegex(one_shot.OneShotError, "another one-shot generation"):
                with one_shot.generation_slot():
                    pass

    def test_growth_profile_removes_early_tag_and_strengthens_cta(self):
        params = valid_params(loop_follow_tag=True, cta_text="FOLLOW FOR MORE ⚡")
        changes = one_shot.apply_growth_profile(params)
        self.assertFalse(params.loop_follow_tag)
        self.assertEqual(params.cta_text, "FOLLOW FOR UNTOLD FOOTBALL STORIES ⚡")
        self.assertEqual(len(changes), 2)

    def test_auto_footage_segments_share_original_source_identity(self):
        first = "/cache/clips/video123_c0.mp4.seg0.mp4"
        second = "/cache/clips/video123_c4.mp4.seg8.mp4"
        other = "/cache/clips/video999_c0.mp4.seg1.mp4"
        self.assertEqual(one_shot._media_source_key(first), one_shot._media_source_key(second))
        self.assertNotEqual(one_shot._media_source_key(first), one_shot._media_source_key(other))


class TestOneShotLedger(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.storage_patch = patch(
            "app.services.one_shot.utils.storage_dir",
            side_effect=lambda sub_dir="", create=False: self._storage(sub_dir, create),
        )
        self.storage_patch.start()

    def tearDown(self):
        self.storage_patch.stop()
        self.temp.cleanup()

    def _storage(self, sub_dir, create):
        path = os.path.join(self.temp.name, sub_dir)
        if create:
            os.makedirs(path, exist_ok=True)
        return path

    def test_same_topic_can_be_a_new_short_with_a_new_task_id(self):
        params = valid_params()
        report = one_shot.preflight(params)
        first = one_shot.OneShotGuard("first", params, report)
        second = one_shot.OneShotGuard("second", params, report)
        self.assertNotEqual(first.path, second.path)

    def test_same_task_id_cannot_enter_the_pipeline_twice(self):
        params = valid_params()
        report = one_shot.preflight(params)
        one_shot.OneShotGuard("same-task", params, report)
        with self.assertRaisesRegex(one_shot.OneShotError, "task already consumed"):
            one_shot.OneShotGuard("same-task", params, report)

    def test_same_stage_cannot_be_claimed_twice(self):
        params = valid_params()
        guard = one_shot.OneShotGuard("first", params, one_shot.preflight(params))
        guard.claim("voice_generation")
        with self.assertRaisesRegex(one_shot.OneShotError, "automatic retry blocked"):
            guard.claim("voice_generation")

    def test_duration_gate_can_resume_only_unclaimed_stages(self):
        params = valid_params()
        guard = one_shot.OneShotGuard("duration-task", params, one_shot.preflight(params))
        guard.claim("voice_generation")
        guard.finish(
            "failed",
            error="sole narration is 13.06s, above the 12.60s retention ceiling; acquisition/render blocked",
        )

        resumed = one_shot.OneShotGuard.resume_after_duration_gate("duration-task", params)
        with self.assertRaisesRegex(one_shot.OneShotError, "automatic retry blocked"):
            resumed.claim("voice_generation")
        resumed.claim("material_acquisition")
        resumed.claim("final_render")

    def test_duration_resume_rejects_other_failures(self):
        params = valid_params()
        guard = one_shot.OneShotGuard("other-failure", params, one_shot.preflight(params))
        guard.claim("voice_generation")
        guard.finish("failed", error="network unavailable")

        with self.assertRaisesRegex(one_shot.OneShotError, "did not fail"):
            one_shot.OneShotGuard.resume_after_duration_gate("other-failure", params)

if __name__ == "__main__":
    unittest.main()
