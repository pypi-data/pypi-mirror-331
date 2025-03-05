from dataclasses import dataclass, field
from typing import List, Dict, Set
import datetime
import dateutil.parser
import pylcs
import re

from ed_api_client.websockets import File


def getOverlap(idx):

    aStart = None
    aEnd = None

    bStart = None
    bEnd = None

    for i in range(0, len(idx)):
        if idx[i] >= 0:
            if aStart is None:
                aStart = i
                bStart = idx[i]
        else:
            if aStart is not None:
                aEnd = i
                bEnd = idx[i - 1] + 1
                break

    if aStart is None:
        return None, None

    if aEnd is None:
        aEnd = len(idx)
        bEnd = idx[len(idx) - 1] + 1

    return (aStart, aEnd), (bStart, bEnd)


def getMaskedSection(text, start=None, end=None, maskChar="~"):
    if start is None:
        start = 0

    if end is None:
        end = len(text)

    return "".join(
        [text[i] if text[i] == "\n" else maskChar for i in range(start, end)]
    )


def getCodeCharacterCount(text):

    count = 0

    for i in range(0, len(text)):
        if text[i].isspace():
            continue
        if text[i] == "}" or text[i] == ")":
            continue

        count += 1

    return count


def getMaskedProportion(text, maskChar="~", ignoreChar='#'):

    whitespaceCount = 0
    maskedCount = 0
    unmaskedCount = 0

    for i in range(0, len(text)):
        if text[i].isspace() or text[i] == ignoreChar:
            whitespaceCount += 1
        elif text[i] == maskChar:
            maskedCount += 1
        else:
            unmaskedCount += 1

    if maskedCount + unmaskedCount == 0:
        return 0
    else:
        return maskedCount / (maskedCount + unmaskedCount)


def getPastedSections(code, pastes, minOverlapLength=5):

    offsets = []
    for i in range(0, len(code)):
        if code[i].isspace():
            continue
        offsets.append(i)

    # print(code)
    # print(offsets)

    maskedCode = re.sub(r"\s+", "", code)
    pastedSections = []

    ps = [re.sub(r"\s+", "", p) for p in pastes]

    while len(ps) > 0:

        ps.sort(key=len, reverse=True)

        paste = ps.pop(0)
        if len(paste) < minOverlapLength:
            break

        idx = pylcs.lcs_string_idx(maskedCode, paste)

        overlapCode, overlapPaste = getOverlap(idx)
        if overlapCode is None:
            continue

        overlapLength = overlapCode[1] - overlapCode[0]

        if overlapLength < minOverlapLength:
            continue

        pastedSections.append(
            (offsets[overlapCode[0]], offsets[overlapCode[1] - 1] + 1)
        )

        maskedCode = (
            maskedCode[: overlapCode[0]]
            + ("~" * overlapLength)
            + maskedCode[overlapCode[1] :]
        )

        pasteRemainderA = paste[: overlapPaste[0]]
        if len(pasteRemainderA) >= minOverlapLength:
            ps.append(pasteRemainderA)

        pasteRemainderB = paste[overlapPaste[1] :]
        if len(pasteRemainderB) >= minOverlapLength:
            ps.append(pasteRemainderB)

    return pastedSections


@dataclass
class Event:
    at: datetime.datetime
    clientId: int
    userId: int

    type: str = field(default=None, init=False)

    def from_json(json: dict):

        t = json.get("type")
        if t == "join":
            return JoinEvent.from_json(json)
        if t == "init":
            return InitEvent.from_json(json)
        if t == "cursor":
            return CursorEvent.from_json(json)
        if t == "edit":
            return EditEvent.from_json(json)
        if t == "leave":
            return LeaveEvent.from_json(json)

        print("unhandled event type", t, json)


@dataclass
class AttemptEvent(Event):
    type = "attempt"

    def from_timestamp(timestamp: str):
        return AttemptEvent(dateutil.parser.isoparse(timestamp), None, None)


@dataclass
class SubmissionEvent(Event):
    type = "submission"
    passed: bool

    def from_json(json: dict):
        return SubmissionEvent(
            dateutil.parser.isoparse(json["at"]), None, None, json["passed"]
        )


@dataclass
class JoinEvent(Event):
    type = "join"

    def from_json(json: dict):
        return JoinEvent(
            dateutil.parser.isoparse(json["at"]), json["client_id"], json["user_id"]
        )


