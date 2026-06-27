from agent_harness.intake import TaskType, classify_task


def test_plain_conversation_does_not_default_to_technical_work() -> None:
    classification = classify_task("xin chao")

    assert classification.task_type is TaskType.CONVERSATION
    assert classification.route == "conversation"
    assert classification.requires_clarification is False
    assert classification.requires_plan_approval is False


def test_clear_repository_task_classifies_as_technical_work_without_planning() -> None:
    classification = classify_task("Fix the failing pytest test in src/agent.py")

    assert classification.task_type is TaskType.TECHNICAL_WORK
    assert classification.route == "technical_work"
    assert classification.requires_clarification is False
    assert classification.requires_plan_approval is False
    assert classification.requires_higher_autonomy is False
    assert "failing pytest test" in classification.explanation


def test_representative_tasks_classify_to_supported_task_types() -> None:
    examples = [
        ("Look up the current OpenAI API docs for structured outputs", TaskType.WEB_RESEARCH),
        ("Remember that I prefer concise completion reports", TaskType.MEMORY_WORK),
        ("Create a local issue for adding retry logging", TaskType.LOCAL_ISSUE_WORK),
        ("Set my search provider API key in .env.local", TaskType.SECRET_CONFIGURATION),
        ("Update the status page with the new backlog scope", TaskType.STATUS_PAGE_WORK),
    ]

    for task, expected_type in examples:
        classification = classify_task(task)

        assert classification.task_type is expected_type
        assert classification.route == expected_type.value
        assert classification.requires_clarification is False
        assert classification.requires_plan_approval is False
        assert classification.requires_higher_autonomy is False
        assert expected_type.value in classification.explanation


def test_ambiguous_task_requests_concise_clarification() -> None:
    classification = classify_task("Review the docs and remember what matters")

    assert classification.requires_clarification is True
    assert classification.clarification_question is not None
    assert "research" in classification.clarification_question.lower()
    assert "memory" in classification.clarification_question.lower()
    assert len(classification.clarification_question) < 140
    assert "ambiguous" in classification.explanation


def test_delivery_action_task_requires_plan_approval_and_higher_autonomy() -> None:
    classification = classify_task("Fix the test, commit the changes, and push the branch")

    assert classification.task_type is TaskType.TECHNICAL_WORK
    assert classification.requires_plan_approval is True
    assert classification.requires_higher_autonomy is True
    assert "delivery_action" in classification.explanation


def test_explicit_commands_bypass_task_classification() -> None:
    classification = classify_task("/autonomy deliver")

    assert classification.task_type is None
    assert classification.route == "explicit_command"
    assert classification.bypasses_classification is True
    assert classification.requires_clarification is False
    assert "autonomy" in classification.explanation
