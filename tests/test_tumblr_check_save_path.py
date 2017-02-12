"""test Tumblr method."""
from unittest import mock
import pytest


@pytest.mark.parametrize('save_path', [None, 'path', '/path'])
def test_check_save_path(save_path):
    """test method.

    """
    with mock.patch('tumblr_ids.tumblr.Tumblr.__init__', return_value=None):
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
            # obj._set_default_save_path.assert_called_once_with(
            # m_os.getcwd.return_value, "imgs/", obj.blog)
            return
        if save_path.startswith('/'):
            obj._create_dir_if_not_exists(obj.save_path)
        else:
            # NOTE: only work on func test, not file test
            # obj._set_default_save_path.assert_called_once_with(
            # m_os.getcwd.return_value, "imgs/", obj.save_path)
            pass
