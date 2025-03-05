import csv
from typing import Dict

from ed_api_client import Assignment, Users, AssignmentResult


class CanvasExporter:
    def __init__(self, students: Users):
        self.__students = students
        self.__assignmentsByCol = {}
        self.__resultsByCol = {}
        self.__fieldNames = ["Student", "ID", "SIS User ID", "SIS Login ID", "Section"]

    def addAssignment(
        self,
        assignment: Assignment,
        columnName: str,
        results: Dict[int, AssignmentResult],
    ):

        self.__assignmentsByCol[columnName] = assignment
        self.__resultsByCol[columnName] = results
        self.__fieldNames.append(columnName)
        return self

    def generateCsv(self, sourceCsv, targetCsv):

        with open(sourceCsv) as input:
            reader = csv.DictReader(input)

            with open(targetCsv, "w") as output:
                writer = csv.DictWriter(output, fieldnames=self.__fieldNames)
                writer.writeheader()

                for inputRow in reader:

                    outputRow = self.handleRow(inputRow)

                    if outputRow is None:
                        continue

                    writer.writerow(outputRow)

    def handleRow(self, inputRow: dict):

        studentEmail = inputRow.get("SIS Login ID")
        if studentEmail is None:
            return None

        student = self.__students.getByEmail(studentEmail.lower())
        if student is None:
            print(f"Could not locate student {studentEmail}")
            return None

        outputRow = {}
        for field in ["Student", "ID", "SIS User ID", "SIS Login ID", "Section"]:
            outputRow[field] = inputRow[field]

        for col, assignment in self.__assignmentsByCol.items():

            results = self.__resultsByCol.get(col, {}).get(student.id)
            if results is None:
                outputRow[col] = 0
            else:
                outputRow[col] = round(results.mark, 3)

        return outputRow
