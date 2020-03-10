""" Tests for cli/metrics.py module """

from cli.metrics import node

from tests.constants import NODE_ID, BOUNTY_COUNT, SERVICE_ROW_COUNT

from core.metrics import get_metrics_from_events
from datetime import datetime


def yy_mm_dd_to_date(date_str):
    format_str = '%Y-%m-%d'
    return datetime.strptime(date_str, format_str)


def test_metrics(runner):
    result = runner.invoke(node, ['-id', str(NODE_ID)])
    row_count = BOUNTY_COUNT + SERVICE_ROW_COUNT
    metrics, total_bounty = get_metrics_from_events([NODE_ID])
    print(metrics)
    output_list = result.output.splitlines()[-row_count:]
    print(output_list)
    print(len(output_list))
    assert '       Date           Bounty   Downtime   Latency' == output_list[0]
    assert '-------------------------------------------------' == output_list[1]

    assert f'{metrics[0][0]}    {metrics[0][1]:.1f}          {metrics[0][2]}       {metrics[0][3]:.1f}' == output_list[2]  # noqa
    assert f'{metrics[1][0]}    {metrics[1][1]:.1f}          {metrics[1][2]}       {metrics[1][3]:.1f}' == output_list[3]  # noqa
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa


def test_metrics_limited(runner):
    metrics, total_bounty = get_metrics_from_events([NODE_ID], limit=1)
    result = runner.invoke(node, ['-id', str(NODE_ID), '-l', str(1)])
    row_count = len(metrics) + SERVICE_ROW_COUNT
    print(metrics)
    output_list = result.output.splitlines()[-row_count:]
    print(output_list)
    assert '       Date           Bounty   Downtime   Latency' == output_list[0]
    assert '-------------------------------------------------' == output_list[1]
    assert f'{metrics[0][0]}    {metrics[0][1]:.1f}          {metrics[0][2]}       {metrics[0][3]:.1f}' == output_list[2]  # noqa
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa


def test_metrics_since_limited_not_empty(runner):
    start_date = '2000-01-01'
    metrics, total_bounty = get_metrics_from_events([NODE_ID], limit=1,
                                                    start_date=yy_mm_dd_to_date(start_date))
    result = runner.invoke(node, ['-id', str(NODE_ID), '-l', str(1), '-s', start_date])
    row_count = len(metrics) + SERVICE_ROW_COUNT
    print(metrics)
    output_list = result.output.splitlines()[-row_count:]
    print(output_list)
    assert '       Date           Bounty   Downtime   Latency' == output_list[0]
    assert '-------------------------------------------------' == output_list[1]
    assert f'{metrics[0][0]}    {metrics[0][1]:.1f}          {metrics[0][2]}       {metrics[0][3]:.1f}' == output_list[2]  # noqa
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa


def test_metrics_since_limited_empty(runner):
    start_date = '2100-01-01'
    metrics, total_bounty = get_metrics_from_events([NODE_ID], limit=1,
                                                    start_date=yy_mm_dd_to_date(start_date))
    result = runner.invoke(node, ['-id', str(NODE_ID), '-l', str(1), '-s', start_date])
    row_count = len(metrics) + SERVICE_ROW_COUNT
    print(metrics, total_bounty)
    output_list = result.output.splitlines()[-row_count:]
    print(output_list)
    assert 'Date   Bounty   Downtime   Latency' == output_list[0]
    assert '----------------------------------' == output_list[1]
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa


def test_metrics_till_limited_not_empty(runner):
    end_date = '2100-01-01'
    metrics, total_bounty = get_metrics_from_events([NODE_ID], limit=1,
                                                    end_date=yy_mm_dd_to_date(end_date))
    result = runner.invoke(node, ['-id', str(NODE_ID), '-l', str(1), '-t', end_date])
    row_count = len(metrics) + SERVICE_ROW_COUNT
    print(metrics)
    output_list = result.output.splitlines()[-row_count:]
    print(output_list)
    assert '       Date           Bounty   Downtime   Latency' == output_list[0]
    assert '-------------------------------------------------' == output_list[1]
    assert f'{metrics[0][0]}    {metrics[0][1]:.1f}          {metrics[0][2]}       {metrics[0][3]:.1f}' == output_list[2]  # noqa
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa


def test_metrics_till_limited_empty(runner):
    end_date = '2000-01-01'
    metrics, total_bounty = get_metrics_from_events([NODE_ID], limit=1,
                                                    end_date=yy_mm_dd_to_date(end_date))
    result = runner.invoke(node, ['-id', str(NODE_ID), '-l', str(1), '-t', end_date])
    row_count = len(metrics) + SERVICE_ROW_COUNT
    print(metrics)
    output_list = result.output.splitlines()[-row_count:]
    print(output_list)
    assert 'Date   Bounty   Downtime   Latency' == output_list[0]
    assert '----------------------------------' == output_list[1]
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa


def test_metrics_since_till_limited_not_empty(runner):
    start_date = '2000-01-01'
    end_date = '2100-01-01'
    metrics, total_bounty = get_metrics_from_events([NODE_ID], limit=1,
                                                    start_date=yy_mm_dd_to_date(start_date),
                                                    end_date=yy_mm_dd_to_date(end_date))
    result = runner.invoke(node, ['-id', str(NODE_ID), '-l', str(1), '-t', end_date])
    row_count = len(metrics) + SERVICE_ROW_COUNT
    print(metrics)
    output_list = result.output.splitlines()[-row_count:]
    print(output_list)
    assert '       Date           Bounty   Downtime   Latency' == output_list[0]
    assert '-------------------------------------------------' == output_list[1]
    assert f'{metrics[0][0]}    {metrics[0][1]:.1f}          {metrics[0][2]}       {metrics[0][3]:.1f}' == output_list[2]  # noqa
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa


def test_metrics_since_till_limited_empty(runner):
    start_date = '2100-01-01'
    end_date = '2100-02-01'
    metrics, total_bounty = get_metrics_from_events([NODE_ID], limit=1,
                                                    start_date=yy_mm_dd_to_date(start_date),
                                                    end_date=yy_mm_dd_to_date(end_date))
    result = runner.invoke(node, ['-id', str(NODE_ID), '-l', str(1), '-t', end_date])
    row_count = len(metrics) + SERVICE_ROW_COUNT
    print(metrics)
    output_list = result.output.splitlines()[-row_count:]
    print(output_list)
    assert 'Date   Bounty   Downtime   Latency' == output_list[0]
    assert '----------------------------------' == output_list[1]
    assert '' == output_list[-2]
    assert f' Total bounty per the given period: {total_bounty:.3f} SKL' == output_list[-1]  # noqa
