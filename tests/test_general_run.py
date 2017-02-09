"""test module."""
from itertools import product
from unittest import mock
from os import path

import pytest


EXAMPLE_FILE = path.join(path.dirname(path.dirname(__file__)), 'example_file.txt')


@pytest.mark.parametrize(
    'blogs_file',
    [
        # example blogs file.
        EXAMPLE_FILE,
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


@pytest.mark.parametrize(
    'user, exp_res',
    [
        ('lazy-artist\n', ('lazy-artist', [''])),
        ('http://cool-artist.tumblr.com/\n', ('cool-artist', [''])),
        (
            'http://reblogging-artist.tumblr.com/;;original-post,cute\n',
            ('reblogging-artist', ['original-post', 'cute'])
        ),
    ]
)
def test_format_tumblr_input(user, exp_res):
    """test func."""
    from tumblr_ids.general_run import format_tumblr_input
    assert exp_res == format_tumblr_input(user)


@pytest.mark.parametrize(
    'seconds, exp_res',
    [
        (0, ''),
        (1, '1s'),
        (60, '1m'),
        (3600, '1h'),
        (3661, '1h1m1s'),

    ]
)
def test_get_readable_time(seconds, exp_res):
    """test func."""
    from tumblr_ids.general_run import get_readable_time
    assert exp_res == get_readable_time(seconds)


@pytest.mark.parametrize(
    'noinfo, stream, threading, tumblr_input, readblogs_retval',
    product(
        [True, False],
        [True, False],
        [True, False],
        [mock.Mock(), None],
        [[mock.Mock()], []],
    )
)
def test_run(noinfo, stream, threading, tumblr_input, readblogs_retval):
    """test func."""
    timeout = mock.Mock()
    filename = mock.Mock()
    proxy = mock.Mock()
    image_limit = mock.Mock()

    user = mock.Mock()
    tags = mock.Mock()

    blog = mock.Mock()
    with mock.patch('tumblr_ids.general_run.readblogs') as m_readblogs, \
            mock.patch('tumblr_ids.general_run.format_tumblr_input') as m_format_ti, \
            mock.patch('tumblr_ids.general_run.Tumblr') as m_tumblr, \
            mock.patch('tumblr_ids.general_run.sys') as m_sys, \
            mock.patch('tumblr_ids.general_run.write_example') as m_write_example, \
            mock.patch('tumblr_ids.general_run.print_info') as m_print_info, \
            mock.patch('tumblr_ids.general_run.time') as m_time, \
            mock.patch('tumblr_ids.general_run.print_elapsed_time') as m_print_et:
        m_format_ti.return_value = (user, tags)
        m_tumblr.return_value = blog
        m_readblogs.return_value = readblogs_retval
        from tumblr_ids.general_run import run
        # run
        run(noinfo, stream, threading, timeout, filename, proxy, image_limit, tumblr_input)
        # test
        m_readblogs.assert_called_once_with(filename)
        if tumblr_input is not None:
            m_format_ti.assert_called_once_with(tumblr_input)
        if not readblogs_retval and tumblr_input is None:
            if noinfo:
                m_sys.exit.assert_called_once_with(0)
            m_write_example.assert_called_once_with()
            return
        if not noinfo:
            m_print_info.assert_called_once_with()
        if tumblr_input is not None:
            blog.run.assert_called_once_with(
                image_limit=image_limit, proxies=proxy, stream=stream, timeout=timeout,
                use_threading=threading
            )
        if not threading:
            m_print_et.assert_called_once_with(start_time=m_time.time.return_value)


@pytest.mark.parametrize('input_retval', ['y', 'n'])
def test_write_example(input_retval):
    """test func."""
    with open(EXAMPLE_FILE) as f:
        example_file_text = f.read()
    file_obj = mock.Mock()
    with mock.patch('tumblr_ids.general_run.input') as m_input, \
            mock.patch('tumblr_ids.general_run.open') as m_open:
        m_input.return_value = input_retval
        m_open.return_value = file_obj
        from tumblr_ids.general_run import write_example
        write_example()
        if input_retval == 'y':
            # file_obj.write.assert_called_once_with(example_file_text)
            assert file_obj.write.call_args[0][0] == example_file_text
