# -*- coding: UTF-8 -*-
import datetime
import unittest

from mock import Mock, patch, call

from xivo_stat import queue


mock_add_full_call = Mock()
mock_fill_full_call = Mock()
mock_get_full_call = Mock()
mock_get_most_recent_time = Mock()
mock_get_periodic_stats = Mock()
mock_insert_periodic_stat = Mock()
mock_insert_stats = Mock()


mocks = [mock_add_full_call,
         mock_fill_full_call,
         mock_get_full_call,
         mock_get_most_recent_time,
         mock_get_periodic_stats,
         mock_insert_periodic_stat,
         mock_insert_stats]


class TestQueue(unittest.TestCase):

    def setUp(self):
        self._queue_name = 'my_queue'
        map(lambda mock: mock.reset_mock(), mocks)

    @patch('xivo_dao.queue_log_dao.get_queue_full_call',
           mock_get_full_call)
    @patch('xivo_dao.stat_call_on_queue_dao.add_full_call',
           mock_add_full_call)
    def test_fill_full(self):
        d1 = (datetime.datetime(2012, 01, 01)
              .strftime("%Y-%m-%d %H:%M:%S.%f"))
        d2 = (datetime.datetime(2012, 01, 01, 23, 59, 59, 999999)
              .strftime("%Y-%m-%d %H:%M:%S.%f"))
        callid = '1234567.890'
        mock_get_full_call.return_value = [{'queue_name': self._queue_name,
                                            'event': 'full',
                                            'time': d1,
                                            'callid': callid}]

        queue.fill_full_call(d1, d2)

        mock_add_full_call.assert_called_once_with(callid, d1, self._queue_name)

    @patch('xivo_stat.queue.fill_full_call', mock_fill_full_call)
    def test_fill_calls(self):
        start = datetime.datetime(2012, 1, 1)
        end = datetime.datetime(2012, 1, 1, 4, 59, 59, 999999)
        queue.fill_calls(start, end)

        mock_fill_full_call.assert_called_once_with(start, end)

    @patch('xivo_dao.stat_call_on_queue_dao.get_periodic_stats',
           mock_get_periodic_stats)
    @patch('xivo_dao.stat_queue_periodic_dao.insert_stats', mock_insert_stats)
    def test_insert_periodic_stat(self):
        s = datetime.datetime(2012, 01, 01)
        e = datetime.datetime(2012, 01, 01, 4, 59, 59, 999999)

        fake_stats = {'stats': 1234}

        expected_periods = [datetime.datetime(2012, 01, 01, 0),
                            datetime.datetime(2012, 01, 01, 1),
                            datetime.datetime(2012, 01, 01, 2),
                            datetime.datetime(2012, 01, 01, 3),
                            datetime.datetime(2012, 01, 01, 4)]
        expected_calls = [call(fake_stats, t) for t in expected_periods]

        mock_get_periodic_stats.return_value = fake_stats

        queue.insert_periodic_stat(s, e)

        self.assertEqual(mock_insert_stats.call_args_list, expected_calls)
