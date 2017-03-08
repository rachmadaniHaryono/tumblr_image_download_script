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
    with mock.patch('tumblr_ids.tumblr.get_logger') as m_get_logger, \
            mock.patch('tumblr_ids.tumblr.Tumblr._check_save_path'):
        from tumblr_ids.tumblr import Tumblr
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


@pytest.mark.parametrize(
    'total_posts_default, get_total_posts_retval, need_save',
    product([0, 1], [0, 1], [True, False])
)
def test_get_imgs_using_threading(total_posts_default, get_total_posts_retval, need_save):
    """test method."""
    with mock.patch('tumblr_ids.tumblr.Tumblr.__init__', return_value=None):
        from tumblr_ids.tumblr import Tumblr
        obj = Tumblr(blog=mock.Mock())
        obj.need_save = need_save
        obj.tags = [mock.Mock()]
        obj.total_posts = total_posts_default
        obj._get_total_posts = mock.Mock(return_value=get_total_posts_retval)
        obj._process_img_queue = mock.Mock()
        obj._run_threads = mock.Mock()
        # run
        obj.get_imgs_using_threading()
        # test
        assert obj.tag == obj.tags[0]
        assert obj.total_posts == 0
        if total_posts_default or get_total_posts_retval:
            obj._run_threads.assert_called_once_with()
        if get_total_posts_retval:
            obj._run_threads.assert_called_once_with()
        if need_save:
            obj._process_img_queue.assert_called_once_with([])


def test_run_threads():
    """test method."""
    with mock.patch('tumblr_ids.tumblr.Tumblr.__init__', return_value=None), \
            mock.patch('tumblr_ids.tumblr.threading') as m_threading:
        from tumblr_ids.tumblr import Tumblr
        obj = Tumblr(blog=mock.Mock())
        obj.threads_num = 1
        obj._get_img_urls = mock.Mock()
        # run
        obj._run_threads()
        # test
        m_threading.assert_has_calls([
            mock.call.Thread(target=obj._get_img_urls),
            mock.call.Thread().start(),
            mock.call.Thread().join()
        ])


@pytest.mark.parametrize('is_img_queue_empty', [True, False])
def test_process_img_queue(is_img_queue_empty):
    """test method."""
    with mock.patch('tumblr_ids.tumblr.Tumblr.__init__', return_value=None), \
            mock.patch('tumblr_ids.tumblr.threading') as m_threading:
        from tumblr_ids.tumblr import Tumblr
        obj = Tumblr(blog=mock.Mock())
        obj.threads_num = 1
        obj.img_queue = mock.Mock()
        obj.img_queue.empty.return_value = is_img_queue_empty
        obj._download_imgs = mock.Mock()
        # run
        obj._process_img_queue(consumer=[])
        # test
        if not is_img_queue_empty:
            m_threading.assert_has_calls([
                mock.call.Thread(target=obj._download_imgs),
                mock.call.Thread().start()
            ])


@pytest.mark.parametrize(
    'is_img_queue_empty, need_save, total_posts_default, get_total_posts_retval',
    product([True, False], [True, False], [0, 1], [0, 1])
)
def test_get_imgs(is_img_queue_empty, need_save, total_posts_default, get_total_posts_retval):
    """test method."""
    with mock.patch('tumblr_ids.tumblr.Tumblr.__init__', return_value=None):
        from tumblr_ids.tumblr import Tumblr
        obj = Tumblr(blog=mock.Mock())
        obj.threads_num = 1
        obj.tags = [mock.Mock()]
        obj.total_posts = total_posts_default
        obj.need_save = need_save
        obj.img_queue = mock.Mock()
        obj.img_queue.empty.return_value = is_img_queue_empty
        obj._download_imgs = mock.Mock()
        obj._get_img_urls = mock.Mock()
        obj._get_total_posts = mock.Mock(return_value=get_total_posts_retval)
        # run
        obj.get_imgs()
        # test
        assert obj.total_posts == 0
        if total_posts_default or get_total_posts_retval:
            obj._get_img_urls.assert_called_once_with()
        if need_save and not is_img_queue_empty:
            obj._download_imgs.assert_called_once_with()


@pytest.mark.parametrize('isfile_retval', [True, False])
def test_check_already_exists(isfile_retval):
    """test method."""
    name = mock.Mock()
    with mock.patch('tumblr_ids.tumblr.Tumblr.__init__', return_value=None), \
            mock.patch('tumblr_ids.tumblr.os') as m_os:
        from tumblr_ids.tumblr import Tumblr
        m_os.path.isfile.return_value = isfile_retval
        obj = Tumblr(blog=mock.Mock())
        obj.save_path = mock.Mock()
        res = obj._check_already_exists(name=name)
        assert isfile_retval == res


