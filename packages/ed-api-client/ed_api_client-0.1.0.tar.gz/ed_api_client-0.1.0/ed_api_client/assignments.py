from dataclasses import dataclass, field
from typing import List, Dict, Set
import datetime
import math

from ed_api_client import Slide, ChallengeResult, User, QuizResult, Quiz
from ed_api_client.challenges import ChallengeMarker, MarkType, Challenge


@dataclass
class Assignment:
    """
    An assignment against which students are graded

    Attributes
    ----------
    name : int
        The name of the assignment.
    marks : int
        The total available marks for this assignment
    maxScore : int
        The maximum score that users might achieve on this assignment. This depends on the gradeType:
            For BY_CHALLENGE this should be the number of challenges.
            For BY_TESTCASE this should be the number of test cases accross all challenges.
            For BY_TESTCASE_SCORE this should be the sum of all scores for all test cases across all challenges
    gradeType: GradeType
        The approach used for calculating grades
    deadline: datetime
        The default deadline beyond which submissions will be penalised.
    lessonIds: Set[int]
        The ids of all lessons involved in this assignment (note this is populated automatically as slides are added)
    slideIds: Set[int]
        The ids of all slides involved in this assignment (note this is populated automatically as slides are added)
    challengeIds: List[int]
        The ids of all challenges involved in this assignment (note this is populated automatically as slides are added)
    challengeNames: List[str]
        The names of all challenges involved in this assignment (note this is populated automatically as slides are added)
    extensionsByStudentId: Dict[int,datetime]
        Associates ids of students with deadlines that have been given to them (i.e. as extensions)

    Methods
    ----------
    add_slide (slide:Slide)
        Adds a slide (usually a code challenge) to this assignment
    add_extension (student: User, deadline:datetime)
        Provides the given student with an extension, until the given deadline
    get_deadline (student: Student) -> datetime
        Returns the deadline for the given student
    get_canvas_col ( ) -> str
        Returns the name of the column that would match this assignment in an gradebook exported from canvas.

    """

    name: str
    maxMarks: int
    marker: ChallengeMarker
    deadline: datetime.datetime
    challenges: List[Challenge] = field(default_factory=list)
    quizzes: List[Quiz] = field(default_factory=list)
    extensionsByStudentId: Dict[int, datetime.datetime] = field(default_factory=dict)
    dailyPenalty: float = 0.05

    def add_challenge_slide(self, slide: Slide):

        if slide.challengeId is None:
            raise ValueError("This slide is not a code challenge")

        self.challenges.append(Challenge(slide.challengeId, slide.id, slide.title))

    def add_quiz_slide(self, slide: Slide, questions: list):

        self.quizzes.append(Quiz(slide.id, slide.title, questions))

    def add_multichoice_solution(self, questionId: int, solution: Set[int]):

        for quiz in self.quizzes:

            if quiz.add_multichoice_solution(questionId, solution):
                return

        print(f"could not locate multichoice question {questionId}")

    def add_parsons_solution(self, questionId: int, solution: str):

        for quiz in self.quizzes:

            if quiz.add_parsons_solution(questionId, solution):
                return

        print(f"could not locate parsons question {questionId}")

    def add_extension(self, student, deadline):
        self.extensionsByStudentId[student.id] = deadline

    def add_extensions(self, students, deadline):
        for student in students:
            self.extensionsByStudentId[student.id] = deadline

    def get_deadline(self, student):
        if student.id in self.extensionsByStudentId:
            return self.extensionsByStudentId[student.id]

        return self.deadline

    def get_max_score(self):
        maxScore = 0
        for quiz in self.quizzes:
            maxScore = maxScore + quiz.getMaxScore()

        if self.marker.markType == MarkType.BY_CHALLENGE:
            maxScore = maxScore + (
                len(self.challenges) * self.marker.pointsPerChallenge
            )
        else:
            maxScore = maxScore + self.marker.maxTestCaseScore

        return maxScore

    def get_canvas_col(self):
        return "{} ({})".format(self.name, self.id)


@dataclass
class AssignmentResult:
    """
    Records the results of a student for an assignment.

    Marks for the assignment include a 10% penalty per day if work is received late.
    Late submissions are only considered if they improve the student's marks after the late penalty is applied.

    Attributes
    ----------
    studentId : int
        The id of the student
    completed : bool
        True if the student successfully completed this assignment, otherwise false.
    score : int
        The score recieved by this student
    mark : float
        The mark recieved by this student.
    daysLate: int
        The number of days past the deadline that work was received and considered.
    challengeResults: Dict[int, ChallengeResult]
        Associates ids of challenges with their individual results

    Methods
    ----------
    add (submission:Submission,  student:Student, assignment:Assignment)
        Updates this result based on a single submission
    finalize (assignment:Assignment, crawler: EdCrawler)
        To be called after all submissions have been added.
    """

    studentId: int
    score: int = None
    mark: float = None
    daysLate: int = None
    penalty: float = None
    challengeResults: Dict[int, ChallengeResult] = field(default_factory=dict)
    quizResults: Dict[int, QuizResult] = field(default_factory=dict)

    def add_challenge_submission(self, submission, student, assignment):

        deadline = assignment.get_deadline(student)

        daysLate = 0
        if submission.markedAt > deadline:
            diff = submission.markedAt - deadline
            daysLate = math.ceil(diff.total_seconds() / (60 * 60 * 24))

        if submission.challengeId not in self.challengeResults:
            self.challengeResults[submission.challengeId] = ChallengeResult()

        self.challengeResults[submission.challengeId].add(submission, daysLate)

    def add_quiz_result(self, quizResult: QuizResult):
        self.quizResults[quizResult.quizId] = quizResult

    def finalize(self, assignment: Assignment, crawler):

        self.score = 0
        self.mark = 0
        self.daysLate = 0
        self.penalty = 0

        quizScore = 0
        for quizResult in self.quizResults.values():
            quizScore = quizScore + quizResult.score

        if self.challengeResults is not None:
            for challengeId, challenge in self.challengeResults.items():
                challenge.finalize(assignment.marker, crawler)

        dailyMarkPenalty = assignment.dailyPenalty * assignment.maxMarks

        for daysLate in range(0, 6):
            score = quizScore

            for challengeId, challenge in self.challengeResults.items():
                score = score + challenge.scoresByCalendarDaysLate[daysLate]

            mark = assignment.maxMarks * (score / assignment.get_max_score())
            penalty = daysLate * dailyMarkPenalty
            mark = mark - penalty
            if mark < 0:
                mark = 0

            if mark > self.mark:
                self.score = score
                self.mark = mark
                self.daysLate = daysLate
                self.penalty = penalty

    def printSummary(self, student: User, assignment: Assignment):

        msg = f"{student.name} got {self.mark:.1f}/{assignment.maxMarks} marks from {self.score}/{assignment.get_max_score()} points"

        if self.daysLate > 0:
            msg = f"{msg} and a penalty of {self.penalty:.1f} marks for submitting {self.daysLate} days late"

        print(msg)

        for quiz in assignment.quizzes:
            quizResult = self.quizResults.get(quiz.id)

            if quiz.id is None:
                print(
                    f"  0/{quiz.getMaxScore()} points for "
                    + quiz.name
                    + " due to no attempt"
                )
            else:
                quizResult.print_summary(quiz)

        for challenge in assignment.challenges:

            challengeResult = self.challengeResults.get(challenge.id)
            if challengeResult is None:
                print(f"  0 points for " + challenge.name + " due to no attempt")
            else:
                challengeResult.print_summary(challenge, self.daysLate)
