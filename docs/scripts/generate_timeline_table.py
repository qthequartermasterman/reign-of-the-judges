import docs.scripts.model as model
import pathlib
import json

EVENTS_DIR = pathlib.Path("docs/events")


def event_to_markdown(event: model.Event) -> str:
    """Convert an event to a markdown table row.

    Args:
        event: An event object.

    Returns:
        A markdown table row.
    """
    return f"| {event.date} | {event.end_date or ''} | {event.name} | {event.location or ''} | {', '.join(str(s) for s in event.sources)} | {event.description} |"


def events_to_markdown(events: list[model.Event]) -> str:
    """Convert a list of events to a markdown table.

    Args:
        events: A list of event objects.

    Returns:
        A markdown table.
    """
    text = """\
| Date | End Date | Title | Location| Sources | Description |
| --- | --- | --- | --- | --- | --- |
"""
    return text + "\n".join([event_to_markdown(event) for event in events])


def extract_events_from_files(events_dir: pathlib.Path) -> list[model.Event]:
    """Extract events from json files in a directory.

    Args:
        events_dir: A directory containing json files.

    Returns:
        A list of event objects.
    """
    json_files = events_dir.glob("**/*.json")
    events: list[model.Event] = []
    for i, json_file in enumerate(json_files):
        print(str(json_file))
        raw_json = json_file.read_text()
        parsed_json = json.loads(raw_json)
        event = model.Event(**parsed_json)
        events.append(event)
    return sorted(events)


markdown_table = events_to_markdown(extract_events_from_files(EVENTS_DIR))
