from metrics.workflow_efficiency.task_completion import task_completion_score
from metrics.context_relevance.precision import context_precision


def test_task_completion_score():
    assert task_completion_score("settled is in the contract but test failed", "") == 1.0


def test_context_precision():
    assert context_precision("settled payment status contract", ["settled", "contract"]) == 1.0
