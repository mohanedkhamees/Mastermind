# EvaluationResult.py
class EvaluationResult:
    def __init__(self, correct_position: int, correct_color: int):
        self.correct_position = correct_position
        self.correct_color = correct_color

    def is_correct(self, code_length: int) -> bool:
        return self.correct_position == code_length
