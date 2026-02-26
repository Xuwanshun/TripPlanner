import json
import os
import re
import html
from datetime import datetime
from typing import Type, Literal, Optional, Dict, Any, List, Union

import requests
from pydantic import BaseModel, Field
from crewai.tools import BaseTool

class RoutePlannerInput(BaseModel):
    origin: str = Field(..., description="Starting point (address/place name)")
    destination: str = Field(..., description="Ending point (address/place name)")
    travel_mode: Literal["driving", "walking", "bicycling", "transit"] = Field(
        "transit",
        description="Travel mode: driving|walking|bicycling|transit",
    )
    departure_time: Optional[str] = Field(
        None,
        description=(
            "Optional. 'now' OR ISO datetime "
            "(e.g. 2026-02-26T09:00:00 or 2026-02-26T09:00:00+09:00). "
            "Used mainly for transit/driving traffic estimates."
        ),
    )
    language: str = Field("en", description="Language for returned instructions (e.g. en, zh-CN)")
    region: Optional[str] = Field(
        None,
        description="Optional. Region bias as ccTLD (e.g. 'us', 'jp', 'cn').",
    )
    alternatives: bool = Field(
        False,
        description="Whether to request alternative routes (Directions API).",
    )
    debug: bool = Field(
        False,
        description="If true, prints request/response debug information to stdout.",
    )