@pytest.mark.parametrize('data', [None, mock.Mock()])
def test_get_img_urls(data):
    """test method."""
    q_item = mock.Mock()
    item1 = mock.Mock()
    item2 = mock.Mock()
    with mock.patch('tumblr_ids.tumblr.Tumblr.__init__', return_value=None), \
            mock.patch('tumblr_ids.tumblr.utils') as m_utils, \
            mock.patch('tumblr_ids.tumblr.get_video_url') as m_get_vu:
        m_utils.download_page.return_value = data
        m_get_vu.return_value = [item2]
        from tumblr_ids.tumblr import Tumblr
        obj = Tumblr(blog=mock.Mock())
        obj.post_queue = queue.Queue()
        obj.post_queue.put(q_item)
        obj.base_url = mock.Mock()
        obj.num = mock.Mock()
        obj.tag = mock.Mock()
        obj.proxies = mock.Mock()
        obj.img_re = mock.Mock()
        obj.img_re.findall.return_value = [item1]
        obj._process_images = mock.Mock()
        obj._process_images.return_value = {'is_limit_reached': False, 'image_counter': 0}
        # run
        obj._get_img_urls()
        # test
        m_utils.download_page.assert_called_once_with(
            "{}{}&num={}&tagged={}".format(obj.base_url, q_item, obj.num, obj.tag),
            proxies=obj.proxies
        )
        if data:
            obj._process_images(
                image_counter=0,
                images=[item1, item2],
                is_limit_reached=False
            )


@pytest.mark.parametrize(
    'filename_exists, is_limit_reached, need_save, image_limit',
    product(
        [True, False],
        [True, False],
        [True, False],
        [None, 0],
    )
)
def test_process_images(filename_exists, is_limit_reached, need_save, image_limit):
    """test method."""
    img_item = mock.Mock()
    img_item.replace.return_value = img_item
    images = [img_item]
    image_counter = 0
    filename = mock.Mock()
    exp_res = {'is_limit_reached': is_limit_reached, 'image_counter': image_counter}
    if need_save:
        if image_limit is not None:
            if image_limit <= image_counter:
                exp_res['is_limit_reached'] = True
        else:
            exp_res['is_limit_reached'] = False
        if not(filename_exists or exp_res['is_limit_reached']):
            exp_res['image_counter'] += 1
    with mock.patch('tumblr_ids.tumblr.Tumblr.__init__', return_value=None), \
            mock.patch('tumblr_ids.tumblr.get_filename', return_value=filename):
        from tumblr_ids.tumblr import Tumblr
        obj = Tumblr(blog=mock.Mock())
        obj.need_save = need_save
        obj.image_limit = image_limit
        obj.img_queue = mock.Mock()
        obj.imglog = mock.Mock()
        obj._check_already_exists = mock.Mock(return_value=filename_exists)
        # run
        res = obj._process_images(
            images=images, image_counter=image_counter, is_limit_reached=is_limit_reached)
        assert res == exp_res
        # test
        if need_save and not(filename_exists or exp_res['is_limit_reached']):
            obj.img_queue.put.assert_called_once_with(images[0])


@pytest.mark.parametrize('image_limit, image_counter', product([None, 1], [0, 1]))
def test_check_limit(image_limit, image_counter):
    """test method."""
    from tumblr_ids.tumblr import Tumblr
    res = Tumblr._check_limit(image_limit, image_counter)
    if image_limit is not None:
        if image_limit <= image_counter:
            assert res
    else:
        assert not res


@pytest.mark.parametrize(
    'need_save, path_exists_retval, tags',
    product(
        [True, False],
        [True, False],
        [None, mock.Mock()]
    )
)
def test_download_imgs(need_save, path_exists_retval, tags):
    """test method."""
    img_url = mock.Mock()
    img_name = mock.Mock()
    with mock.patch('tumblr_ids.tumblr.Tumblr.__init__', return_value=None), \
            mock.patch('tumblr_ids.tumblr.utils') as m_utils, \
            mock.patch('tumblr_ids.tumblr.os') as m_os, \
            mock.patch('tumblr_ids.tumblr.get_filename', return_value=img_name):
        m_os.path.exists.return_value = path_exists_retval
        from tumblr_ids.tumblr import Tumblr
        obj = Tumblr(blogs=mock.Mock())
        obj.tags = tags
        obj.save_path = mock.Mock()
        obj.proxies = mock.Mock()
        obj.stream = mock.Mock()
        obj.timeout = mock.Mock()
        obj.img_queue = mock.Mock()
        obj.img_queue.empty.side_effect = [False, True]
        obj.img_queue.get.return_value = img_url
        obj.post_queue = mock.Mock()
        obj.post_queue.empty.side_effect = [False, True]
        obj.need_save = need_save
        # run
        obj._download_imgs()
        if not need_save:
            return
        if not (tags and path_exists_retval):
            m_utils.download_imgs.assert_called_once_with(
                img_url, obj.save_path, img_name, obj.proxies, stream=obj.stream,
                timeout=obj.timeout
            )
        else:
            m_utils.download_imgs.assert_not_called()


