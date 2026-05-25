def needs_human_correction(task_score: float, threshold: float = 0.67) -> bool:
    return task_score < threshold
