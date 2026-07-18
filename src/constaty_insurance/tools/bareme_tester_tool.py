import json
from typing import Any, ClassVar, Type

from crewai.tools import BaseTool
from pydantic import BaseModel, Field


class BaremeTesterInput(BaseModel):
    predicted_case_no: int = Field(
        ...,
        ge=1,
        le=25,
        description="Predicted FTUSA barème case number from 1 to 25.",
    )
    responsibility_x_pct: int = Field(
        ...,
        ge=0,
        le=100,
        description="Predicted responsibility percentage for vehicle X.",
    )
    responsibility_y_pct: int = Field(
        ...,
        ge=0,
        le=100,
        description="Predicted responsibility percentage for vehicle Y.",
    )
    detected_features: list[str] = Field(
        default_factory=list,
        description="Canonical accident features detected by the agent.",
    )
    explanation: str = Field(
        ...,
        description="Short explanation supporting the case classification.",
    )


class BaremeTesterTool(BaseTool):
    name: str = "BaremeTesterTool"
    description: str = (
        "Deterministically validates a predicted accident case against the "
        "Tunisian FTUSA 25-case responsibility barème. It checks the selected "
        "case, X/Y responsibility percentages, and required canonical features."
    )
    args_schema: Type[BaseModel] = BaremeTesterInput

    # FTUSA "Barème de responsabilité", 1 June 1999.
    # Cases 24 and 25 are multi-vehicle rules; percentages are encoded
    # pairwise as X = vehicle ahead/damaged and Y = striking vehicle.
    BAREME_CASES: ClassVar[dict[int, dict[str, Any]]] = {
        1: {
            "category": "same_direction_same_road",
            "title": "Vehicle X struck on the rear",
            "expected_x_pct": 0,
            "expected_y_pct": 100,
            "required_features": ["same_direction", "same_lane", "x_rear_impact"],
        },
        2: {
            "category": "same_direction_same_road",
            "title": "Sideswipe without a lane change",
            "expected_x_pct": 50,
            "expected_y_pct": 50,
            "required_features": ["same_direction", "different_lanes", "sideswipe", "no_lane_change"],
        },
        3: {
            "category": "same_direction_same_road",
            "title": "Y changes lane while X overtakes on the median axis",
            "expected_x_pct": 50,
            "expected_y_pct": 50,
            "required_features": ["same_direction", "y_lane_change", "x_overtaking", "x_on_median_axis"],
        },
        4: {
            "category": "same_direction_same_road",
            "title": "Vehicle Y changes lane",
            "expected_x_pct": 0,
            "expected_y_pct": 100,
            "required_features": ["same_direction", "different_lanes", "y_lane_change"],
        },
        5: {
            "category": "same_direction_same_road",
            "title": "Vehicle Y leaves a parking position",
            "expected_x_pct": 0,
            "expected_y_pct": 100,
            "required_features": ["y_leaving_parking", "x_in_traffic_lane"],
        },
        6: {
            "category": "opposite_directions",
            "title": "Vehicle Y crosses or straddles the median axis",
            "expected_x_pct": 0,
            "expected_y_pct": 100,
            "required_features": ["opposite_directions", "y_crosses_median", "x_in_own_lane"],
        },
        7: {
            "category": "opposite_directions",
            "title": "Both vehicles cross the median or their positions are indeterminate",
            "expected_x_pct": 50,
            "expected_y_pct": 50,
            "required_features": ["opposite_directions", "median_position_indeterminate_or_both_cross"],
        },
        8: {
            "category": "different_roads",
            "title": "Priority vehicle X crosses the median axis",
            "expected_x_pct": 25,
            "expected_y_pct": 75,
            "required_features": ["different_roads", "x_has_priority", "x_crosses_median", "y_in_own_lane"],
        },
        9: {
            "category": "different_roads",
            "title": "Vehicle X has right-hand priority and remains in its lane",
            "expected_x_pct": 0,
            "expected_y_pct": 100,
            "required_features": ["different_roads", "x_has_right_priority", "x_in_own_lane"],
        },
        10: {
            "category": "parked_or_stopped",
            "title": "Vehicle X is legally parked or stopped",
            "expected_x_pct": 0,
            "expected_y_pct": 100,
            "required_features": ["x_parked_or_stopped", "x_position_regular"],
        },
        11: {
            "category": "parked_or_stopped",
            "title": "Vehicle X is illegally parked in an urban area without obstructing traffic",
            "expected_x_pct": 0,
            "expected_y_pct": 100,
            "required_features": ["x_parked_or_stopped", "urban_area", "x_position_illegal", "no_traffic_obstruction"],
        },
        12: {
            "category": "parked_or_stopped",
            "title": "Vehicle X is illegally parked in an urban area and obstructs traffic",
            "expected_x_pct": 25,
            "expected_y_pct": 75,
            "required_features": ["x_parked_or_stopped", "urban_area", "x_position_illegal", "traffic_obstruction"],
        },
        13: {
            "category": "parked_or_stopped",
            "title": "Vehicle X is irregularly parked or stopped outside an urban area",
            "expected_x_pct": 50,
            "expected_y_pct": 50,
            "required_features": ["x_parked_or_stopped", "outside_urban_area", "x_position_irregular"],
        },
        14: {
            "category": "special",
            "title": "Vehicle Y disobeys traffic control or road signage",
            "expected_x_pct": 0,
            "expected_y_pct": 100,
            "required_features": ["y_disobeys_traffic_control_or_sign"],
        },
        15: {
            "category": "special",
            "title": "Vehicle Y reverses, makes a U-turn, or performs a parking manoeuvre",
            "expected_x_pct": 0,
            "expected_y_pct": 100,
            "required_features": ["y_reversing_u_turn_or_parking_manoeuvre"],
        },
        16: {
            "category": "special",
            "title": "Vehicle Y exits parking, private property, or a dirt road",
            "expected_x_pct": 0,
            "expected_y_pct": 100,
            "required_features": ["y_exits_parking_private_place_or_dirt_road"],
        },
        17: {
            "category": "special",
            "title": "Vehicle X enters parking, private property, or a dirt road without changing lane",
            "expected_x_pct": 0,
            "expected_y_pct": 100,
            "required_features": ["x_enters_parking_private_place_or_dirt_road", "x_no_lane_change"],
        },
        18: {
            "category": "special",
            "title": "Vehicle X enters parking, private property, or a dirt road while changing lane",
            "expected_x_pct": 100,
            "expected_y_pct": 0,
            "required_features": ["x_enters_parking_private_place_or_dirt_road", "x_lane_change"],
        },
        19: {
            "category": "special",
            "title": "A door of vehicle Y is opened",
            "expected_x_pct": 0,
            "expected_y_pct": 100,
            "required_features": ["y_door_open"],
        },
        20: {
            "category": "special",
            "title": "Vehicle Y causes damage with stones or transported objects",
            "expected_x_pct": 0,
            "expected_y_pct": 100,
            "required_features": ["damage_from_y_stones_or_transported_objects"],
        },
        21: {
            "category": "special",
            "title": "Vehicle Y drives without lights outside an urban area",
            "expected_x_pct": 0,
            "expected_y_pct": 100,
            "required_features": ["y_without_lights", "outside_urban_area"],
        },
        22: {
            "category": "special",
            "title": "Vehicle Y drives without lights inside an urban area",
            "expected_x_pct": 50,
            "expected_y_pct": 50,
            "required_features": ["y_without_lights", "urban_area"],
        },
        23: {
            "category": "special",
            "title": "Disagreement about the traffic-light phase or accident origin",
            "expected_x_pct": 50,
            "expected_y_pct": 50,
            "required_features": ["traffic_light_or_origin_disputed"],
        },
        24: {
            "category": "special",
            "title": "Chain collision",
            "expected_x_pct": 0,
            "expected_y_pct": 100,
            "required_features": ["chain_collision", "y_is_last_vehicle_in_chain"],
        },
        25: {
            "category": "special",
            "title": "Successive impacts",
            "expected_x_pct": 0,
            "expected_y_pct": 100,
            "required_features": ["successive_impacts", "y_hits_vehicle_ahead"],
        },
    }

    def _run(
        self,
        predicted_case_no: int,
        responsibility_x_pct: int,
        responsibility_y_pct: int,
        detected_features: list[str],
        explanation: str,
    ) -> str:
        case = self.BAREME_CASES.get(predicted_case_no)
        if case is None:
            return json.dumps(
                {
                    "passed": False,
                    "expected_case_title": "Unknown FTUSA barème case",
                    "expected_x_pct": 0,
                    "expected_y_pct": 0,
                    "received_x_pct": responsibility_x_pct,
                    "received_y_pct": responsibility_y_pct,
                    "matched_features": [],
                    "missing_features": [],
                    "notes": "predicted_case_no must be between 1 and 25.",
                },
                ensure_ascii=False,
            )

        normalized_features = {
            feature.strip().lower() for feature in detected_features if feature.strip()
        }
        required_features = {
            feature.lower() for feature in case["required_features"]
        }
        matched_features = sorted(required_features & normalized_features)
        missing_features = sorted(required_features - normalized_features)

        percentages_match = (
            responsibility_x_pct == case["expected_x_pct"]
            and responsibility_y_pct == case["expected_y_pct"]
            and responsibility_x_pct + responsibility_y_pct == 100
        )
        passed = percentages_match and not missing_features

        notes: list[str] = []
        if not percentages_match:
            notes.append("The predicted X/Y responsibility split does not match the selected case.")
        if missing_features:
            notes.append("One or more required case features are missing.")
        if passed:
            notes.append("Case number, responsibility split, and required features match.")
        if explanation.strip():
            notes.append(f"Agent explanation received: {explanation.strip()}")

        result = {
            "passed": passed,
            "expected_case_title": case["title"],
            "expected_x_pct": case["expected_x_pct"],
            "expected_y_pct": case["expected_y_pct"],
            "received_x_pct": responsibility_x_pct,
            "received_y_pct": responsibility_y_pct,
            "matched_features": matched_features,
            "missing_features": missing_features,
            "notes": " ".join(notes),
        }
        return json.dumps(result, ensure_ascii=False)