@dataclass
class LeaveEvent(Event):
    type = "leave"

    def from_json(json: dict):
        return LeaveEvent(
            dateutil.parser.isoparse(json["at"]), json["client_id"], json["user_id"]
        )


@dataclass
class InitEvent(Event):

    type = "init"
    fileId: int
    contents: str

    def from_json(json: dict):
        # print(json)
        return InitEvent(
            dateutil.parser.isoparse(json["at"]),
            json["client_id"],
            json["user_id"],
            json.get("data", {}).get("file_id", ""),
            json.get("data", {}).get("contents", ""),
        )


@dataclass
class CursorEvent(Event):
    type = "cursor"
    cursorStart: int
    cursorEnd: int
    fileId: int

    def from_json(json: dict):
        # print(json)

        cursor = json.get("data", {}).get("cursor")

        return CursorEvent(
            dateutil.parser.isoparse(json["at"]),
            json["client_id"],
            json["user_id"],
            None if cursor is None else cursor["start"],
            None if cursor is None else cursor["end"],
            json.get("data", {}).get("file_id"),
        )


@dataclass
class EditEvent(Event):
    type = "edit"
    fileId: int
    edits: List[Event] = field(default_factory=list)

    def from_json(json: dict):
        # print(json)

        event = EditEvent(
            dateutil.parser.isoparse(json["at"]),
            json["client_id"],
            json["user_id"],
            json.get("data", {}).get("file_id"),
        )

        for e in json.get("data", {}).get("edits", []):
            event.edits.append(Edit.from_json(e))

        return event


@dataclass
class Edit:
    type: str = field(default=None, init=False)

    def from_json(json: dict):
        t = json.get("type")
        if t == "skip":
            return SkipEdit.from_json(json)
        if t == "insert":
            return InsertEdit.from_json(json)
        if t == "delete":
            return DeleteEdit.from_json(json)

        print("unhandled edit type", t, json)


@dataclass
class SkipEdit(Edit):
    type = "skip"
    value: int

    def from_json(json: dict):
        return SkipEdit(json["value"])


@dataclass
class InsertEdit(Edit):
    type = "insert"
    value: str

    def from_json(json: dict):
        return InsertEdit(json["value"])


@dataclass
class DeleteEdit(Edit):
    type = "delete"
    value: int

    def from_json(json: dict):
        return DeleteEdit(json["value"])


@dataclass
class WorkspaceLog:
    events: List[Event] = field(default_factory=list)

    def from_json(json: dict):

        attemptsAndResults = []
        for ca in json.get("challenge_attempts", []):
            attemptsAndResults.append(AttemptEvent.from_timestamp(ca))

        for cr in json.get("challenge_results", []):
            attemptsAndResults.append(SubmissionEvent.from_json(cr))

        # print(attemptsAndResults)

        attemptsAndResults = sorted(attemptsAndResults, key=lambda d: d.at)

        # print(attemptsAndResults)

        log = WorkspaceLog()
        for e in json.get("events", []):

            event = Event.from_json(e)
            if event is None:
                continue

            while len(attemptsAndResults) > 0 and attemptsAndResults[0].at < event.at:
                log.events.append(attemptsAndResults.pop(0))

            log.events.append(event)

        while len(attemptsAndResults) > 0:
            log.events.append(attemptsAndResults.pop(0))

        return log


@dataclass
class FileSummary(File):
    activeTime: datetime.timedelta = datetime.timedelta(0)
    prevActiveTime: datetime.datetime = None

    typingTime: datetime.timedelta = datetime.timedelta(0)
    prevTypingTime: datetime.datetime = None

    externalPastes: List[str] = field(default_factory=list)

    pastedProportion: float = 0
    pastedMask: str = ""

    transcribedProportion: float = 0
    transcribedMask: str = ""

    editCount: int = 0

    def from_file(file: File):
        fs = FileSummary(file.id, file.path, file.content)
        fs.pastedMask = getMaskedSection(file.content, maskChar='#')
        fs.transcribedMask = getMaskedSection(file.content, maskChar='#')
        return fs


