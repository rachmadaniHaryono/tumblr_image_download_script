"""test module."""
from itertools import product
from unittest import mock

import pytest


@pytest.mark.parametrize(
    'url, ret_json, proxies, status_code',
    product(
        [None, mock.Mock()],
        [False, True],
        [None, mock.Mock()],
        [200, 404]
    )
)
def test_download_page(url, ret_json, proxies, status_code):
    """test func."""
    response = mock.Mock()
    response.status_code = status_code
    with mock.patch('tumblr_ids.utils.requests') as m_req:
        m_req.get.return_value = response
        from tumblr_ids.utils import download_page
        # run
        res = download_page(url, ret_json, proxies)
        # test
        if url is None or status_code != 200:
            assert not res
        elif url is not None and status_code == 200 and ret_json:
            assert res == response.json.return_value
        else:
            assert res == response.text


def test_download_imgs():
    """test func."""
    chunk = mock.Mock()
    response = mock.Mock()
    response.iter_content.return_value = [chunk]
    url = mock.Mock()
    path = mock.Mock()
    name = mock.Mock()
    m_open = mock.mock_open()
    with mock.patch('tumblr_ids.utils.requests') as m_req, \
            mock.patch('tumblr_ids.utils.open', m_open, create=True), \
            mock.patch('tumblr_ids.utils.os') as m_os:
        m_req.get.return_value = response
        from tumblr_ids.utils import download_imgs
        # run
        download_imgs(url, path, name, proxies=None, stream=True, timeout=10)
        # test
        m_open.assert_has_calls([
            mock.call(m_os.path.join.return_value, 'wb'),
            mock.call().__enter__(),
            mock.call().write(chunk),
            mock.call().__exit__(None, None, None)
        ])
