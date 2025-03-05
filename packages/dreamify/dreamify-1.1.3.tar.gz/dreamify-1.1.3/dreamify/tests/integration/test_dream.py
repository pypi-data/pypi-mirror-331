from pathlib import Path

import pytest

from dreamify.dream import Dream, dream


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_mock_dream_rgb():
    img_path = "examples/mock_rgb.jpg"

    dream(
        img_path,
        output_path="mock_dream.png",
        octaves=1,
        iterations=5,
        learning_rate=15.0,
        save_video=True,
        save_gif=True,
        mirror_video=True,
    )
    Path("mock_dream.png").unlink(missing_ok=True)
    Path("mock_dream.mp4").unlink(missing_ok=True)
    Path("mock_dream.gif").unlink(missing_ok=True)


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_mock_dream_grayscale():
    img_path = "examples/mock_grayscale.jpg"

    dream(
        img_path,
        output_path="mock_dream.png",
        octaves=1,
        iterations=5,
        learning_rate=15.0,
        save_video=True,
        save_gif=True,
        mirror_video=True,
    )
    Path("mock_dream.png").unlink(missing_ok=True)
    Path("mock_dream.mp4").unlink(missing_ok=True)
    Path("mock_dream.gif").unlink(missing_ok=True)


def test_dream_validator():
    img_path = "examples/mock_rgb.jpg"
    out_path = "examples/mock_dream.jpg"

    with pytest.raises(ValueError):
        dream(
            img_path,
            output_path=out_path,
            num_octave=-1,
            iterations=5,
            learning_rate=15.0,
        )
        print("Handled negative")


@pytest.mark.filterwarnings("ignore::UserWarning")
def test_classed_dream():
    img_path = "examples/mock_rgb.jpg"

    dream = Dream(iterations=1, octaves=1)

    dream(img_path)
    dream.save_video()
    dream.save_gif()
    Path("dream.png").unlink(missing_ok=True)
