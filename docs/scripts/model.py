# generated by datamodel-codegen:
#   filename:  event.json
#   timestamp: 2024-08-04T18:22:02+00:00

from __future__ import annotations

from enum import Enum
import pydantic

from pydantic import BaseModel, Field, model_validator
import functools
import re

SCRIPTUREVERSE_REGEX = re.compile(
    r"(\d*\s*[a-zA-Z\s]+)\s*(\d+)(?::(\d+))?(\s*-\s*(\d+)(?:\s*([a-z]+)\s*(\d+))?(?::(\d+))?)?"
)
BOOK_OF_MORMON_BOOK_INDICES = {
    "1 Nephi": 1,
    "2 Nephi": 2,
    "Jacob": 3,
    "Enos": 4,
    "Jarom": 5,
    "Omni": 6,
    "Words of Mormon": 7,
    "Mosiah": 8,
    "Alma": 9,
    "Helaman": 10,
    "3 Nephi": 11,
    "4 Nephi": 12,
    "Mormon": 13,
    "Ether": 14,
    "Moroni": 15,
}

END_OF_YEAR_WORDS = ["end", "ended", "endeth", "concluded", "conclusion", "concludeth"]
BEGINNING_OF_YEAR_WORDS = ["begin", "began", "beginning", "beginneth", "commenced", "commences", "commenceth", "commencement", "start"]

class Location(BaseModel):
    # model_config = magentic.ConfigDict(openai_strict=True)

    name: str = Field(
        description="The name of the location.",
        examples=[
            "City of Zarahemla",
            "City of Gideon",
            "City of Mulek",
            "Land of Nephi",
            "Land of Jershon",
            "Waters of Mormon",
        ],
    )
    description: str | None = Field(
        None,
        description="A description of the location.",
        examples=[
            "South of the land of Shilom",
            "North of the land of Zarahemla",
            "East of the land of Zarahemla",
            "West of the land of Zarahemla",
        ],
    )

    def __str__(self) -> str:
        return self.name + (f" ({self.description})" if self.description else "")


class RelativeEvents(BaseModel):
    # model_config = magentic.ConfigDict(openai_strict=True)

    before: list[str | dict[str, str]] | None = Field(
        None, description="Events that this event is definitely before."
    )
    after: list[str | dict[str, str]] | None = Field(
        None, description="Events that this event is definitely after."
    )


class CalendarSystem(Enum):
    """The calendar system of the date. Mormon uses three different calendar systems to describe dates during the reign of the judges. Care should be taken to use the correct calendar system when describing dates."""

    # model_config = magentic.ConfigDict(openai_strict=True)

    reign_of_the_judges = "reign-of-the-judges"
    """Year 1 is the establishment of the reign of the judges. Primarily used in the Book of Alma and the Book of Helaman."""
    after_christ = "after-christ"
    """Year 1 is the year that the Nephites see the sign of Christ's birth. Primarily used in 3 Nephi."""
    after_lehi = "after-lehi"
    """Year 1 is the year that Lehi left Jerusalem. Year 600 corresponds to Christ's birth. Only occasionally used during the Books of Alma, Helaman, or 3 Nephi."""


