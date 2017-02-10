"""test module."""
from unittest import mock


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
            mock.call.getLogger(logfile),
        ])
        assert res == m_logging.getLogger.return_value
