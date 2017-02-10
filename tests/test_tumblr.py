"""test module."""
from itertools import product
from unittest import mock
import queue
import re

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


@pytest.mark.parametrize(
    'total_post_re, img_re, save_path, need_save',
    product(
        [None, mock.Mock()],
        [None, mock.Mock()],
        [None, mock.Mock()],
        [True, False, None]
    )
)
def test_init(total_post_re, img_re, save_path, need_save):
    """test init.

    None as input value mean no input given, not `None` as value given.
    """
    blog = mock.Mock()
    default_attr = {
        'base_url': "http://{}.tumblr.com/api/read/json?start=".format(blog),
        'blog': blog,
        'image_limit': None,
        'img_re': re.compile('photo-url-1280":"(http.*?)",'),
        'imglog': None,
        'limit_start': 0,
        'max_posts': None,
        'need_save': True,
        'num': 30,
        'proxies': None,
        'save_path': None,
        'stream': True,
        'tag': '',
        'tags': [''],
        'threads_num': 10,
        'timeout': 10,
        'total_post_re': re.compile('"posts-total":"*(\\d+)"*,'),
        'total_posts': 0
    }
    default_attr['need_save'] = need_save is None or need_save
    default_attr['total_post_re'] = total_post_re if total_post_re is not None else \
        re.compile('"posts-total":"*(\\d+)"*,')
    default_attr['img_re'] = img_re if img_re is not None else \
        re.compile('photo-url-1280":"(http.*?)",')
    default_attr['save_path'] = save_path if need_save is None or need_save else None
    kwargs = {'blog': blog}
    if total_post_re is not None:
        kwargs['total_post_re'] = total_post_re
    if img_re is not None:
        kwargs['img_re'] = img_re
    if need_save is not None:
        kwargs['need_save'] = need_save
    if save_path is not None:
        kwargs['save_path'] = save_path
    with mock.patch('tumblr_ids.tumblr.get_logger') as m_get_logger:
        from tumblr_ids.tumblr import Tumblr
        Tumblr._check_save_path = mock.Mock()
        if not(need_save is None or need_save):
            default_attr['imglog'] = m_get_logger.return_value
        obj = Tumblr(**kwargs)
        obj_vars = vars(obj)
        assert isinstance(obj_vars.pop('img_queue'), queue.Queue)
        assert isinstance(obj_vars.pop('post_queue'), queue.Queue)
        assert obj_vars == default_attr
        if need_save or need_save is None:
            obj._check_save_path.assert_called_once_with()
        else:
            m_get_logger.assert_called_once_with('imgurl')


@pytest.mark.parametrize(
    'use_threading, image_limit',
    product([True, False, None], [None, mock.Mock()])
)
def test_run(use_threading, image_limit):
    """test run."""
    exp_obj_vars = {'proxies': None, 'stream': True, 'timeout': 10}
    kwargs = {}
    if use_threading is not None:
        kwargs['use_threading'] = use_threading
    if image_limit is not None:
        kwargs['image_limit'] = image_limit
        exp_obj_vars['image_limit'] = image_limit
    with mock.patch('tumblr_ids.tumblr.Tumblr.__init__', return_value=None):
        from tumblr_ids.tumblr import Tumblr
        obj = Tumblr(blog=mock.Mock())
        obj.get_imgs_using_threading = mock.Mock()
        obj.get_imgs = mock.Mock()
        # run
        obj.run(**kwargs)
        # test
        if use_threading is None or use_threading:
            obj.get_imgs_using_threading.assert_called_once_with()
        else:
            obj.get_imgs.assert_called_once_with()
        obj_vars = vars(obj)
        obj_vars.pop('get_imgs_using_threading')
        obj_vars.pop('get_imgs')
        assert obj_vars == exp_obj_vars
