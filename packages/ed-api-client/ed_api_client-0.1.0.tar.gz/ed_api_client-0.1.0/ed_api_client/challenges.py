from dataclasses import dataclass, field
from typing import List
from enum import Enum
import datetime
import dateutil.parser


@dataclass
class Challenge:
    id: int
    slideId: int
    name: str


class MarkType(Enum):
    """
    Different approaches used for grading assignments

    BY_CHALLENGE
        user recieves a point for each challenge they complete
    BY_TESTCASE
        user recieves a point for each testcase they pass, across all challenges
    BY_TESTCASE_SCORE
        user recieves points for each testcase they pass, across all challenges.
        The points recieved for each testcase is whatever score value was assigned
        to the testcase
    """

    BY_CHALLENGE = 1
    BY_TESTCASE = 2
    BY_TESTCASE_SCORE = 3


class ChallengeMarker:
    def __init__(self, markType: MarkType):
        self.markType = markType

    def passFail(pointsPerChallenge: int = 1):
        marker = ChallengeMarker(MarkType.BY_CHALLENGE)
        marker.pointsPerChallenge = pointsPerChallenge
        return marker

    def perTestCase(maxTestCaseScore: int):
        marker = ChallengeMarker(MarkType.BY_TESTCASE)
        marker.maxTestCaseScore = maxTestCaseScore
        return marker

    def perScoredTestCase(maxTestCaseScore: int):
        marker = ChallengeMarker(MarkType.BY_TESTCASE_SCORE)
        marker.maxTestCaseScore = maxTestCaseScore
        return marker


@dataclass
class TestCase:
    """
    A test case, that a user may or may not have passed

    ...

    Attributes
    ----------
    name : str
        The  name of the test case
    score : int
        The points assigned to this test case
    passed : bool
        True if the user has passed the test case, otherwise false

    """

    name: str
    score: int
    passed: bool

    def from_json(j: dict):
        return TestCase(j["name"], j["score"], j["passed"])


@dataclass
class Submission:
    """
    A submission that a user has made towards a challenge

    ...

    Attributes
    ----------
    id : int
        The unique id of the submission
    userId : int
        The id of the user who made the submission
    challengeId : int
        The id of the challenge this submission was made toward
    status : bool
        One of "passed", "failed", etc.
    testCasesPassed: int
        The number of test cases that this submission has passed
    testCasesTotal: int
        The number of test cases that this submission was tested against
        (Note this may be smaller than the number of test cases provided by the
        challenge, if the submission has compilation errors)
    markedAt: datetime
        A timestamp of when this submission was recieved and assessed
    testcases: List[TestCase]
        A list of details for each test case (Note this is only populated if you request
        a specific submission from the api. It will be left unpopulated by any requests that
        return multiple submissions)

    """

    id: int
    userId: int
    challengeId: int
    workspaceId: str
    status: str
    testCasesPassed: int
    testCasesTotal: int
    markedAt: datetime.datetime
    testcases: List[TestCase] = field(default_factory=list)

    def from_json(j: dict):
        submission = Submission(
            j["id"],
            j["user_id"],
            j["challenge_id"],
            j["workspace_id"],
            j["status"],
            j["testcase_pass_count"],
            j["testcase_total_count"],
            dateutil.parser.isoparse(j["marked_at"]),
        )

        for tc in j.get("result", {}).get("testcases", []):
            submission.testcases.append(TestCase.from_json(tc))

        return submission


