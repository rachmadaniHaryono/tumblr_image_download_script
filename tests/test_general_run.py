"""test module."""
from unittest import mock
from os import path

import pytest


@pytest.mark.parametrize(
    'blogs_file',
    [
        # example blogs file.
        path.join(path.dirname(path.dirname(__file__)), 'blogs.txt'),
        'random_path'
    ]
)
def test_readblogs(blogs_file):
    """test func."""
    user, tags = mock.Mock(), mock.Mock()
    with mock.patch('tumblr_ids.general_run.format_tumblr_input') as m_format_ti,\
            mock.patch('tumblr_ids.general_run.Tumblr') as m_tumblr:
        from tumblr_ids.general_run import readblogs
        m_format_ti.return_value = user, tags
        # run
        res = readblogs(blogs_file)
        # test
        assert isinstance(res, list)
        if path.isfile(blogs_file):
            m_tumblr.assert_has_calls([
                mock.call(user, tags=tags),
                mock.call(user, tags=tags),
                mock.call(user, tags=tags),
            ])
            m_format_ti.assert_has_calls([
                mock.call('lazy-artist\n'),
                mock.call('http://cool-artist.tumblr.com/\n'),
                mock.call('http://reblogging-artist.tumblr.com/;;original-post,cute\n')
            ])
            assert res == [m_tumblr.return_value, m_tumblr.return_value, m_tumblr.return_value]
        else:
            assert not res  # empty list