class RoutePlannerTool(BaseTool):
    """
    Route planner tool using Google Maps APIs:
      - Distance Matrix API: distance + duration
      - Directions API: step-by-step route instructions + overview polyline
    """

    name: str = "Route planner (Google Maps)"
    description: str = (
        "Compute travel distance/time and a step-by-step route between two places "
        "using Google Distance Matrix + Directions."
    )
    args_schema: Type[BaseModel] = RoutePlannerInput

    def _run(
        self,
        origin: str,
        destination: str,
        travel_mode: str = "transit",
        departure_time: Optional[str] = None,
        language: str = "en",
        region: Optional[str] = None,
        alternatives: bool = False,
        debug: bool = False,
    ) -> str:
        api_key = os.environ.get("GOOGLE_MAPS_API_KEY")
        if not api_key:
            return json.dumps(
                {"error": "Missing GOOGLE_MAPS_API_KEY in environment."},
                ensure_ascii=False,
                indent=2,
            )

        # ---------- Helpers ----------
        def _safe_get(d: Any, path: List[Union[str, int]], default=None):
            """Safely traverse nested dict/list structures."""
            cur = d
            for p in path:
                if isinstance(cur, dict):
                    if p not in cur:
                        return default
                    cur = cur[p]
                elif isinstance(cur, list):
                    if not isinstance(p, int) or p < 0 or p >= len(cur):
                        return default
                    cur = cur[p]
                else:
                    return default
            return cur

        def _mask_key(params: Dict[str, Any]) -> Dict[str, Any]:
            masked = dict(params)
            if "key" in masked and masked["key"]:
                masked["key"] = "***MASKED***"
            return masked

        def _mask_url_key(url: str) -> str:
            # Masks query parameter "key=..."
            return re.sub(r"([?&]key=)[^&]+", r"\1***MASKED***", url)

        def _debug_print(title: str, data: Any):
            if debug:
                print(f"\n[DEBUG] {title}")
                try:
                    print(json.dumps(data, ensure_ascii=False, indent=2))
                except Exception:
                    print(str(data))

        def _html_to_text(s: Optional[str]) -> Optional[str]:
            """Convert Google html_instructions into readable plain text."""
            if not s:
                return s
            txt = s.replace("<wbr/>", "")
            # Preserve div notes like "Toll road" / "Destination will be on the left"
            txt = re.sub(r"<div[^>]*>", " — ", txt, flags=re.IGNORECASE)
            txt = re.sub(r"</div>", "", txt, flags=re.IGNORECASE)
            txt = re.sub(r"<[^>]+>", "", txt)
            txt = html.unescape(txt)
            txt = " ".join(txt.split())
            return txt

        def _parse_departure_time(dt: Optional[str]) -> Optional[Union[str, int]]:
            """
            Google supports:
              - departure_time=now
              - departure_time=UNIX seconds (int)
            """
            if not dt:
                return None

            s = dt.strip()
            if s.lower() == "now":
                return "now"

            try:
                iso_s = s.replace("Z", "+00:00")
                parsed = datetime.fromisoformat(iso_s)
                return int(parsed.timestamp())
            except Exception:
                return None

        def _api_error_payload(stage: str, api_name: str, data: Dict[str, Any]) -> Dict[str, Any]:
            status = data.get("status")
            error_message = data.get("error_message")

            # Friendly message mapping
            friendly = {
                "REQUEST_DENIED": "API request denied. Check API key restrictions and whether the API is enabled.",
                "OVER_QUERY_LIMIT": "Quota exceeded or rate-limited. Check billing/quota settings.",
                "INVALID_REQUEST": "Invalid request parameters sent to Google Maps API.",
                "MAX_ELEMENTS_EXCEEDED": "Too many origins/destinations for Distance Matrix request.",
                "MAX_DIMENSIONS_EXCEEDED": "Request dimensions exceed API limits.",
                "ZERO_RESULTS": "No route found for the selected mode between origin and destination.",
                "UNKNOWN_ERROR": "Google Maps API temporary server error. Retry may succeed.",
            }.get(status, f"{api_name} returned an error.")

            return {
                "error": f"{api_name} API error",
                "message": friendly,
                "stage": stage,
                "api_status": status,
                "error_message": error_message,
                "details": data,
            }

        dep = _parse_departure_time(departure_time)
        timeout_s = 12

        # ---------- 1) Distance Matrix ----------
        dm_url = "https://maps.googleapis.com/maps/api/distancematrix/json"
        dm_params: Dict[str, Any] = {
            "origins": origin,
            "destinations": destination,
            "mode": travel_mode,
            "key": api_key,
            "language": language,
        }
        if region:
            dm_params["region"] = region
        if dep is not None and travel_mode in ("driving", "transit"):
            dm_params["departure_time"] = dep

        _debug_print("Distance Matrix request params", _mask_key(dm_params))

        try:
            dm_resp = requests.get(dm_url, params=dm_params, timeout=timeout_s)
            if debug:
                print(f"[DEBUG] Distance Matrix HTTP status: {dm_resp.status_code}")
                print(f"[DEBUG] Distance Matrix URL: {_mask_url_key(dm_resp.url)}")
            dm_resp.raise_for_status()
            dm_data = dm_resp.json()
        except requests.RequestException as e:
            return json.dumps(
                {
                    "error": f"Distance Matrix request failed: {str(e)}",
                    "stage": "distance_matrix_request",
                },
                ensure_ascii=False,
                indent=2,
            )
        except ValueError as e:
            return json.dumps(
                {
                    "error": f"Distance Matrix returned invalid JSON: {str(e)}",
                    "stage": "distance_matrix_parse",
                },
                ensure_ascii=False,
                indent=2,
            )

        _debug_print("Distance Matrix raw response", dm_data)

        if dm_data.get("status") != "OK":
            return json.dumps(
                _api_error_payload("distance_matrix_status", "Distance Matrix", dm_data),
                ensure_ascii=False,
                indent=2,
            )

        elem = _safe_get(dm_data, ["rows", 0, "elements", 0], {})
        _debug_print("Distance Matrix first element", elem)

        if not elem:
            return json.dumps(
                {
                    "error": "Distance Matrix response missing rows[0].elements[0].",
                    "stage": "distance_matrix_shape",
                    "details": dm_data,
                },
                ensure_ascii=False,
                indent=2,
            )

        # Element-level status can be ZERO_RESULTS even when top-level status is OK.
        elem_status = elem.get("status")
        if elem_status not in ("OK", "ZERO_RESULTS"):
            return json.dumps(
                {
                    "error": "No route found (Distance Matrix).",
                    "message": f"Distance Matrix element returned unexpected status: {elem_status}",
                    "stage": "distance_matrix_element_status",
                    "element_status": elem_status,
                    "details": elem,
                },
                ensure_ascii=False,
                indent=2,
            )

        distance_text = _safe_get(elem, ["distance", "text"])
        distance_value_m = _safe_get(elem, ["distance", "value"])
        duration_text = _safe_get(elem, ["duration", "text"])
        duration_value_s = _safe_get(elem, ["duration", "value"])
        duration_in_traffic_text = _safe_get(elem, ["duration_in_traffic", "text"])
        duration_in_traffic_value_s = _safe_get(elem, ["duration_in_traffic", "value"])

        # ---------- 2) Directions ----------
        dir_url = "https://maps.googleapis.com/maps/api/directions/json"
        dir_params: Dict[str, Any] = {
            "origin": origin,
            "destination": destination,
            "mode": travel_mode,
            "key": api_key,
            "language": language,
            "alternatives": str(alternatives).lower(),
        }
        if region:
            dir_params["region"] = region
        if dep is not None and travel_mode in ("driving", "transit"):
            dir_params["departure_time"] = dep

        _debug_print("Directions request params", _mask_key(dir_params))

        try:
            dir_resp = requests.get(dir_url, params=dir_params, timeout=timeout_s)
            if debug:
                print(f"[DEBUG] Directions HTTP status: {dir_resp.status_code}")
                print(f"[DEBUG] Directions URL: {_mask_url_key(dir_resp.url)}")
            dir_resp.raise_for_status()
            dir_data = dir_resp.json()
        except requests.RequestException as e:
            return json.dumps(
                {
                    "error": f"Directions request failed: {str(e)}",
                    "stage": "directions_request",
                },
                ensure_ascii=False,
                indent=2,
            )
        except ValueError as e:
            return json.dumps(
                {
                    "error": f"Directions returned invalid JSON: {str(e)}",
                    "stage": "directions_parse",
                },
                ensure_ascii=False,
                indent=2,
            )

        _debug_print("Directions raw response", dir_data)

        dir_status = dir_data.get("status")
        if dir_status not in ("OK", "ZERO_RESULTS"):
            return json.dumps(
                _api_error_payload("directions_status", "Directions", dir_data),
                ensure_ascii=False,
                indent=2,
            )

        routes = dir_data.get("routes", [])
        if not routes or dir_status == "ZERO_RESULTS":
            return json.dumps(
                {
                    "origin": origin,
                    "destination": destination,
                    "mode": travel_mode,
                    "distance_matrix": {
                        "element_status": elem_status,
                        "distance": {"text": distance_text, "value_meters": distance_value_m},
                        "duration": {"text": duration_text, "value_seconds": duration_value_s},
                        "duration_in_traffic": {
                            "text": duration_in_traffic_text,
                            "value_seconds": duration_in_traffic_value_s,
                        },
                    },
                    "directions": {
                        "status": dir_status,
                        "routes_count": len(routes),
                    },
                    "note": "No detailed route steps available for this request/mode.",
                },
                ensure_ascii=False,
                indent=2,
            )

        # Pick the first route as "best"
        best = routes[0]
        leg = _safe_get(best, ["legs", 0], {}) or {}

        steps_out = []
        for st in leg.get("steps", []) or []:
            html_instruction = st.get("html_instructions")
            steps_out.append(
                {
                    "instruction_html": html_instruction,
                    "instruction_text": _html_to_text(html_instruction),
                    "distance": {
                        "text": _safe_get(st, ["distance", "text"]),
                        "value_meters": _safe_get(st, ["distance", "value"]),
                    },
                    "duration": {
                        "text": _safe_get(st, ["duration", "text"]),
                        "value_seconds": _safe_get(st, ["duration", "value"]),
                    },
                    "travel_mode": st.get("travel_mode"),
                    "maneuver": st.get("maneuver"),
                    "transit_details": st.get("transit_details"),  # transit-only
                }
            )

        result: Dict[str, Any] = {
            "origin": origin,
            "destination": destination,
            "mode": travel_mode,
            "distance_matrix": {
                "element_status": elem_status,
                "distance": {
                    "text": distance_text,
                    "value_meters": distance_value_m,
                },
                "duration": {
                    "text": duration_text,
                    "value_seconds": duration_value_s,
                },
                "duration_in_traffic": {
                    "text": duration_in_traffic_text,
                    "value_seconds": duration_in_traffic_value_s,
                },
            },
            "directions": {
                "status": dir_status,
                "summary": best.get("summary"),
                "start_address": leg.get("start_address"),
                "end_address": leg.get("end_address"),
                "leg_distance": {
                    "text": _safe_get(leg, ["distance", "text"]),
                    "value_meters": _safe_get(leg, ["distance", "value"]),
                },
                "leg_duration": {
                    "text": _safe_get(leg, ["duration", "text"]),
                    "value_seconds": _safe_get(leg, ["duration", "value"]),
                },
                "leg_duration_in_traffic": {
                    "text": _safe_get(leg, ["duration_in_traffic", "text"]),
                    "value_seconds": _safe_get(leg, ["duration_in_traffic", "value"]),
                },
                "overview_polyline": _safe_get(best, ["overview_polyline", "points"]),
                "steps": steps_out,
            },
        }

        if debug:
            result["_debug"] = {
                "distance_matrix_status": dm_data.get("status"),
                "directions_status": dir_status,
                "departure_time_input": departure_time,
                "departure_time_parsed": dep,
                "distance_matrix_rows_count": len(dm_data.get("rows", [])) if isinstance(dm_data.get("rows"), list) else None,
                "directions_routes_count": len(routes),
            }

        return json.dumps(result, ensure_ascii=False, indent=2)

# ##################################################
# #################Test Code Below##################
# ##################################################
# if __name__ == "__main__":
#    from dotenv import load_dotenv
#    load_dotenv()
#    tool = RoutePlannerTool()

#    print(
#        tool.run(
#            origin="Shibuya Station, Tokyo",
#            destination="Senso-ji, Tokyo",
#            travel_mode="driving",
#            departure_time="now",
#            debug=False,  # enable debug prints
#        )
#    )