@dataclass
class ChallengeResult:
    """
    Records the results of a student for a challenge within an assignment

    Attributes
    ----------
    attempts : int
        The number of attempts that the student submitted for this assignment.
    completed : bool
        True if the student successfully completed this challenge, otherwise false.
    bestSubmissionByCalendarDaysLate : List[Submission]
        The best submissions recieved by this student before and after the deadline.
            The first element contains the best submission recieved before the deadline.
            The second element contains the best submission recieved within one day after the deadline.
            The third element contains the best submission recieved between one and two days after the deadline. etc.
    scoresByCalendarDaysLate : List[int]
        The best scores recieved by this student before and after the deadline.
            The first element contains the best score recieved before the deadline.
            The second element contains the best score recieved within one day after the deadline.
            The third element contains the best score recieved between one and two days after the deadline. etc.
    firstAttempt: datetime
        A timestamp of this students first submission towards the assignment.
    lastAttempt: datetime
        A timestamp of this student's last submission towards the assignment.

    Methods
    ----------
    add (submission:Submission,  daysLate:  int)
        Updates this result based on a single submission
    finalize (assignment:Assignment, crawler: EdCrawler)
        To be called after all submissions have been added.
    """
    maxDaysLate: int = 7
    attempts: int = 0
    completed: bool = False
    bestSubmissionByCalendarDaysLate: List[Submission] = None
    scoresByCalendarDaysLate: List[int] = None
    firstAttempt: datetime.datetime = None
    lastAttempt: datetime.datetime = None

    def add(self, submission: Submission, daysLate: int):

        if self.bestSubmissionByCalendarDaysLate is None:
            self.bestSubmissionByCalendarDaysLate = [None] * (self.maxDaysLate + 1)
            self.scoresByCalendarDaysLate = [0] * (self.maxDaysLate + 1)

        self.attempts += 1
        if (
            submission.status == "passed"
            and submission.testCasesPassed == submission.testCasesTotal
        ):
            self.completed = True

        if self.firstAttempt is None or self.firstAttempt > submission.markedAt:
            self.firstAttempt = submission.markedAt
        if self.lastAttempt is None or self.lastAttempt < submission.markedAt:
            self.lastAttempt = submission.markedAt

        if daysLate <= self.maxDaysLate:
            if (
                self.bestSubmissionByCalendarDaysLate[daysLate] is None
                or self.bestSubmissionByCalendarDaysLate[daysLate].testCasesPassed
                < submission.testCasesPassed
            ):
                self.bestSubmissionByCalendarDaysLate[daysLate] = submission

    def finalize(self, marker: ChallengeMarker, crawler):
        for daysLate in range(0, self.maxDaysLate+1):
            submission = self.bestSubmissionByCalendarDaysLate[daysLate]
            if submission is None:
                continue

            if marker.markType is MarkType.BY_CHALLENGE:
                if (
                    submission.status == "passed"
                    and submission.testCasesPassed == submission.testCasesTotal
                ):
                    self.scoresByCalendarDaysLate[daysLate] = marker.pointsPerChallenge
            elif marker.markType is MarkType.BY_TESTCASE:
                self.scoresByCalendarDaysLate[daysLate] += submission.testCasesPassed
            elif marker.markType is MarkType.BY_TESTCASE_SCORE:
                # we have to fetch full submission details
                s = crawler.get_submission(submission.id)
                for test in s.testcases:
                    # print(test)
                    if test.passed:
                        self.scoresByCalendarDaysLate[daysLate] = (
                            self.scoresByCalendarDaysLate[daysLate] + test.score
                        )
            else:
                raise Exception(f"Invalid marker type {marker.markType}")

        # make sure scores can only go up
        for daysLate in range(1, self.maxDaysLate+1):
            if (
                self.scoresByCalendarDaysLate[daysLate]
                < self.scoresByCalendarDaysLate[daysLate - 1]
            ):
                self.scoresByCalendarDaysLate[daysLate] = self.scoresByCalendarDaysLate[
                    daysLate - 1
                ]

    def __get_best_day(self, daysLate: int):

        bestScore = 0
        bestDay = 0

        for day in range(0, daysLate + 1):
            if self.scoresByCalendarDaysLate[day] > bestScore:
                bestScore = self.scoresByCalendarDaysLate[day]
                bestDay = day

        return bestDay

    def print_summary(self, challenge: Challenge, daysLate: int):

        bestDay = self.__get_best_day(daysLate)
        bestScore = self.scoresByCalendarDaysLate[bestDay]

        print(
            f"  {bestScore} points for {challenge.name} from the following submissions:"
        )

        for day in range(0, len(self.scoresByCalendarDaysLate)):
            score = self.scoresByCalendarDaysLate[day]
            submission = self.bestSubmissionByCalendarDaysLate[day]
            if submission is None:
                continue

            submittedAt = submission.markedAt.strftime("%m/%d/%Y, %H:%M:%S")

            msg = f"    {score} points from {submission.testCasesPassed}/{submission.testCasesTotal} test cases @ {day} days overdue ({submittedAt})"

            if day < bestDay:
                msg = f"{msg} - superseded by later submission"
            elif day > bestDay:
                msg = f"{msg} - ignored for not overcoming late penalty"

            print(msg)
