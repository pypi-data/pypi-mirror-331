from dataclasses import dataclass, field
import datetime
from dateutil import parser
from typing import List, Dict
import operator

from ed_api_client.users import User

@dataclass
class Slide:
    """
    A single slide within an Ed lesson

    ...

    Attributes
    ----------
    id : int
        Unique id for the slide.
    lessonId : int
        The id of the lesson this slide belongs to
    challengeId : int
        If this slide represents a challenge that students can complete, then this will be a unique id useful for retrieving challenge submissions. Otherwise None.
    title : str
        The title of the slide
    type : str
        E.g.  code, document, video, etc.
    hidden : bool
        True if slide is currently hidden from students, otherwise false

    """

    id: int
    lessonId: int
    challengeId: int
    title: str
    type: str
    hidden: bool

    def from_json(s: dict):
        return Slide(
            s["id"],
            s["lesson_id"],
            s.get("challenge_id"),
            s["title"],
            s["type"],
            s["is_hidden"],
        )


@dataclass
class Lesson:
    """
    A lesson within a module

    ...

    Attributes
    ----------
    id : int
        Unique id for each lesson
    title : str
        The title of the lesson
    index : int
        For determining the order of the lesson within the module
    slides : List[Slide]
        A list of slides contained within the lesson

    Methods
    -------
    add_slide(slide : Slide)
        Adds a single slide to the lesson
    get_slide(slideId: int)
        Retrieves a slide with the given id
    """

    id: int
    title: str
    index: int
    slides: List[Slide] = field(default_factory=list)
    _slidesById: Dict[int, Slide] = field(default_factory=dict)

    def from_json(j: dict):
        return Lesson(j["id"], j["title"], j["index"])

    def add_slide(self, slide: Slide):
        if slide.id not in self._slidesById:
            self._slidesById[slide.id] = slide
            self.slides.append(slide)

    def get_slide(self, id: int) -> Slide:
        return self._slidesById.get(id)


@dataclass
class Module:
    """
    A module within the Ed lessons page

    ...

    Attributes
    ----------
    id : int
        Unique id for each module
    name : str
        The name of the module
    index : int
        For determining the order of the module in the lessons page
    lessons : List[Lesson]
        A list of lessons contained within the module

    Methods
    -------
    add_lesson(lesson : Lesson)
        Adds a single lesson to the module
    get_lesson(lessonId: int)
        Retrieves a lesson with the given id
    """

    id: int
    name: str
    index: int
    lessons: List[Lesson] = field(default_factory=list)
    _lessonsById: Dict[int, Lesson] = field(default_factory=dict)

    def add_lesson(self, lesson: Lesson):
        if lesson.id not in self._lessonsById:
            self._lessonsById[lesson.id] = lesson
            self.lessons.append(lesson)
            self.lessons.sort(key=operator.attrgetter("index"))

    def get_lesson(self, id: int) -> Lesson:
        return self._lessonsById.get(id)


@dataclass
class SlideResult:
    """
    Records whether a particular user has viewed, attempted or completed a particular slide

    ...

    Attributes
    ----------
    viewed : bool
        True if the user has viewed the slide, otherwise false
    attempted : bool
        True if the user has attempted the slide, otherwise false
    completed : bool
        True if the user has completed the slide, otherwise false

    """

    viewed: bool
    attempted: bool
    completed: bool

    def from_json(j: dict):
        return SlideResult(
            j.get("viewed", False),
            j.get("attempted", False),
            j.get("completed", False),
        )


@dataclass
class SlideResultSet:
    """
    Records student interactions with slides

    ...

    Methods
    ----------
    add (userId:int, slideId:int, result:SlideResult)
        Adds a record of a particular user interacting with a particular slide
    add_all (slideResults:SlideResultSet)
        Adds all records of users interacting with slides from the given result set
    get (userId:int, slideId:int) -> SlideResult
        Returns the record of a particular user interacting with a particular slide

    """

    _resultsByUserAndSlide: Dict[int, Dict[int, SlideResult]] = field(
        default_factory=dict
    )

    def add(self, userId: int, slideId: int, result: SlideResult):
        if not userId in self._resultsByUserAndSlide:
            self._resultsByUserAndSlide[userId] = {}

        self._resultsByUserAndSlide[userId][slideId] = result

    def add_all(self, slideResults):
        for userId, userResults in slideResults._resultsByUserAndSlide.items():
            for slideId, slideResult in userResults.items():
                self.add(userId, slideId, slideResult)

    def get(self, userId: int, slideId: int):
        return self._resultsByUserAndSlide.get(userId, {}).get(slideId)


@dataclass
class Override:
    """
    Records whether a particular user has viewed, attempted or completed a particular slide

    ...

    Attributes
    ----------
    viewed : bool
        True if the user has viewed the slide, otherwise false
    attempted : bool
        True if the user has attempted the slide, otherwise false
    completed : bool
        True if the user has completed the slide, otherwise false

    """
    id: int
    lessonId: int
    user: User
    dueAt: datetime.datetime

    def from_json(j: dict):

        return Override(
            j.get("id"),
            j.get("lesson_id"),
            User.from_json(j.get("user")),
            parser.parse(j.get("due_at_override"))
        )