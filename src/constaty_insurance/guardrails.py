from typing import Any

from crewai import TaskOutput
from pydantic import ValidationError

from constaty_insurance.models import ConstatTaskOutput


def maximum_two_questions(result: TaskOutput) -> tuple[bool, Any]:
    if result.json_dict is None:
        return False, "Return valid JSON matching the required constat schema."

    try:
        validated = ConstatTaskOutput.model_validate(result.json_dict)
    except ValidationError as error:
        return False, f"The JSON does not match the required schema: {error}"

    if len(validated.follow_up_questions) > 2:
        return False, "Return no more than 2 follow-up questions."

    return True, validated.model_dump_json()
