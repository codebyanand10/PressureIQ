"""Tests for Submission Packager."""

from pathlib import Path
from src.final_audit.submission_packager import SubmissionPackager


def test_submission_packager_components():
    """Verify packager creates rankings, PDFs, scripts, and checklists."""
    root_dir = Path(__file__).resolve().parents[2]
    packager = SubmissionPackager(root_dir)

    # 1. Test ranking packaging
    rank_files = packager.package_rankings()
    assert len(rank_files) == 4
    for rf in rank_files:
        assert Path(rf).exists()

    # 2. Test video script packaging
    vid_files = packager.package_video_materials()
    assert len(vid_files) == 2
    for vf in vid_files:
        assert Path(vf).exists()

    # 3. Test checklist & readme
    chk = packager.create_submission_checklist()
    assert Path(chk).exists()
    rdm = packager.create_submission_readme()
    assert Path(rdm).exists()

    # 4. Test PDF summaries
    p1 = packager.generate_ranking_validation_summary_pdf()
    assert Path(p1).exists()
    p2 = packager.generate_statistical_robustness_summary_pdf()
    assert Path(p2).exists()

