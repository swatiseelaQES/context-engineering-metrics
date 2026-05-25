from metrics.context_relevance.precision import context_precision


def context_relevance_score(context, required_context):
    """
    Aggregate relevance metric for retrieved context.
    """
    return context_precision(context, required_context)