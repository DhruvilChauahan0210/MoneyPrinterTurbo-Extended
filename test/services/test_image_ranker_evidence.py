import unittest
from collections import Counter
from unittest.mock import patch

from app.services import image_ranker
from app.services.one_shot import OneShotError


class TestEvidenceContext(unittest.TestCase):
    def test_hook_candidate_rejects_poster_that_beats_face_prompt(self):
        import numpy as np

        chosen = image_ranker._select_hook_candidate(
            pos_sims=np.array([0.34, 0.31]),
            sharpness=np.array([90.0, 70.0]),
            # Candidate zero is a sharp poster; candidate one is the real face.
            negative_sims=np.array([[0.39, 0.21], [0.20, 0.18]]),
            min_similarity=0.25,
            negative_margin=0.0,
        )

        self.assertEqual(chosen, 1)

    def test_hook_candidate_fails_when_every_frame_matches_negatives(self):
        import numpy as np

        chosen = image_ranker._select_hook_candidate(
            pos_sims=np.array([0.30, 0.29]),
            sharpness=np.array([80.0, 60.0]),
            negative_sims=np.array([[0.35], [0.31]]),
            min_similarity=0.25,
            negative_margin=0.0,
        )

        self.assertIsNone(chosen)

    def test_caption_fragments_receive_full_sentence_evidence(self):
        script = (
            "Roy Keane ended Haaland's dad's career? That's the myth. "
            "Alfie finished the match and played for Norway four days later."
        )
        fragments = [
            "Roy Keane ended", "Haaland's dad's career", "That's the myth",
            "Alfie finished", "the match", "and played for Norway",
            "four days later",
        ]
        evidence = ["the 2001 tackle", "the tackle replay", "Alfie playing after the tackle"]

        contexts = image_ranker.contextualize_segment_texts(fragments, script, evidence)

        self.assertEqual(contexts[:2], ["the 2001 tackle"] * 2)
        self.assertEqual(contexts[2], "the tackle replay")
        self.assertEqual(contexts[3:], ["Alfie playing after the tackle"] * 4)

    def test_strict_assignment_never_round_robins_without_clip(self):
        with patch.object(image_ranker, "_try_load_clip", return_value=False):
            with self.assertRaisesRegex(OneShotError, "evidence assignment is unavailable"):
                image_ranker.assign_images_to_segments(
                    ["a.mp4", "b.mp4"], ["the tackle"], strict=True
                )

    def test_assignment_caps_cut_reuse_and_alternates_source_uploads(self):
        import torch

        paths = [
            "/clips/source_a_c0.mp4", "/clips/source_a_c1.mp4",
            "/clips/source_b_c0.mp4", "/clips/source_b_c1.mp4",
            "/clips/source_c_c0.mp4", "/clips/source_c_c1.mp4",
        ]
        text_embeddings = torch.tensor([[1.0, 0.0]] * 6)
        media_embeddings = torch.tensor([[1.0, 0.0]] * 6)
        with (
            patch.object(image_ranker, "_try_load_clip", return_value=True),
            patch.object(image_ranker, "_embed_texts", return_value=text_embeddings),
            patch.object(image_ranker, "_embed_images", return_value=media_embeddings),
        ):
            chosen = image_ranker.assign_images_to_segments(
                paths,
                ["actual tackle footage"] * 6,
                reuse_penalty=0.1,
                source_reuse_penalty=0.2,
                max_media_reuse=1,
                max_source_reuse=2,
                strict=True,
            )

        self.assertEqual(max(Counter(chosen).values()), 1)
        sources = [paths[i].split("_c", 1)[0] for i in chosen]
        self.assertTrue(all(a != b for a, b in zip(sources, sources[1:])))


if __name__ == "__main__":
    unittest.main()