@dataclass
class WorkspaceSummary:

    totalActiveTime: datetime.timedelta
    totalTypingTime: datetime.timedelta

    fileSummaries: Dict[int, FileSummary]

    def from_log(
        files: List[File],
        log: WorkspaceLog,
        stopAtFirstSuccessfullSubmission: bool = True,
        maxIdleSeconds=30,
        minSuspiciousPasteChars=50,
        maxContinuousTypingSeconds=2,
    ):

        fileSummaries = {}
        for file in files:
            fileSummaries[file.id] = FileSummary.from_file(file)

        selections = set()

        currSelection = None
        for event in log.events:

            if event is None:
                continue

            # print(event)
            if event.type == "submission":
                if event.passed and stopAtFirstSuccessfullSubmission:
                    break

            if event.type != "cursor" and event.type != "edit" and event.type != "init":
                continue

            file = fileSummaries.get(event.fileId)
            if file is None:
                continue

            if file.prevActiveTime is not None:
                elapsed = event.at - file.prevActiveTime
                if elapsed.total_seconds() < maxIdleSeconds:
                    file.activeTime += elapsed

            file.prevActiveTime = event.at

            if event.type == "init":
                # file has been reset
                file.content = event.contents
                file.transcribedMask = event.contents
                file.pastedMask = event.contents

            if event.type == "cursor":
                if event.cursorStart is None or event.cursorEnd is None:
                    currSelection = None
                    continue

                if event.cursorEnd - event.cursorStart > minSuspiciousPasteChars:
                    currSelection = (event.cursorStart, event.cursorEnd)
                    selection = file.content[event.cursorStart : event.cursorEnd]
                    selections.add(selection.strip())

            if event.type != "edit":
                continue

            pos = 0

            isUninterrupted = False
            if file.prevTypingTime is not None:
                elapsed = event.at - file.prevTypingTime
                if elapsed.total_seconds() < maxContinuousTypingSeconds:
                    isUninterrupted = True

                if elapsed.total_seconds() < maxIdleSeconds:
                    file.typingTime += elapsed

            file.prevTypingTime = event.at

            for edit in event.edits:
                if edit.type == "skip":
                    pos = pos + edit.value
                    currSelection = None

                if edit.type == "delete":
                    file.content = file.content[:pos] + file.content[pos + edit.value :]
                    file.transcribedMask = (
                        file.transcribedMask[:pos]
                        + file.transcribedMask[pos + edit.value :]
                    )

                if edit.type == "insert":

                    if currSelection is not None:
                        print(
                            f"Inserting {len(edit.value)} to replace selection: ({currSelection[0]}, {currSelection[1]})"
                        )
                    if (
                        isUninterrupted
                        and getCodeCharacterCount(file.content[pos:]) < 5
                    ):
                        file.transcribedMask = (
                            file.transcribedMask[:pos]
                            + getMaskedSection(edit.value)
                            + file.transcribedMask[pos:]
                        )
                    else:
                        file.transcribedMask = (
                            file.transcribedMask[:pos]
                            + edit.value
                            + file.transcribedMask[pos:]
                        )

                    if len(edit.value) > minSuspiciousPasteChars:
                        if edit.value.strip() not in selections:
                            # print(edit.value.replace('\n', '>'))
                            # print(file.content.replace('\n', '>'))
                            file.externalPastes.append(edit.value)

                    file.content = file.content[:pos] + edit.value + file.content[pos:]
                    pos = pos + len(edit.value)

            # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>')
            # print(edit)
            # print(file.content)
            # print('>>>>>>>>>>>>>>>>>>>>>>>>>>>>')

            # if "}\n\nimport java.util.ArrayList;" in file.content:
            #    break

        totalActiveTime = datetime.timedelta(0)
        totalTypingTime = datetime.timedelta(0)
        for fileId, file in fileSummaries.items():
            totalActiveTime += file.activeTime
            totalTypingTime += file.typingTime

            pastedSections = getPastedSections(
                file.content, file.externalPastes, minSuspiciousPasteChars
            )
            file.pastedMask = file.content
            pastedLength = 0
            for section in pastedSections:
                sectionLength = section[1] - section[0]
                file.pastedMask = (
                    file.pastedMask[: section[0]]
                    + getMaskedSection(file.pastedMask, section[0], section[1])
                    + file.pastedMask[section[1] :]
                )
                pastedLength += sectionLength

            if len(file.content) > 0:
                file.pastedProportion = pastedLength / len(file.content)

                file.transcribedProportion = getMaskedProportion(file.transcribedMask)

        return WorkspaceSummary(totalActiveTime, totalTypingTime, fileSummaries)