@functools.total_ordering
class Date(BaseModel):
    # model_config = magentic.ConfigDict(openai_strict=True)
    model_config = pydantic.ConfigDict(frozen=True)

    year: int | None = Field(None, description="The year of the event.")
    month: int | None = Field(None, description="The month of the event.")
    day: int | None = Field(None, description="The day of the event.")
    calendar_system: CalendarSystem | None = Field(
        None,
        description="The calendar system of the date.",
        examples=[
            CalendarSystem.reign_of_the_judges,
            CalendarSystem.after_christ,
            CalendarSystem.after_lehi,
        ],
    )
    miscellaneous: str | None = Field(
        None,
        description="Any additional information about the date",
        examples=[
            "In the commencement",
            "In the end",
            "as the year ended",
            "the spring",
            "the summer",
            "the fall",
            "the winter",
        ],
    )

    @property
    def year_after_reign_of_the_judges(self) -> int:
        if self.calendar_system == CalendarSystem.reign_of_the_judges:
            return self.year
        if self.calendar_system == CalendarSystem.after_christ:
            return self.year + 91
        if self.calendar_system == CalendarSystem.after_lehi:
            return self.year - 600

    def __str__(self) -> str:
        text = f"Year {self.year_after_reign_of_the_judges}"
        if self.month is not None:
            text += f" Month {self.month}"
        if self.day is not None:
            text += f" Day {self.day}"
        if self.calendar_system == CalendarSystem.after_christ:
            text += f" (Year {self.year} After Christ)"
        elif self.calendar_system == CalendarSystem.after_lehi:
            text += f" (Year {self.year} After Lehi)"
        return text

    def __eq__(self, value):
        return (
            self.year == value.year
            and self.month == value.month
            and self.day == value.day
            and self.calendar_system == value.calendar_system
        )

    def __hash__(self):
        return hash((self.year, self.month, self.day, self.calendar_system))

    @pydantic.field_validator("calendar_system")
    @classmethod
    def infer_calendar_system(
        cls, calendar_system: CalendarSystem | None
    ) -> CalendarSystem:
        if calendar_system is not None:
            return calendar_system
        return CalendarSystem.reign_of_the_judges

    def __lt__(self, other: Date | None) -> bool:
        if other is None:
            return False
        if not isinstance(other, Date):
            return NotImplemented
        
        
        return (
            self.year_after_reign_of_the_judges or -1,
            self.effective_month,
            self.day or -1,
        ) < (
            other.year_after_reign_of_the_judges or -1,
            other.effective_month,
            other.day or -1,
        )

    @property
    def effective_month(self) -> int:
        if self.month is None and self.miscellaneous:
            if any(word in self.miscellaneous for word in BEGINNING_OF_YEAR_WORDS):
                return -1
            elif any(word in self.miscellaneous for word in END_OF_YEAR_WORDS):
                return 12
            else:
                return 0
        return self.month

@functools.total_ordering
class ScriptureReference(pydantic.BaseModel):
    book: str = Field(
        None,
        description="The name of the book of scripture.",
        examples=["Alma", "3 Nephi", "Helaman", "Ether", "Moroni"],
    )
    start_chapter: int = Field(
        None,
        description="The chapter of the first verse of the reference.",
        examples=[1, 2, 3, 4, 5],
    )
    start_verse: int | None = Field(
        None,
        description="The verse of the first verse of the reference.",
        examples=[1, 2, 3, 4, 5],
    )
    end_chapter: int | None = Field(
        None,
        description="The chapter of the last verse of the reference.",
        examples=[1, 2, 3, 4, 5],
    )
    end_verse: int | None = Field(
        None,
        description="The verse of the last verse of the reference.",
        examples=[1, 2, 3, 4, 5],
    )

    def __lt__(self, other: ScriptureReference):
        if not isinstance(other, ScriptureReference):
            return NotImplemented
        return (
            BOOK_OF_MORMON_BOOK_INDICES[self.book],
            self.start_chapter,
            self.start_verse or tuple(sorted(self.sources)),
        ) < (
            BOOK_OF_MORMON_BOOK_INDICES[other.book],
            other.start_chapter,
            other.start_verse or tuple(sorted(self.sources)),
        )

    def __eq__(self, value):
        return (
            self.book == value.book
            and self.start_chapter == value.start_chapter
            and self.start_verse == value.start_verse
            and self.end_chapter == value.end_chapter
            and self.end_verse == value.end_verse
        )

    def __hash__(self):
        return hash(
            (
                self.book,
                self.start_chapter,
                self.start_verse,
                self.end_chapter,
                self.end_verse,
            )
        )

    @pydantic.field_validator("book")
    @classmethod
    def strip_whitespace(cls, value: str) -> str:
        return value.strip()

    def __str__(self) -> str:
        string = f"{self.book} {self.start_chapter}"
        if self.start_verse is not None:
            string += f":{self.start_verse}"
        if self.end_chapter is not None:
            string += f"-{self.end_chapter}"
        if self.end_chapter is not None and self.end_verse is not None:
            string += ":"
        if self.end_verse is not None:
            string += f"{self.end_verse}"
        return string


