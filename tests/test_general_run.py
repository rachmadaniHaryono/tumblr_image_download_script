"""test module."""
from itertools import product
from unittest import mock
from os import path
import time

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


@pytest.mark.parametrize('noinfo', [True, False])
def test_run_with_no_blog_given(noinfo):
    """test func."""
    with mock.patch('tumblr_ids.general_run.readblogs') as m_readblogs, \
            mock.patch('tumblr_ids.general_run.sys') as m_sys, \
            mock.patch('tumblr_ids.general_run.write_example') as m_write_example:
        m_readblogs.return_value = []
        from tumblr_ids.general_run import run
        # run
        run(
            noinfo=noinfo, stream=mock.Mock(), threading=mock.Mock(), timeout=mock.Mock(),
            filename='filename', proxy=mock.Mock(), tumblr_input=None
        )
        # test
        m_write_example.assert_called_once_with()
        if noinfo:
            m_sys.exit.assert_called_once_with(0)


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


@pytest.mark.parametrize(
    'argv, exp_res_dict',
    [
        (
            [],
            {
                'proxy': None, 'noinfo': False, 'limit': None, 'filename': 'blogs.txt',
                'timeout': None, 'threading': False, 'tumblr_input': None, 'stream': False
            }
        ),
        (['--limit', '-1'], None),
        (
            ['--limit', '1'],
            {
                'proxy': None, 'noinfo': False, 'limit': 1, 'filename': 'blogs.txt',
                'timeout': None, 'threading': False, 'tumblr_input': None, 'stream': False
            }
        ),
        (
            ['--proxy', 'protocol://host:port'],
            {
                'proxy': {'protocol': 'protocol://host:port'}, 'noinfo': False, 'limit': None,
                'filename': 'blogs.txt', 'timeout': None, 'threading': False,
                'tumblr_input': None, 'stream': False
            }
        ),
    ]
)
def test_get_args(argv, exp_res_dict):
    """test func."""
    from tumblr_ids.general_run import get_args
    # run
    if argv == ['--limit', '-1']:
        with pytest.raises(SystemExit):
            res = get_args(argv)
    else:
        res = get_args(argv)
    # test
    if exp_res_dict is not None:
        assert res.__dict__ == exp_res_dict


def test_print_elapsed_time():
    """test func."""
    from tumblr_ids.general_run import print_elapsed_time
    start_time = time.time()
    print_elapsed_time(start_time)


@pytest.mark.parametrize('input_retval, blogs', product(['y', 'n'], [[], [mock.Mock()]]))
def test_print_info(input_retval, blogs):
    """test func."""
    with mock.patch('tumblr_ids.general_run.sys') as m_sys, \
            mock.patch('tumblr_ids.general_run.input') as m_input:
        m_input.return_value = input_retval
        from tumblr_ids.general_run import print_info
        # run
        print_info(blogs=blogs, stream=mock.Mock(), threading=mock.Mock(), timeout=mock.Mock())
        # test
        if input_retval != 'y':
            m_sys.exit.assert_called_once_with(0)


def test_main():
    """test func."""
    argv = mock.Mock()
    args = mock.Mock()
    with mock.patch('tumblr_ids.general_run.get_args') as m_get_args, \
            mock.patch('tumblr_ids.general_run.run') as m_run:
        m_get_args.return_value = args
        from tumblr_ids.general_run import main
        main(argv)
        m_run.assert_called_once_with(
            args.noinfo, args.stream, args.threading, args.timeout, args.filename, args.proxies,
            image_limit=args.limit, tumblr_input=args.tumblr_input
        )


@pytest.mark.parametrize(
    'value, exp_res',
    [(None, None), ('protocol://host:port', {'protocol': 'protocol://host:port'})]
)
def test_check_proxy(value, exp_res):
    """test func"""
    from tumblr_ids.general_run import check_proxy
    assert exp_res == check_proxy(value)
