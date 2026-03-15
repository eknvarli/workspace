from __future__ import annotations

from typing import Any

from .models import ActivityLog


def log_task_event(*, task, actor, verb: str, metadata: dict[str, Any] | None = None) -> ActivityLog:
    return ActivityLog.objects.create(
        organization=task.organization,
        actor=actor,
        project=task.project,
        task=task,
        verb=verb,
        metadata=metadata or {},
    )


def log_comment_event(*, comment, actor, verb: str, metadata: dict[str, Any] | None = None) -> ActivityLog:
    return ActivityLog.objects.create(
        organization=comment.task.organization,
        actor=actor,
        project=comment.task.project,
        task=comment.task,
        comment=comment,
        verb=verb,
        metadata=metadata or {},
    )
