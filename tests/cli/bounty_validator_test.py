""" Tests for cli/metrics.py module """

from datetime import datetime

from cli.bounty import validator
from core.metrics import get_bounty_from_events, get_nodes_for_validator
from tests.constants import D_VALIDATOR_ID, SERVICE_ROW_COUNT
from tests.prepare_data import set_test_msr
from utils.texts import Texts

G_TEXTS = Texts()
NO_DATA_MSG = G_TEXTS['msg']['no_data']
NEG_ID_MSG = G_TEXTS['bounty']['validator']['index']['valid_id_msg']
NOT_EXIST_ID_MSG = G_TEXTS['bounty']['validator']['index']['id_error_msg']


def setup_module(module):
    set_test_msr(0)


def teardown_module(module):
    set_test_msr()


def yy_mm_dd_to_date(date_str):
    format_str = '%Y-%m-%d'
    return datetime.strptime(date_str, format_str)


def test_neg_id(runner):
    result = runner.invoke(validator, ['-id', str(-1)])
    output_list = result.output.splitlines()
    assert NEG_ID_MSG == output_list[-1]


def test_not_existing_id(runner):
    result = runner.invoke(validator, ['-id', str(10)])
    output_list = result.output.splitlines()
    assert NOT_EXIST_ID_MSG == output_list[-1]


def test_bounty(skale, runner):
    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID)])
    node_ids = get_nodes_for_validator(skale, D_VALIDATOR_ID)
    metrics = get_bounty_from_events(skale, node_ids)
    row_count = len(metrics) + SERVICE_ROW_COUNT
    output_list = result.output.splitlines()[-row_count:]
    assert '      Date          All nodes   Node ID = 0   Node ID = 1' == output_list[0]
    assert '---------------------------------------------------------' == output_list[1]
    assert f'    {metrics[0][0]}     {metrics[0][1]:.3f}       {metrics[0][2]:.3f}       {metrics[0][3]:.3f}' == output_list[2]  # noqa


def test_metrics_since_till_limited_not_empty(skale, runner):
    start_date = '2000-01-01'
    end_date = '2100-01-01'
    node_ids = get_nodes_for_validator(skale, D_VALIDATOR_ID)
    metrics = get_bounty_from_events(skale, node_ids, limit=1,
                                     start_date=yy_mm_dd_to_date(start_date),
                                     end_date=yy_mm_dd_to_date(end_date))
    row_count = len(metrics) + SERVICE_ROW_COUNT
    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID), '-l', str(1),
                                       '-s', start_date, '-t', end_date])
    output_list = result.output.splitlines()[-row_count:]
    assert '      Date          All nodes   Node ID = 0   Node ID = 1' == output_list[0]
    assert '---------------------------------------------------------' == output_list[1]
    assert f'    {metrics[0][0]}     {metrics[0][1]:.3f}       {metrics[0][2]:.3f}       {metrics[0][3]:.3f}' == output_list[2]  # noqa


def test_metrics_since_till_limited_empty(runner):
    start_date = '2100-01-01'
    end_date = '2100-02-01'
    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID), '-l', str(1),
                                       '-s', start_date, '-t', end_date])
    output_list = result.output.splitlines()
    assert NO_DATA_MSG == output_list[-1]


def test_metrics_since_till_limited_in_wei_not_empty(skale, runner):
    start_date = '2000-01-01'
    end_date = '2100-01-01'
    node_ids = get_nodes_for_validator(skale, D_VALIDATOR_ID)
    metrics = get_bounty_from_events(skale, node_ids, limit=1, wei=True,
                                     start_date=yy_mm_dd_to_date(start_date),
                                     end_date=yy_mm_dd_to_date(end_date))
    row_count = len(metrics) + SERVICE_ROW_COUNT
    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID), '-l', str(1),
                                       '-s', start_date, '-t', end_date, '-w'])
    output_list = result.output.splitlines()[-row_count:]
    assert '      Date                All nodes              Node ID = 0             Node ID = 1     ' == output_list[0]  # noqa
    assert '-----------------------------------------------------------------------------------------' == output_list[1]  # noqa
    assert f'    {metrics[0][0]}   {metrics[0][1]}   {metrics[0][2]}   {metrics[0][3]}' == output_list[2]  # noqa
