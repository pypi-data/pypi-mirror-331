from __future__ import annotations
from typing import Optional
from edsl.questions.QuestionMultipleChoice import QuestionMultipleChoice

from edsl.questions.decorators import inject_exception


class QuestionLikertFive(QuestionMultipleChoice):
    """This question prompts the agent to respond to a statement on a 5-point Likert scale."""

    question_type = "likert_five"
    likert_options: list[str] = [
        "Strongly disagree",
        "Disagree",
        "Neutral",
        "Agree",
        "Strongly agree",
    ]

    def __init__(
        self,
        question_name: str,
        question_text: str,
        question_options: Optional[list[str]] = likert_options,
        answering_instructions: Optional[str] = None,
        question_presentation: Optional[str] = None,
        include_comment: bool = True,
    ):
        """Initialize the question.

        :param question_name: The name of the question.
        :param question_text: The text of the question.
        :param question_options: The options the respondent should select from (list of strings). If not provided, the default Likert options are used (['Strongly disagree', 'Disagree', 'Neutral', 'Agree', 'Strongly agree']). To view them, run `QuestionLikertFive.likert_options`.
        """
        super().__init__(
            question_name=question_name,
            question_text=question_text,
            question_options=question_options,
            use_code=False,
            include_comment=include_comment,
            answering_instructions=answering_instructions,
            question_presentation=question_presentation,
        )

    @classmethod
    @inject_exception
    def example(cls) -> QuestionLikertFive:
        """Return an example question."""
        return cls(
            question_name="happy_raining",
            question_text="I'm only happy when it rains.",
        )


def main():
    """Test QuestionLikertFive."""
    from edsl.questions.derived.QuestionLikertFive import QuestionLikertFive

    q = QuestionLikertFive.example()
    q.question_text
    q.question_options
    q.question_name
    # validate an answer
    q._validate_answer({"answer": 0, "comment": "I like custard"})
    # translate answer code
    q._translate_answer_code_to_answer(0, {})
    q._simulate_answer()
    q._simulate_answer(human_readable=False)
    q._validate_answer(q._simulate_answer(human_readable=False))
    # serialization (inherits from Question)
    q.to_dict()
    assert q.from_dict(q.to_dict()) == q

    import doctest

    doctest.testmod(optionflags=doctest.ELLIPSIS)