class Event(BaseModel):
    """An event that occurred in the Book of Mormon."""

    # model_config = magentic.ConfigDict(openai_strict=True)

    name: str = Field(description="The name of the event.")
    description: str = Field(description="A description of the event.")
    sources: list[ScriptureReference] = Field(
        default_factory=list,
        description="The sources that describe the event.",
        examples=[
            ["Alma 56:1-57:36"],
            ["Helaman 1:1-2:14"],
            ["3 Nephi 1:1-2:10"],
            ["Alma 1:1-2:14", "Alma 3:1-4:14"],
        ],
    )
    date: Date | None = Field(
        None,
        description="The date of the event, if it occurred at a single, specific time, or the date of the event's beginning, if it was a period of time.",
        examples=[
            Date(
                year=1,
                month=1,
                day=1,
                calendar_system=CalendarSystem.reign_of_the_judges,
            )
        ],
    )
    end_date: Date | None = Field(
        None,
        description="The date of the event's end, if it was a period of time.",
        examples=[
            Date(
                year=1,
                month=1,
                day=5,
                calendar_system=CalendarSystem.reign_of_the_judges,
            )
        ],
    )
    location: Location | None = Field(
        None,
        description="The location of the event.",
        examples=[
            Location(
                name="City of Zarahemla", description="South of the land of Shilom"
            ),
            Location(name="City of Gideon"),
            Location(name="Land of Nephi"),
        ],
    )
    participants: list[str] | None = Field(
        None,
        description="The participants in the event.",
        examples=[
            ["Amalickiah", "Moroni"],
            ["Teancum"],
            ["Lehi"],
            ["Nephi", "Alma", "Helaman"],
            ["Samuel the Lamanite", "The People of Zarahemla"],
        ],
    )
    relative_events: RelativeEvents | None = Field(
        None,
        description="Events that this event is definitely after or before.",
        examples=[
            RelativeEvents(
                before=["The death of Amalickiah"], after=["The death of Moroni"]
            )
        ],
    )

    @pydantic.field_validator("sources", mode="before")
    @classmethod
    def validate_sources(
        cls, sources: list[str | ScriptureReference]
    ) -> list[ScriptureReference]:
        return [cls.validate_source(source) for source in sources]

    @staticmethod
    def validate_source(source: str | ScriptureReference) -> ScriptureReference:
        if isinstance(source, ScriptureReference):
            return source
        match = SCRIPTUREVERSE_REGEX.match(source)
        if match is None:
            raise ValueError(f"Invalid scripture reference: {source}")
        book = match.group(1)
        start_chapter = int(match.group(2))
        start_verse = int(match.group(3)) if match.group(3) else None
        end_chapter = int(match.group(5)) if match.group(5) else None
        end_verse = int(match.group(8)) if match.group(8) else None
        return ScriptureReference(
            book=book,
            start_chapter=start_chapter,
            start_verse=start_verse,
            end_chapter=end_chapter,
            end_verse=end_verse,
        )

    @model_validator(mode="after")
    def third_nephi_year(self):
        """The language model isn't always great at inferring the calendar system from the text. Some simple heuristics can help in 3rd Nephi."""
        if self.date is None:
            return self

        if not any("3 Nephi" in source.book for source in self.sources):
            return self

        if (
            self.date.calendar_system == CalendarSystem.reign_of_the_judges
            or self.date.calendar_system is None
        ) and self.date.year < 40:
            self.date.calendar_system = CalendarSystem.after_christ
        elif (
            self.date.calendar_system == CalendarSystem.after_christ
            or self.date.calendar_system is None
        ) and self.date.year >= 40:
            self.date.calendar_system = CalendarSystem.reign_of_the_judges

        if (
            self.end_date
            and (
                self.end_date.calendar_system == CalendarSystem.reign_of_the_judges
                or self.end_date.calendar_system is None
            )
            and self.end_date.year < 40
        ):
            self.end_date.calendar_system = CalendarSystem.after_christ
        elif (
            self.end_date
            and (
                self.end_date.calendar_system == CalendarSystem.after_christ
                or self.end_date.calendar_system is None
            )
            and self.end_date.year >= 40
        ):
            self.end_date.calendar_system = CalendarSystem.reign_of_the_judges

        return self

    def __lt__(self, other: Event) -> bool:
        if not isinstance(other, Event):
            return NotImplemented

        return (self.date or Date(year=-1), tuple(sorted(self.sources))) < (
            other.date or Date(year=-1),
            tuple(sorted(other.sources)),
        )

        # if self.date is not None and other.date is not None:
        #     date_lt = self.date < other.date
        #     if date_lt:
        #         return True
        # # TODO: respect relative events
        # return sorted(self.sources)[0] < sorted(other.sources)[0]


RelativeEvents.model_rebuild()
