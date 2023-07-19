from __future__ import print_function

import logging
import re
import time
from typing import Dict

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.errors import HttpError

SCOPES = ['https://www.googleapis.com/auth/spreadsheets']
SERVICE_ACCOUNT_FILE = "/Users/mirco/CODICE/egopapers/sage-artifact-148817-0722216499fe.json"
SAMPLE_SPREADSHEET_ID = '1_z0775nzf1LNjSHp_cw-XbxyVSmbIarbjPRBPhHwjEQ'
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=SCOPES)
service = build('sheets', 'v4', credentials=credentials)
sheet = service.spreadsheets()



def update_values(creds, spreadsheet_id, range_name, value_input_option,
                  _values):
    # pylint: disable=maybe-no-member
    try:

        service = build('sheets', 'v4', credentials=creds)
        values = [
            [
                _values  # Cell values ...
            ],
            # Additional rows ...
        ]
        body = {
            'values': values
        }
        result = service.spreadsheets().values().update(
            spreadsheetId=spreadsheet_id, range=range_name,
            valueInputOption=value_input_option, body=body).execute()
        print(f"{result.get('updatedCells')} cells updated.")
        return result
    except HttpError as error:
        print(f"An error occurred: {error}")
        return error

def parser_paper(line: str,
                 category: str = None,
                 section: str = None,
                 subsection: str = None):
    # Extract title and link
    title_paper = re.findall(r"(.*?)\]", line)
    line_update = line[len(title_paper):]
    link_paper = re.findall(r"\]\((.*?)\)", line_update) # todo check could be more then one
    line_update = line_update[len(link_paper):]
    logging.warning(title_paper)
    # Extract authors and conference
    authors_conference_year = re.findall(r"- .*?\d{4}\.", line_update)[0][1:-1]
    conference_year = authors_conference_year.split(",")[-1]

    year = conference_year.split(" ")[-1]
    conference = conference_year[:-len(year)]

    authors = authors_conference_year[:-len(conference_year) - 1]

    # Others link
    link_code = re.findall(r"code\]\]\((.*?)\)", line_update, re.DOTALL)
    link_project_page = re.findall(r"preject page\]\]\((.*?)\)", line_update, re.DOTALL)
    link_demo = re.findall(r"demo\]\]\((.*?)\)", line_update, re.DOTALL)
    link_presentation_video = re.findall(r"resentation video\]\]\((.*?)\)", line_update, re.DOTALL)
    link_video = re.findall(r"video\]\]\((.*?)\)", line_update, re.DOTALL)

    link_code = link_code if len(link_code) == 0 else link_code[0]
    link_project_page = link_project_page  if len(link_project_page) == 0 else link_project_page[0]
    link_demo = link_demo  if len(link_demo) == 0 else link_demo[0]
    link_presentation_video = link_presentation_video  if len(link_presentation_video) == 0 else link_presentation_video[0]
    link_video = link_video  if len(link_video) == 0 else link_video[0]

    # Return the extracted information as a dictionary
    return {
        "category": category,
        "section": section,
        "subsection": subsection,
        "title": title_paper[0],
        "link_paper": link_paper[0],
        "authors": authors,
        "conference": conference,
        "year": int(year),
        "link_demo": link_demo,
        "link_code": link_code,
        "link_project_page": link_project_page,
        "link_presentation_video": link_presentation_video,
        "link_video": link_video,
    }

def parser_paper_dataset(line: str,
                 category: str = None,
                 section: str = None,
                 subsection: str = None):
    # Extract title and link
    title_dataset = re.findall(r"(.*?)\]", line)[0]
    line_update = line[len(title_dataset):]
# - [UEC Dataset](http://www.cs.cmu.edu/~kkitani/datasets/) - Two choreographed datasets with different egoactions (walk, jump, climb, etc.) + 6 YouTube sports videos.
# - [Assembly101](https://assembly101.github.io/) - Procedural activity dataset featuring 4321 videos of people assembling and disassembling 101 “take-apart” toy vehicles. [[paper]](https://arxiv.org/pdf/2203.14712.pdf) CVPR 2022.

    link_dataset = re.findall(r"\]\((.*?)\)", line_update)[0] # todo check could be more then one
    line_update = line_update[len(link_dataset)+3:]

    logging.warning(title_dataset)
    if "[[paper]]" in line_update:
        dataset_description = re.findall(r"- (.*?) \[\[paper\]\]", line_update)[0]
        paper_link = re.findall(r"\[\[paper\]\]\((.*?)\)", line_update)[0]
        line_update = line_update[len(dataset_description)+3:]
        line_update = line_update[len(paper_link)+12:]
        conference = line_update.strip()[:-1]

        year = conference.split(" ")[-1]
        conference = conference[:-len(year)]


    else:
        dataset_description = line_update[2:]
        paper_link = ""
        conference = ""

    # Return the extracted information as a dictionary
    return {
        "category": category,
        "section": section,
        "subsection": subsection,
        "title": title_dataset,
        "link_paper": paper_link,
        "conference": conference,
        "year": int(year),
        "link_project_page": link_dataset,
        "dataset_description": dataset_description,
    }


