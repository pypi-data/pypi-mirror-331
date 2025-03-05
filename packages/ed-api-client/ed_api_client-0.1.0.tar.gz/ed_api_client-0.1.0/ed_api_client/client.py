import operator
import requests
import time
import json

from ed_api_client import (
    User,
    Slide,
    Lesson,
    SlideResultSet,
    SlideResult,
    Module,
    Submission,
    Assignment,
    AssignmentResult,
    Question,
    Answer,
    Users,
    QuizResult,
    WorkspaceLog,
    ScaffoldSession, Override,
)


class EdClient:
    """
    Provides access to the Ed API

    Methods
    ----------

    get_user () -> User
        Retrieves details of the authenticated user
    get_users (courseId:int) -> List<User>
        Retrieves details of all users involved in the given course
    get_slides (lessonId:int) -> List<Slide>
        Retrieves all slides for the given lesson
    get_module_structure (courseId:int, fetchSlides:bool=False) -> List<Module>
        Retrieves all modules and lessons for the given course, and optionally all slides within each lesson
    get_slide_results (lessonId: int) -> SlideResultSet
        Retrieves records of student interactions with slides within the given lesson
    get_submission (submissionId: int) -> Submission
        Retrieves details of a single submission (i.e. a student hitting Mark).
        Note the returned submission will include details of indiviual test cases that are passed or failed.
    get_submissions (userId: int, challengeId: int) -> List<Submission>
        Retrieves details of all submissions made by the given student towards the given challenge.
        Note the returned submissions will not include details of indiviual test cases that are passed or failed.
    getResultsForStudent (assignment: Assignment, student: Student) -> AssignmentResult
        Retrieves the marks and other details for the given student and given assignment
    """

    def __init__(self, token):
        self.host = "https://edstem.org/api"
        self.session = requests.Session()
        # self.session.headers.update({"x-token": token})
        self.session.headers.update({"Authorization": f"Bearer {token}"})
        self.MAX_ATTEMPTS = 3
        self.DELAY = 60

    def __get_json(self, url, params=None):
        r = None

        for attempt in range(0, self.MAX_ATTEMPTS):
            r = self.session.get(url, params=params)

            if r.status_code >= 200 and r.status_code < 300:
                return r.json()

            if r.status_code == 429:
                # getting rate limited
                time.sleep(self.DELAY)

        print(
            "given up on request to {} after {} attempts, due to {}:{}".format(
                url, self.MAX_ATTEMPTS, r.status_code, r.content
            )
        )
        r.raise_for_status()

    def get_user(self) -> User:
        r = self.__get_json("{}/user".format(self.host))
        u = r.get("user")
        if u is None:
            return None

        return User.from_json(u)

    def get_users(self, courseId: int, role: str = None) -> Users:
        users = Users()

        r = self.__get_json("{}/courses/{}/admin".format(self.host, courseId))

        for u in r.get("users", []):
            user = User.from_json(u)
            if role is None or role == user.role:
                users.add(user)

        return users

    def get_slides(self, lessonId):
        slides = []

        r = self.__get_json("{}/lessons/{}".format(self.host, lessonId))

        for s in r.get("lesson", {}).get("slides", []):
            slides.append(Slide.from_json(s))

        return slides

    def get_slide(self, slideId):
        slides = []

        r = self.__get_json(f"{self.host}/lessons/slides/{slideId}")
        print(r)
        return Slide.from_json(r["slide"])

    def get_challenge(self, challengeId):
        slides = []

        r = self.__get_json(f"{self.host}/challenges/{challengeId}")
        print(r)
        # return Slide.from_json(r['slide'])

    def get_module_structure(self, courseId, fetch_slides=False):
        r = self.__get_json("{}/courses/{}/lessons".format(self.host, courseId))

        modules = []
        modulesById = {}
        moduleIndex = 0
        for m in r.get("modules", []):
            module = Module(m["id"], m["name"], moduleIndex)
            modules.append(module)
            modulesById[module.id] = module
            moduleIndex += 1

        for l in r.get("lessons", []):
            if l["is_hidden"]:
                continue

            moduleId = l.get("module_id")

            if moduleId is None or moduleId not in modulesById:
                continue

            lesson = Lesson.from_json(l)
            modulesById[moduleId].add_lesson(lesson)

            if fetch_slides:
                for slide in self.get_slides(lesson.id):
                    lesson.add_slide(slide)

        modules.sort(key=operator.attrgetter("index"))
        return modules

    def get_slide_results(self, lessonId):
        r = self.__get_json("{}/lessons/{}/results".format(self.host, lessonId))

        results = SlideResultSet()

        for user in r:
            userId = user["user_id"]

            for slide in user.get("slides", []):
                slideId = slide["slide_id"]
                results.add(userId, slideId, SlideResult(slide))

        return results

    def get_submission(self, submissionId):
        r = self.__get_json(
            "{}/challenges/submissions/{}".format(self.host, submissionId)
        )
        s = r.get("submission")

        if s is None:
            return None

        return Submission.from_json(s)

    def get_submissions(self, userId, challengeId):
        submissions = []
        r = self.__get_json(
            "{}/users/{}/challenges/{}/submissions".format(
                self.host, userId, challengeId
            )
        )

        for s in r.get("submissions", []):
            submissions.append(Submission.from_json(s))

        return submissions

    def get_scaffold(self, challengeId: str):

        r = self.__get_json(f"{self.host}/challenges/{challengeId}/scaffold")
        print(json.dumps(r))

    def get_workspace_log(self, workspaceId: str) -> WorkspaceLog:

        r = self.__get_json(f"{self.host}/workspaces/{workspaceId}/logs")
        # print(r['challenge_attempts'], r['challenge_results'])

        return WorkspaceLog.from_json(r)

    def getResultsForStudent(
        self, assignment: Assignment, student: User
    ) -> AssignmentResult:
        result = AssignmentResult(student.id)

        for quiz in assignment.quizzes:
            answers = self.getAnswers(quiz.id, student.id)
            result.add_quiz_result(QuizResult.build(quiz.id, quiz.questions, answers))

        for challenge in assignment.challenges:
            submissions = self.get_submissions(student.id, challenge.id)

            submissions.sort(key=lambda x: x.markedAt)

            for submission in submissions:
                result.add_challenge_submission(submission, student, assignment)

        result.finalize(assignment, self)
        return result

    def getQuestions(self, slideId):

        questions = []
        r = self.__get_json(f"{self.host}/lessons/slides/{slideId}/questions")

        for q in r.get("questions", []):
            questions.append(Question.from_json(q))

        return questions

    def getAnswers(self, slideId, userId):

        answers = []
        r = self.__get_json(
            f"{self.host}/lessons/slides/{slideId}/questions/responses?user_id={userId}"
        )

        for a in r.get("responses", []):

            if a.get("data") is None:
                continue

            answers.append(Answer.from_json(a))

        return answers

    def get_scaffold_files(self, challengeId):

        r = self.session.post(f"{self.host}/challenges/{challengeId}/connect/scaffold")
        ticket = r.json().get("ticket")

        session = ScaffoldSession(ticket)
        session.start()

        return list(session.filesById.values())

    def get_overrides(self, courseId:int, lessonId:int):

        r = self.__get_json(
            f"{self.host}/courses/{courseId}/overrides",
            {'lesson_id' : lessonId}
        )

        overrides = []
        for o in r.get('overrides',[]):
            overrides.append(Override.from_json(o))

        return overrides