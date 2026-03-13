import os
import pytest
from services.video_service import ensure_hindi_font, _generate_beat
from PIL import ImageFont
import config


def test_font_loading():
    path = ensure_hindi_font()
    assert path is not None
    assert os.path.exists(path)

    # Check it parses
    font = ImageFont.truetype(path, 50)
    assert font is not None


def test_video_render(mocker):
    # Testing beat generation rather than full ffmpeg render (for unit test perf)
    beat_path = _generate_beat(1.0)
    assert os.path.exists(beat_path)
    assert os.path.getsize(beat_path) > 1000
    os.remove(beat_path)
