"""test module."""
import pytest


@pytest.mark.parametrize(
    'data, exp_res',
    [
        (
            '<source src=\\"http://user.tumblr.com/video_file/random/tumblr_random\\" >',
            ['http://user.tumblr.com/video_file/random/tumblr_random']
        ),
    ]
)
def test_get_video_url(data, exp_res):
    """test func."""
    from tumblr_ids.tumblr import get_video_url
    assert exp_res == get_video_url(data)


@pytest.mark.parametrize(
    'url, exp_res',
    [
        [
            'http://user.tumblr.com/video_file/random/tumblr_random',
            'tumblr_random.mp4',

        ],
        [
            'http://random.media.tumblr.com/random/tumblr_random_rrandom_random.png',
            'tumblr_random_rrandom_random.png'

        ]
    ],
)
def test_get_filename(url, exp_res):
    """test func."""
    from tumblr_ids.tumblr import get_filename
    assert exp_res == get_filename(url)
