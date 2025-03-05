from dataclasses import dataclass, field
from typing import List, Set, Dict
import datetime
import dateutil.parser
import re


def getParsonsSolutionFromSource(source):
    solution = ""
    for line in re.split("-----\\s*\n", source):
        line = line.rstrip()

        if len(line) == 0:
            continue

        if line.endswith("#alt"):
            continue

        if line.endswith("#distractor"):
            continue

        solution = solution + line + "\n"

    return solution


def getParsonsAnswer(items):
    answer = ""
    for item in items:
        for i in range(0, item.get("indent", 0)):
            answer = answer + " "

        answer = answer + item.get("text", "") + "\n"

    return answer


def doesCodeMatch(codeA: str, codeB: str, strictIndentation: bool = False):

    codeA = re.sub("-----", "", codeA)
    codeB = re.sub("-----", "", codeB)

    if strictIndentation:
        return codeA == codeB

    normA = re.sub("\\s+", " ", codeA).strip()
    normB = re.sub("\\s+", " ", codeB).strip()

    # print("A", normA)
    # print("B", normB)

    return normA == normB


@dataclass
class Quiz:
    id: int
    name: str
    questions: list

    def getMaxScore(self):
        score = 0
        for question in self.questions:
            score = score + question.points

        return score

    def add_multichoice_solution(self, questionId: int, solution: Set[int]) -> bool:

        for question in self.questions:
            if question.type != "multichoice":
                continue

            if question.id != questionId:
                continue

            question.add_solution(solution)
            return True

        return False

    def add_parsons_solution(self, questionId: int, solution: str) -> bool:

        for question in self.questions:
            if question.type != "parsons":
                continue

            if question.id != questionId:
                continue

            question.add_solution(solution)
            return True

        return False


@dataclass
class Question:
    id: int
    points: int
    content: str
    type: str = field(default=None, init=False)

    def from_json(json: dict):
        question_type = json.get("data", {}).get("type", "unknown")
        if question_type == "multiple-choice":
            return MultichoiceQuestion.from_json(json)
        if question_type == "parsons":
            return ParsonsQuestion.from_json(json)
        if question_type == "short-answer":
            return ShortAnswerQuestion.from_json(json)


@dataclass
class ShortAnswerQuestion(Question):
    type = "short-answer"

    def from_json(json: dict):
        return ShortAnswerQuestion(
            json["id"], json["auto_points"], json.get("data", {}).get("content")
        )


@dataclass
class MultichoiceQuestion(Question):
    type = "multichoice"
    multiple_selection: bool
    options: List[str]
    solutions: List[Set[int]]

    def from_json(json: dict):
        return MultichoiceQuestion(
            json["id"],
            json["auto_points"],
            json.get("data", {}).get("content"),
            json.get("data", {}).get("multiple_selection", False),
            json.get("data", {}).get("answers", []),
            [json.get("data", {}).get("solution", [])],
        )

    def add_solution(self, solution: Set[int]):
        self.solutions.append(solution)


@dataclass
class ParsonsQuestion(Question):
    type = "parsons"
    solutions: List[str] = field(default_factory=list)

    def from_json(json: dict):
        return ParsonsQuestion(
            json["id"],
            json["auto_points"],
            json.get("data", {}).get("content"),
            [getParsonsSolutionFromSource(json.get("data", {}).get("source"))],
        )

    def add_solution(self, solution: str):
        self.solutions.append(solution)


@dataclass
class Answer:
    question_id: int
    created_at: datetime.datetime
    type: str = field(default=None, init=False)

    def from_json(j: dict):

        if type(j["data"]) == list:
            return MultichoiceAnswer.from_json(j)
        elif type(j["data"]) == str:
            return ShortAnswer.from_json(j)
        else:
            return ParsonsAnswer.from_json(j)


@dataclass
class MultichoiceAnswer(Answer):
    type = "multichoice"
    choices: Set[int]

    def from_json(j: dict):
        return MultichoiceAnswer(
            j["question_id"], dateutil.parser.isoparse(j["created_at"]), j["data"]
        )


@dataclass
class ParsonsAnswer(Answer):
    type = "parsons"
    code: str

    def from_json(j: dict):

        return ParsonsAnswer(
            j["question_id"],
            dateutil.parser.isoparse(j["created_at"]),
            getParsonsAnswer(j["data"]["items"]),
        )


@dataclass
class ShortAnswer(Answer):
    type = "shortanswer"
    text: str

    def from_json(j: dict):

        return ShortAnswer(
            j["question_id"], dateutil.parser.isoparse(j["created_at"]), j["data"]
        )


@dataclass
class QuizResult:
    quizId: int
    score: int = 0
    answersByQuestionId: Dict[int, Answer] = field(default_factory=dict)
    pointsByQuestionId: Dict[int, int] = field(default_factory=dict)

    def build(quizId: int, questions: List, answers: List):

        result = QuizResult(quizId)

        for answer in answers:
            result.answersByQuestionId[answer.question_id] = answer

        for question in questions:

            answer = result.answersByQuestionId.get(question.id)
            if answer is None:
                # result.pointsByQuestionId[question.id] = None
                continue

            if question.type == "multichoice":
                correct = False
                for solution in question.solutions:

                    if solution == answer.choices:
                        correct = True
                        break

                if correct:
                    result.score = result.score + question.points
                    result.pointsByQuestionId[question.id] = question.points
                else:
                    result.pointsByQuestionId[question.id] = 0

            if question.type == "parsons":
                correct = False
                for solution in question.solutions:
                    if doesCodeMatch(solution, answer.code, False):
                        correct = True
                        break

                if correct:
                    result.score = result.score + question.points
                    result.pointsByQuestionId[question.id] = question.points
                else:
                    result.pointsByQuestionId[question.id] = 0

        return result

    def print_summary(self, quiz: Quiz):

        print(
            f"  {self.score}/{quiz.getMaxScore()} points for "
            + quiz.name
            + " from the following questions:"
        )

        for index in range(0, len(quiz.questions)):
            question = quiz.questions[index]
            points = self.pointsByQuestionId.get(question.id)

            if points is None:
                print(f"    Q{index+1}: 0 points (unanswered)")
            elif points == 0:
                print(f"    Q{index+1}: 0 points (incorrect)")
            else:
                print(f"    Q{index + 1}: {points} points (correct)")
