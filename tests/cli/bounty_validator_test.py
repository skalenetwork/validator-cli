""" Tests for cli/metrics.py module """

from datetime import datetime

from cli.bounty import validator
from core.metrics import get_bounty_from_events, get_nodes_for_validator
from tests.constants import D_VALIDATOR_ID, SERVICE_ROW_COUNT
from utils.texts import Texts

G_TEXTS = Texts()
NO_DATA_MSG = G_TEXTS['msg']['no_data']


def yy_mm_dd_to_date(date_str):
    format_str = '%Y-%m-%d'
    return datetime.strptime(date_str, format_str)


def test_bounty(runner):
    result = runner.invoke(validator, ['-id', str(D_VALIDATOR_ID)])
    node_ids = get_nodes_for_validator(D_VALIDATOR_ID)
    metrics, total_bounty = get_bounty_from_events(node_ids)
    row_count = len(metrics) + SERVICE_ROW_COUNT
    print(f'count = {row_count}')
    print(metrics)
    output_list = result.output.splitlines()[-row_count:]
    print(output_list)
    print(len(output_list))
    assert '      Date          All nodes   Node ID = 0   Node ID = 1' == output_list[0]
    assert '---------------------------------------------------------' == output_list[1]
    assert f'    {metrics[0][0]}     {metrics[0][1]:.3f}       {metrics[0][2]:.3f}       {metrics[0][3]:.3f}' == output_list[2]  # noqa