@pytest.mark.parametrize(
    'total_posts_from_data, max_posts, limit_start, data',
    product(
        [0, 1, '0', '1'],
        [None, 0, 1],
        [0, 1],
        [None, mock.Mock()]
    )
)
def test_get_total_posts(total_posts_from_data, max_posts, limit_start, data):
    """test method"""
    default_total_posts = 0
    with mock.patch('tumblr_ids.tumblr.Tumblr.__init__', return_value=None), \
            mock.patch('tumblr_ids.tumblr.utils') as m_utils:
        m_utils.download_page.return_value = data
        from tumblr_ids.tumblr import Tumblr
        obj = Tumblr(blogs=mock.Mock())
        obj.total_post_re = mock.Mock()
        obj.total_post_re.findall.return_value = [total_posts_from_data]
        obj.max_posts = max_posts
        obj.limit_start = limit_start
        obj.post_queue = mock.Mock()
        obj.base_url = mock.Mock()
        obj.tag = mock.Mock()
        obj.num = 1
        obj.total_posts = default_total_posts
        # run
        res = obj._get_total_posts()
        if not data:
            assert res == default_total_posts
        elif not max_posts:
            assert res == int(total_posts_from_data)
            if limit_start < res:
                obj.post_queue.put.called_once_with(obj.limit_start)
            else:
                obj.post_queue.put.assert_not_called()
        elif max_posts:
            assert res == min(int(total_posts_from_data), max_posts)
            if limit_start < res:
                obj.post_queue.put.called_once_with(obj.limit_start)
            else:
                obj.post_queue.put.assert_not_called()
        else:
            raise NotImplementedError


@pytest.mark.parametrize('isdir_retval', [True, False])
def test_create_dir_if_not_exists(isdir_retval):
    """test method."""
    path = mock.Mock()
    with mock.patch('tumblr_ids.tumblr.os') as m_os:
        m_os.path.isdir.return_value = isdir_retval
        from tumblr_ids.tumblr import Tumblr
        Tumblr._create_dir_if_not_exists(path)
        if not isdir_retval:
            m_os.makedirs.assert_called_once_with(path)


@pytest.mark.parametrize('total_posts', [None, mock.Mock()])
def test_str(total_posts):
    """test method."""
    txt_fmt = "{0} has {1} posts, left {2} json to parse, left {3} imgs to download"
    with mock.patch('tumblr_ids.tumblr.Tumblr.__init__', return_value=None):
        from tumblr_ids.tumblr import Tumblr
        obj = Tumblr(blogs=mock.Mock())
        obj.total_posts = total_posts
        obj._get_total_posts = mock.Mock()
        obj.blog = mock.Mock()
        obj.post_queue = mock.Mock()
        obj.img_queue = mock.Mock()
        assert str(obj) == txt_fmt.format(
            obj.blog, obj.total_posts, obj.post_queue.qsize.return_value,
            obj.img_queue.qsize.return_value
        )


@pytest.mark.parametrize('save_path', [None, 'path', '/path'])
def test_check_save_path(save_path):
    """test method.

    """
    with mock.patch('tumblr_ids.tumblr.Tumblr.__init__', return_value=None), \
            mock.patch('tumblr_ids.tumblr.os') as m_os:
        from tumblr_ids.tumblr import Tumblr
        obj = Tumblr(blogs=mock.Mock())
        obj._create_dir_if_not_exists = mock.Mock()
        obj._set_default_save_path = mock.Mock()
        obj.blog = mock.Mock()
        obj.save_path = save_path
        # run
        obj._check_save_path()
        if save_path is None:
            # NOTE: only work on func test, not file test
            obj._set_default_save_path.assert_called_once_with(
                m_os.getcwd.return_value, "imgs/", obj.blog)
            return
        if save_path.startswith('/'):
            obj._create_dir_if_not_exists(obj.save_path)
        else:
            # NOTE: only work on func test, not file test
            obj._set_default_save_path.assert_called_once_with(
                m_os.getcwd.return_value, "imgs/", obj.save_path)
            pass


def test_set_default_save_path():
    dirname = mock.Mock()
    basename = mock.Mock()
    with mock.patch('tumblr_ids.tumblr.Tumblr.__init__', return_value=None), \
            mock.patch('tumblr_ids.tumblr.os') as m_os:
        from tumblr_ids.tumblr import Tumblr
        obj = Tumblr(blogs=mock.Mock())
        obj._create_dir_if_not_exists
        obj._set_default_save_path(dirname, basename)
        assert obj.save_path == m_os.path.join.return_value
        m_os.path.join.assert_called_once_with(dirname, basename)
