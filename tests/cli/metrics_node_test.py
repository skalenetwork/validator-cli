""" Tests for cli/metrics.py module """

import os.path
from datetime import datetime

import pandas

from cli.metrics import node
from core.metrics import get_metrics_for_node
from tests.constants import NODE_ID, SERVICE_ROW_COUNT
from tests.prepare_data import set_test_msr
from utils.texts import Texts

G_TEXTS = Texts()
NO_DATA_MSG = G_TEXTS['msg']['no_data']
NEG_ID_MSG = G_TEXTS['metrics']['node']['index']['valid_id_msg']
NOT_EXIST_NODE_ID_MSG = G_TEXTS['metrics']['node']['index']['id_error_msg']


def setup_module(module):
    set_test_msr(0)


def teardown_module(module):
    set_test_msr()


def yy_mm_dd_to_date(date_str):
    format_str = '%Y-%m-%d'
    return datetime.strptime(date_str, format_str)


def test_neg_id(runner):
    result = runner.invoke(node, ['-id', str(-1)])
    output_list = result.output.splitlines()
    assert NEG_ID_MSG == output_list[-1]


def test_not_existing_id(runner):
    result = runner.invoke(node, ['-id', str(10)])
    output_list = result.output.splitlines()
    assert NOT_EXIST_NODE_ID_MSG == output_list[-1]


def test_metrics(skale, runner):
    metrics, total_bounty = get_metrics_for_node(skale, NODE_ID)
    row_count = len(metrics) + SERVICE_ROW_COUNT
    result = runner.invoke(node, ['-id', str(NODE_ID)])
    output_list = result.output.splitlines()[-row_count:]

    assert '       Date            Bounty     Downtime   Latency' == output_list[0]
    assert '----------------------------------------------------' == output_list[1]
    assert f'{metrics[0][0]}   {metrics[0][1]:.1f}          {metrics[0][2]}       {metrics[0][3]:.1f}' == output_list[2]  # noqa
    assert f'{metrics[1][0]}   {metrics[1][1]:.1f}          {metrics[1][2]}       {metrics[1][3]:.1f}' == output_list[3]  # noqa
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa


def test_metrics_since_empty(runner):
    start_date = '2100-01-01'
    result = runner.invoke(node, ['-id', str(NODE_ID), '-s', start_date])
    output_list = result.output.splitlines()

    assert NO_DATA_MSG in output_list[-1]


def test_metrics_till_not_empty(skale, runner):
    end_date = '2100-01-01'
    metrics, total_bounty = get_metrics_for_node(skale, NODE_ID,
                                                 end_date=yy_mm_dd_to_date(end_date))
    row_count = len(metrics) + SERVICE_ROW_COUNT
    result = runner.invoke(node, ['-id', str(NODE_ID), '-t', end_date])
    output_list = result.output.splitlines()[-row_count:]

    assert '       Date            Bounty     Downtime   Latency' == output_list[0]
    assert '----------------------------------------------------' == output_list[1]
    assert f'{metrics[0][0]}   {metrics[0][1]:.1f}          {metrics[0][2]}       {metrics[0][3]:.1f}' == output_list[2]  # noqa
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa


def test_metrics_till_empty(runner):
    end_date = '2000-01-01'
    result = runner.invoke(node, ['-id', str(NODE_ID), '-t', end_date])
    output_list = result.output.splitlines()
    assert NO_DATA_MSG in output_list[-1]


def test_metrics_since_till_not_empty(skale, runner):
    start_date = '2000-01-01'
    end_date = '2100-01-01'
    metrics, total_bounty = get_metrics_for_node(skale, NODE_ID,
                                                 start_date=yy_mm_dd_to_date(start_date),
                                                 end_date=yy_mm_dd_to_date(end_date))
    row_count = len(metrics) + SERVICE_ROW_COUNT
    result = runner.invoke(node, ['-id', str(NODE_ID),
                                  '-s', start_date, '-t', end_date])
    output_list = result.output.splitlines()[-row_count:]

    assert '       Date            Bounty     Downtime   Latency' == output_list[0]
    assert '----------------------------------------------------' == output_list[1]
    assert f'{metrics[0][0]}   {metrics[0][1]:.1f}          {metrics[0][2]}       {metrics[0][3]:.1f}' == output_list[2]  # noqa
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa


def test_metrics_since_till_empty(runner):
    start_date = '2100-01-01'
    end_date = '2100-02-01'
    result = runner.invoke(node, ['-id', str(NODE_ID),
                                  '-s', start_date, '-t', end_date])
    output_list = result.output.splitlines()
    assert NO_DATA_MSG in output_list[-1]


def test_metrics_with_csv_export(skale, runner):
    filname = 'node_metrics.csv'
    metrics, total_bounty = get_metrics_for_node(skale, NODE_ID)
    row_count = len(metrics) + SERVICE_ROW_COUNT
    result = runner.invoke(node, ['-id', str(NODE_ID), '-f', filname])
    output_list = result.output.splitlines()[-row_count:]

    assert '       Date            Bounty     Downtime   Latency' == output_list[0]
    assert '----------------------------------------------------' == output_list[1]
    assert f'{metrics[0][0]}   {metrics[0][1]:.1f}          {metrics[0][2]}       {metrics[0][3]:.1f}' == output_list[2]  # noqa
    assert f'{metrics[1][0]}   {metrics[1][1]:.1f}          {metrics[1][2]}       {metrics[1][3]:.1f}' == output_list[3]  # noqa
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa

    assert os.path.isfile(filname)
    df = pandas.read_csv(filname)
    assert len(df.axes[0]) == 2
    assert len(df.axes[1]) == 4


def test_metrics_with_csv_export_in_wei(skale, runner):
    filname = 'node_metrics.csv'
    metrics, total_bounty = get_metrics_for_node(skale, NODE_ID, wei=True)
    row_count = len(metrics) + SERVICE_ROW_COUNT
    result = runner.invoke(node, ['-id', str(NODE_ID), '-w', '-f', filname])
    output_list = result.output.splitlines()[-row_count:]

    assert '       Date                    Bounty             Downtime   Latency' == output_list[0]
    assert '--------------------------------------------------------------------' == output_list[1]
    assert f'{metrics[0][0]}   {metrics[0][1]}          {metrics[0][2]}       {metrics[0][3]}' == output_list[2]  # noqa
    assert f'{metrics[1][0]}   {metrics[1][1]}          {metrics[1][2]}       {metrics[1][3]}' == output_list[3]  # noqa
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty} wei' == output_list[-1]  # noqa

    assert os.path.isfile(filname)
    df = pandas.read_csv(filname)
    assert len(df.axes[0]) == 2
    assert len(df.axes[1]) == 4
    metrics_list = df.values.tolist()
    metrics_list[0][1] = int(metrics_list[0][1])
    assert metrics[0] == metrics_list[0]
