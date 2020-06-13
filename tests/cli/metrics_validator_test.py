""" Tests for cli/metrics.py module """

from datetime import datetime

from cli.metrics import validator
from core.metrics import get_metrics_for_validator
from tests.constants import D_VALIDATOR_ID, SERVICE_ROW_COUNT
from tests.prepare_data import set_test_msr
from utils.texts import Texts

G_TEXTS = Texts()
NO_DATA_MSG = G_TEXTS['msg']['no_data']
NEG_ID_MSG = G_TEXTS['metrics']['validator']['index']['valid_id_msg']
NOT_EXIST_VAL_ID_MSG = G_TEXTS['metrics']['validator']['index']['id_error_msg']


def setup_module():
    set_test_msr(0)


def teardown_module():
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
    assert NOT_EXIST_VAL_ID_MSG == output_list[-1]


def test_metrics(skale, runner):
    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID)])
    metrics_all, total_bounty = get_metrics_for_validator(skale, D_VALIDATOR_ID)
    metrics = metrics_all['rows']
    row_count = len(metrics) + SERVICE_ROW_COUNT
    output_list = result.output.splitlines()[-row_count:]
    assert '       Date           Node ID   Bounty   Downtime   Latency' == output_list[0]
    assert '-----------------------------------------------------------' == output_list[1]
    assert f'{metrics[0][0]}         {metrics[0][1]}    {metrics[0][2]:.1f}          {metrics[0][3]}       {metrics[0][4]:.1f}' == output_list[2]  # noqa
    assert f'{metrics[1][0]}         {metrics[1][1]}    {metrics[1][2]:.1f}          {metrics[1][3]}       {metrics[1][4]:.1f}' == output_list[3]  # noqa
    assert f'{metrics[2][0]}         {metrics[2][1]}    {metrics[2][2]:.1f}          {metrics[2][3]}       {metrics[2][4]:.1f}' == output_list[4]  # noqa
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa


def test_metrics_since_not_empty(skale, runner):
    start_date = '2000-01-01'
    metrics_all, total_bounty = get_metrics_for_validator(skale, D_VALIDATOR_ID,
                                                          start_date=yy_mm_dd_to_date(start_date))
    metrics = metrics_all['rows']
    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID), '-s', start_date])
    row_count = len(metrics) + SERVICE_ROW_COUNT
    output_list = result.output.splitlines()[-row_count:]

    assert '       Date           Node ID   Bounty   Downtime   Latency' == output_list[0]
    assert '-----------------------------------------------------------' == output_list[1]
    assert f'{metrics[0][0]}         {metrics[0][1]}    {metrics[0][2]:.1f}          {metrics[0][3]}       {metrics[0][4]:.1f}' == output_list[2]  # noqa
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa


def test_metrics_since_empty(runner):
    start_date = '2100-01-01'
    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID), '-s', start_date])
    output_list = result.output.splitlines()

    assert NO_DATA_MSG == output_list[-1]


def test_metrics_till_not_empty(skale, runner):
    end_date = '2100-01-01'
    metrics_all, total_bounty = get_metrics_for_validator(skale, D_VALIDATOR_ID,
                                                          end_date=yy_mm_dd_to_date(end_date))
    metrics = metrics_all['rows']
    row_count = len(metrics) + SERVICE_ROW_COUNT
    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID), '-t', end_date])
    output_list = result.output.splitlines()[-row_count:]

    assert '       Date           Node ID   Bounty   Downtime   Latency' == output_list[0]
    assert '-----------------------------------------------------------' == output_list[1]
    assert f'{metrics[0][0]}         {metrics[0][1]}    {metrics[0][2]:.1f}          {metrics[0][3]}       {metrics[0][4]:.1f}' == output_list[2]  # noqa
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa


def test_metrics_till_empty(runner):
    end_date = '2000-01-01'
    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID), '-t', end_date])
    output_list = result.output.splitlines()

    assert NO_DATA_MSG == output_list[-1]


def test_metrics_since_till_not_empty(skale, runner):
    start_date = '2000-01-01'
    end_date = '2100-01-01'
    metrics_all, total_bounty = get_metrics_for_validator(skale, D_VALIDATOR_ID,
                                                          start_date=yy_mm_dd_to_date(start_date),
                                                          end_date=yy_mm_dd_to_date(end_date))
    metrics = metrics_all['rows']
    row_count = len(metrics) + SERVICE_ROW_COUNT
    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID),
                                       '-s', start_date, '-t', end_date])
    output_list = result.output.splitlines()[-row_count:]

    assert '       Date           Node ID   Bounty   Downtime   Latency' == output_list[0]
    assert '-----------------------------------------------------------' == output_list[1]
    assert f'{metrics[0][0]}         {metrics[0][1]}    {metrics[0][2]:.1f}          {metrics[0][3]}       {metrics[0][4]:.1f}' == output_list[2]  # noqa
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa


def test_metrics_since_till_empty(runner):
    start_date = '2100-01-01'
    end_date = '2100-02-01'
    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID),
                                       '-s', start_date, '-t', end_date])
    output_list = result.output.splitlines()

    assert NO_DATA_MSG == output_list[-1]