def write_paper_on_google_sheet(
        credentials,
        SAMPLE_SPREADSHEET_ID: str,
        paper_info: Dict,
        number_lines: int,
) -> None:
    location = "Foglio1!" + "C" + str(number_lines)
    values = paper_info["title"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)

    location = "Foglio1!" + "D" + str(number_lines)
    values = paper_info["authors"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)

    location = "Foglio1!" + "E" + str(number_lines)
    values = paper_info["conference"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)

    location = "Foglio1!" + "F" + str(number_lines)
    values = paper_info["year"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)

    location = "Foglio1!" + "G" + str(number_lines)
    values = paper_info["category"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)

    location = "Foglio1!" + "H" + str(number_lines)
    values = paper_info["section"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)

    location = "Foglio1!" + "I" + str(number_lines)
    values = paper_info["subsection"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)

    location = "Foglio1!" + "J" + str(number_lines)
    values = paper_info["link_paper"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)

    location = "Foglio1!" + "K" + str(number_lines)
    values = paper_info["link_project_page"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)

    location = "Foglio1!" + "L" + str(number_lines)
    values = paper_info["link_code"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)

    location = "Foglio1!" + "L" + str(number_lines)
    values = paper_info["link_video"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)

def write_paper_datasets_on_google_sheet(
        credentials,
        SAMPLE_SPREADSHEET_ID: str,
        paper_info: Dict,
        number_lines: int,
) -> None:
    location = "Foglio1!" + "C" + str(number_lines)
    values = paper_info["title"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)

    location = "Foglio1!" + "E" + str(number_lines)
    values = paper_info["conference"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)

    location = "Foglio1!" + "F" + str(number_lines)
    values = paper_info["year"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)

    location = "Foglio1!" + "G" + str(number_lines)
    values = paper_info["category"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)

    location = "Foglio1!" + "H" + str(number_lines)
    values = paper_info["section"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)

    location = "Foglio1!" + "I" + str(number_lines)
    values = paper_info["subsection"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)

    location = "Foglio1!" + "J" + str(number_lines)
    values = paper_info["link_paper"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)

    location = "Foglio1!" + "K" + str(number_lines)
    values = paper_info["link_project_page"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)

    location = "Foglio1!" + "N" + str(number_lines)
    values = paper_info["dataset_description"]
    update_values(credentials, SAMPLE_SPREADSHEET_ID, location, 'RAW', values)


# Read the file
with open("/Users/mirco/CODICE/egopapers/egocentric_vision_readme_data.md", "r") as file:
    content = file.read()


categories = ["Surveys", "Papers", "Challenges", "Devices"]


# Find all the sections and their starting positions
all_sections = re.findall(r"##\s(.+)", content)
sections_subsections = re.findall(r"### (.+)", content)
subsections = re.findall(r"#### (.+)", content)

sections = [section for section in sections_subsections if section not in subsections]
section_positions = [match.start() for match in re.finditer(r"##\s", content)]

# Iterate over the sections and extract the titles and URLs
parsed_data = {}

number_lines = 2
section = None
subsection = None
for i in range(len(all_sections)):
    general_section = all_sections[i]
    if general_section in categories:
        category = general_section

    if general_section in sections:
        section = general_section
        subsection = ""

    if general_section in subsections:
        subsection = general_section

    section_start = section_positions[i]
    section_end = section_positions[i + 1] if i + 1 < len(section_positions) else len(content)
    section_content = content[section_start:section_end]

    #if general_section == "Datasets" or general_section == "Challenges" or general_section == "Devices":
    #    continue
    if general_section == "Papers" and False:
        papers = re.findall(r"- \[(.*?)\n", section_content, re.DOTALL)
        for paper in papers:
            #import pdb; pdb.set_trace()
            paper_info = parser_paper(paper, category = category, section=section, subsection=subsection)
            write_paper_on_google_sheet(
                credentials=credentials,
                SAMPLE_SPREADSHEET_ID=SAMPLE_SPREADSHEET_ID,
                paper_info=paper_info,
                number_lines=number_lines)
            number_lines = number_lines + 1

    number_lines = 220
    if general_section == "Datasets":
        section = general_section
        papers_dataset = re.findall(r"- \[(.*?)\n", section_content, re.DOTALL)
        for paper_dataset in papers_dataset:
            paper_dataset_info = parser_paper_dataset(paper_dataset, category = "Papers", section="Datasets", subsection="")
            write_paper_datasets_on_google_sheet(
                credentials=credentials,
                SAMPLE_SPREADSHEET_ID=SAMPLE_SPREADSHEET_ID,
                paper_info=paper_dataset_info,
                number_lines=number_lines)
            number_lines = number_lines + 1
            if number_lines % 5 == 0:
                time.sleep(2)

