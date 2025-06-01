from typing import TypedDict, List


class QAItem(TypedDict):
    question: str
    answer: str


class ResumeQAOutput(TypedDict):
    qas: List[QAItem]
