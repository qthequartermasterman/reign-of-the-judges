import magentic
import pyscripture.download
import pydantic
import pathlib

import docs.scripts.model as model
import tqdm



DF = pyscripture.download.get_dataframe()['Text']['Book of Mormon']

CONTRAINTS = """\
Follow the structured format exactly. 

When describing dates, you should use the year relative to the beginning of the Reign of the Judges. Do not include any
events that are not from the Reign of the Judges, and do not use the Gregorian calendar. If the scripture is in the
Book of Alma or the Book of Helaman, then the event is probably using calendar system `reign-of-the-judges`. If the 
scripture is in 3 Nephi, you will have to infer from the text if the date is `reign-of-the-judges` or `after-christ`. 

You should include the scripture reference for each event with the exact chapter and verse numbers provided. 

Make sure to include any relevant details in the description of the event. 

You should also make sure to include any Locations, if mentioned in the text.

Make sure to include any participants in the event using their names.

Ensure you link to any other related events by their ID.

Do not include any events that are not explicitly mentioned in the text.
"""

SYSTEM_MESSAGE = f"""\
You are an expert Scriptorian and Historian with a perfect knowledge of Book of Mormon and Old Testament events. You 
are excitedly responding to a call to help extract and compile events from the Reign of the Judges. You are given a
set of scriptures, and you should extract the events into a structured format described below. 

{CONTRAINTS}
"""

REFINE_SYSTEM_MESSAGE = f"""\
You are an expert Scriptorian and Historian with a perfect knowledge of Book of Mormon and Old Testament events. You are 
excitedly responding to a call to help refine and compile events from the Reign of the Judges. You are given an intern's
first pass at extracting events from a set of scriptures, and you should refine the events into a structured format described below.

{CONTRAINTS}
"""

@magentic.chatprompt(
    magentic.SystemMessage(SYSTEM_MESSAGE),
    magentic.UserMessage("These are the scriptures whose events you should extract: {scriptures}"),
    model=magentic.OpenaiChatModel("gpt-4o-mini")
)
def extract_events(scriptures: str) -> list[model.Event]:
    ...


def get_verses_from_reference(book: str, chapter:int, string_reference: str) -> str:
    verses = DF.loc[book, chapter]
    string_reference = string_reference.rsplit(":")[-1]
    if "-" in string_reference:
        start, end = string_reference.split("-")
        return '\n'.join([f"{idx}. {verse}" for idx, verse in verses.loc[int(start):int(end)].items()])
    else:
        return f"{string_reference}. {verses.loc[int(string_reference)]}"
    
    


@magentic.chatprompt(
    magentic.SystemMessage(REFINE_SYSTEM_MESSAGE),
    magentic.UserMessage("This is the event extracted by the intern: {event}"),
    magentic.UserMessage("These are the scriptures whose events you should refine: {scriptures}"),
    model=magentic.OpenaiChatModel("gpt-4o-mini")
)
def refine_event(event: model.Event, scriptures: model) -> model.Event:
    ...

def extract_events_from_reference(book: str, chapter:int) -> list[model.Event]:
    verses = DF.loc[book, chapter]
    text = f"The Book of {book}\nChapter {chapter}\n========\n" + '\n'.join(f"{idx}. {verse}" for idx, verse in verses.items())
    assert all(str(i) in text for i in range(1, len(verses)+1)), f"Verse number not found in text: {verses}"
    raw_events = extract_events(text)
    refined_events = []
    for event in raw_events:
        try:
            verses_text = "\n".join([get_verses_from_reference(book, chapter, source) for source in event.sources])
            refined_event = refine_event(event, verses_text)
            refined_events.append(refined_event)
        except Exception as e:
            print(f"Error refining event: {event.name}")
            print(e)
            refined_events.append(event)
    
    return refined_events


if __name__ == '__main__':
    BOOK = '3 Nephi'
    CHAPTER = 10

    dir_path = pathlib.Path("docs/events")/BOOK.replace(' ','-').lower()/f"{CHAPTER}-auto-generated/"

    dir_path.mkdir(parents=True, exist_ok=True)
    
    events = extract_events_from_reference(BOOK, CHAPTER)
    for event in tqdm.tqdm(events):
        file_name = event.name.lower().replace(' ', '-').replace('\n', '-')
        file = dir_path/f"{file_name}.json"
        file.write_text(event.model_dump_json(indent=2))