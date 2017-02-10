"""test module."""
from itertools import product
from unittest import mock

import pytest


def test_get_logger_with_non_empty_handlers_on_root_logger():
    """test func."""
    root_logger = mock.Mock()
    root_logger.handlers = [mock.Mock()]
    logfile = 'logfile'
    with mock.patch('tumblr_ids.mylogger.logging') as m_logging:
        m_logging.getLogger.return_value = root_logger
        from tumblr_ids.mylogger import get_logger
        # run
        res = get_logger(logfile=logfile)
        # test
        m_logging.assert_has_calls([
            mock.call.getLogger(logfile),
        ])
        assert res == m_logging.getLogger.return_value


@pytest.mark.parametrize(
    'path',
    ['logs', 'logs/', '/logs', '/logs/'],
)
def test_get_logger(path):
    """test func."""
    path_startswith_slash = path.startswith('/')
    root_logger = mock.Mock()
    root_logger.handlers = []
    logfile = mock.Mock()
    # rotating file handler
    rfh_path = path if path.endswith('/') else '{}/'.format(path)
    with mock.patch('tumblr_ids.mylogger.logging') as m_logging, \
            mock.patch('tumblr_ids.mylogger.sys') as m_sys, \
            mock.patch('tumblr_ids.mylogger.create_new_logfile_path') as m_cnlp, \
            mock.patch('tumblr_ids.mylogger.process_path_as_folder') as m_ppaf:
        m_logging.getLogger.return_value = root_logger
        m_sys.path = [mock.Mock()]
        m_cnlp.return_value = path  # no change on path.
        from tumblr_ids import mylogger
        # run
        res = mylogger.get_logger(logfile=logfile, path=path)
        # test
        assert res == root_logger
        if path_startswith_slash:
            m_ppaf.assert_called_once_with(path)
        else:
            m_cnlp.assert_called_once_with(path=path)
        logging_calls = [
            mock.call.getLogger(logfile),
            mock.call.handlers.RotatingFileHandler(
                "{}{}.log".format(rfh_path, logfile),
                backupCount=10, encoding='utf-8', maxBytes=mylogger.MAX_BYTE, mode='a'
            ),
            mock.call.Formatter(mylogger.LOGGING_MSG_FORMAT, mylogger.LOGGING_DATE_FORMAT),
            mock.call.handlers.RotatingFileHandler().setFormatter(
                m_logging.Formatter.return_value),
            mock.call.getLogger().addHandler(
                m_logging.handlers.RotatingFileHandler.return_value),
            mock.call.getLogger().setLevel(10),
            mock.call.getLogger(logfile)
        ]
        m_logging.assert_has_calls(logging_calls)


@pytest.mark.parametrize('isdir_retval', [True, False])
def test_create_new_logfile_path(isdir_retval):
    """test func."""
    path = mock.Mock()
    new_path = mock.Mock()
    with mock.patch('tumblr_ids.mylogger.os') as m_os, \
            mock.patch('tumblr_ids.mylogger.sys') as m_sys:
        m_os.path.isdir.return_value = isdir_retval
        m_os.path.join.return_value = new_path
        m_sys.path = [mock.Mock()]
        from tumblr_ids import mylogger
        res = mylogger.create_new_logfile_path(path)
        assert res == m_os.path.join.return_value
        os_calls = [
            mock.call.path.join(m_sys.path[0], path),
            mock.call.path.isdir(new_path),
        ]
        if not isdir_retval:
            os_calls.append(mock.call.makedirs(new_path))
        m_os.assert_has_calls(os_calls)


@pytest.mark.parametrize(
    'isdir_retval, access_retval, makedirs_raise_error',
    product([True, False], repeat=3)
)
def test_process_path_as_folder(isdir_retval, access_retval, makedirs_raise_error):
    """test func."""
    path = mock.Mock()
    with mock.patch('tumblr_ids.mylogger.os') as m_os:
        m_os.isdir.return_value = isdir_retval
        m_os.access.return_value = access_retval
        if makedirs_raise_error:
            m_os.makedirs.side_effects = OSError
        from tumblr_ids import mylogger
        if not access_retval or makedirs_raise_error:
            with pytest.raises('SystemExit'):
                mylogger.process_path_as_folder(path)
            if not isdir_retval:
                m_os.assert_has_calls([
                    mock.call.path.isdir(path),
                    mock.call.makedirs(path),
                ])
            elif not access_retval:
                m_os.assert_has_calls([
                    mock.call.path.isdir(path),
                    mock.call.access_retval(path, m_os.R_OK | m_os.W_OK),
                ])
        else:
            mylogger.process_path_as_folder(path)
            m_os.assert_has_calls([
                mock.call.path.isdir(path),
                mock.call.makedirs(path),
            ])
