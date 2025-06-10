from dataclasses import dataclass, field
from typing import List, Dict, Literal
import datetime

@dataclass
class Message:
    id: str
    type: Literal['user', 'bot']  # garante que só aceita 'user' ou 'bot'
    content: str
    timestamp: datetime.datetime
    subject: str = ""

@dataclass
class Question:
    id: str
    subject: str
    difficulty: str
    question: str
    options: List[str]
    correct_answer: int
    explanation: str
    tags: List[str]

@dataclass
class UserProgress:
    total_questions: int = 0
    correct_answers: int = 0
    streak: int = 0
    subjects: Dict[str, Dict[str, int]] = field(default_factory=dict)
