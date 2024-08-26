# generated by datamodel-codegen:
#   filename:  event.json
#   timestamp: 2024-08-04T18:22:02+00:00

from __future__ import annotations

from enum import Enum
from typing import Any, List, Optional
from uuid import UUID

from pydantic import BaseModel, Field, model_validator
import magentic


class Location(BaseModel):
    # model_config = magentic.ConfigDict(openai_strict=True)
    
    name: str = Field(None, description='The name of the location.', examples=["City of Zarahemla", "City of Gideon", "City of Mulek", "Land of Nephi", "Land of Jershon", "Waters of Mormon"])
    description: str | None = Field(
        None, description='A description of the location.', examples=["South of the land of Shilom", "North of the land of Zarahemla", "East of the land of Zarahemla", "West of the land of Zarahemla"]
    )


class RelativeEvents(BaseModel):
    # model_config = magentic.ConfigDict(openai_strict=True)
    
    before: list[str] | None = Field(
        None, description='Events that this event is definitely before.'
    )
    after: list[str] | None = Field(
        None, description='Events that this event is definitely after.'
    )


class CalendarSystem(Enum):
    """The calendar system of the date. Mormon uses three different calendar systems to describe dates during the reign of the judges. Care should be taken to use the correct calendar system when describing dates."""
    
    # model_config = magentic.ConfigDict(openai_strict=True)
    
    reign_of_the_judges = 'reign-of-the-judges'
    """Year 1 is the establishment of the reign of the judges. Primarily used in the Book of Alma and the Book of Helaman."""
    after_christ = 'after-christ'
    """Year 1 is the year that the Nephites see the sign of Christ's birth. Primarily used in 3 Nephi."""
    after_lehi = 'after-lehi'
    """Year 1 is the year that Lehi left Jerusalem. Year 600 corresponds to Christ's birth. Only occasionally used during the Books of Alma, Helaman, or 3 Nephi."""


class Date(BaseModel):
    # model_config = magentic.ConfigDict(openai_strict=True)
    
    year: int | None = Field(None, description='The year of the event.')
    month: int | None = Field(None, description='The month of the event.')
    day: int | None = Field(None, description='The day of the event.')
    calendar_system: CalendarSystem | None = Field(
        None, description='The calendar system of the date.', examples=[CalendarSystem.reign_of_the_judges, CalendarSystem.after_christ, CalendarSystem.after_lehi]
    )
    miscellaneous: str | None = Field(
        None, description='Any additional information about the date', examples=["In the commencement", "In the end", "as the year ended", "the spring", "the summer", "the fall", "the winter"]
    )


class Event(BaseModel):
    """An event that occurred in the Book of Mormon."""
    # model_config = magentic.ConfigDict(openai_strict=True)
    
    name: str = Field(None, description='The name of the event.')
    description: str = Field(None, description='A description of the event.')
    sources: list[str] = Field(
        None, description='The sources that describe the event.', examples=[["Alma 56:1-57:36"], ["Helaman 1:1-2:14"], ["3 Nephi 1:1-2:10"], ["Alma 1:1-2:14", "Alma 3:1-4:14"]]
    )
    date: Date = Field(
        None,
        description="The date of the event, if it occurred at a single, specific time, or the date of the event's beginning, if it was a period of time.", examples=[Date(year=1, month=1, day=1, calendar_system=CalendarSystem.reign_of_the_judges)]
    )
    end_date: Date | None = Field(
        None, description="The date of the event's end, if it was a period of time.", examples=[Date(year=1, month=1, day=5, calendar_system=CalendarSystem.reign_of_the_judges)]
    )
    location: Location | None = Field(None, description='The location of the event.', examples=[Location(name="City of Zarahemla", description="South of the land of Shilom"), Location(name="City of Gideon"), Location(name="Land of Nephi")])
    participants: list[str] | None = Field(
        None, description='The participants in the event.', examples=[["Amalickiah", "Moroni"], ["Teancum"], ["Lehi"], ["Nephi", "Alma", "Helaman"], ["Samuel the Lamanite", "The People of Zarahemla"]]
    )
    relative_events: RelativeEvents | None = Field(
        None, description='Events that this event is definitely after or before.', examples=[RelativeEvents(before=["The death of Amalickiah"], after=["The death of Moroni"])]
    )

    @model_validator(mode='after')
    def third_nephi_year(self):
        """The language model isn't always great at inferring the calendar system from the text. Some simple heuristics can help in 3rd Nephi."""
        if not any("3 Nephi" in source for source in self.sources):
            return self

        if self.date.calendar_system == CalendarSystem.reign_of_the_judges and self.date.year < 40:
            self.date.calendar_system = CalendarSystem.after_christ
        elif self.date.calendar_system == CalendarSystem.after_christ and self.date.year >= 40:
            self.date.calendar_system = CalendarSystem.reign_of_the_judges

        if self.end_date and self.end_date.calendar_system == CalendarSystem.reign_of_the_judges and self.end_date.year < 40:
            self.end_date.calendar_system = CalendarSystem.after_christ
        elif self.end_date and self.end_date.calendar_system == CalendarSystem.after_christ and self.end_date.year >= 40:
            self.end_date.calendar_system = CalendarSystem.reign_of_the_judges

        return self

        