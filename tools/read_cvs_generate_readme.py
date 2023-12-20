import logging
import math
from collections import OrderedDict

import pandas as pd


def add_git_command(df: pd.DataFrame):
    df_tmp = df.__deepcopy__()
    for index, values in enumerate(df_tmp.values):
        git_command = ""
        title = values[2]
        authors_list = values[3]
        conference = values[4]
        year = values[5]
        category = values[6]
        section = values[7]
        subsection = values[8]

        short_description = values[9]

        link_paper = values[10]
        link_page = values[11]
        link_code = values[12]
        link_video = values[13]

        note = values[14]

        if (category == "Papers" or category == "Surveys") and section != "Datasets":
            git_command += "- [" + title + "]"
            git_command += "(" + link_paper + ")"
            authors_list = authors_list if authors_list[0] != " " else authors_list[1:]
            git_command += " - " + authors_list + ", "
            if not isinstance(conference, float):
                git_command += conference.strip()
            if not math.isnan(year):
                git_command += " " + str(int(year)) + "."

            if not isinstance(link_code, float):
                git_command += " [[code]](" + link_code + ")"

            if not isinstance(link_page, float):
                git_command += " [[project page]](" + link_page + ")"

            if not isinstance(link_video, float):
                git_command += " [[video]](" + link_video + ")"


        elif section == "Datasets":
            git_command += "- [" + title + "]"
            if not isinstance(link_page, float):
                git_command += "(" + link_page + ")"
            short_description = short_description if short_description[-1] != "." else short_description[:-1]
            git_command += " - " + short_description + ". "

            if not isinstance(conference, float):
                git_command += conference.strip()
            if not math.isnan(year):
                git_command += " " + str(int(year)) + "."

            if not isinstance(link_paper, float):
                git_command += " [[paper]](" + link_paper + ")"


        elif category == "Challenges":
            git_command += "- [" + title + "]"
            if not isinstance(link_page, float):
                git_command += "(" + link_page + ")"
            short_description = short_description if short_description[-1] != "." else short_description[:-1]
            git_command += "- " + short_description + "."

        elif category == "Devices":
            git_command += "- [" + title + "]"
            if not isinstance(link_page, float):
                git_command += "(" + link_page + ")"





        df_tmp.at[index, "Git Command"] = git_command

    return df_tmp


def strip_dataframe(df):
    return df.applymap(lambda x: x.strip() if isinstance(x, str) else x)


class Egoindex:
    # category

    init_readme = ""
    body = ""
    final = "This is a work in progress... "

    surveys = []
    papers = OrderedDict()
    challenges = []
    devices = []

    # sections
    papers["Action / Activity Recognition"] = OrderedDict()
    papers["Action Anticipation"] = OrderedDict()
    papers["Multi-Modalities"] = OrderedDict()
    papers["Temporal Segmentation (Action Detection)"] = []
    papers["Retrieval"] = []
    papers["Segmentation"] = []
    papers["Video-Language"] = []
    papers["Few-Shot Action Recognition"] = []
    papers["Gaze"] = []
    papers["From Third-Person to First-Person"] = []
    papers["NeRF"] = []
    papers["User Data from an Egocentric Point of View"] = []
    papers["Localization"] = []
    papers["Privacy protection"] = []
    papers["Tracking"] = []
    papers["Social Interactions"] = []
    papers["Multiple Egocentric Tasks"] = []
    papers["Activity-context"] = []
    papers["Video summarization"] = []
    papers["Applications"] = []
    papers["Human to Robot"] = []
    papers["Asssitive Egocentric Vision"] = []
    papers["Popular Architectures"] = OrderedDict()
    papers["Other EGO-Context"] = []
    papers["Datasets"] = []
    papers["Not Yet Explored Task"] = []

    # sub-sections
    papers["Action / Activity Recognition"]["Action Recognition"] = []
    papers["Action / Activity Recognition"]["Hand-Object Interactions"] = []
    papers["Action / Activity Recognition"]["Usupervised Domain Adaptation"] = []
    papers["Action / Activity Recognition"]["Domain Generalization"] = []
    papers["Action / Activity Recognition"]["Source Free Domain Adaptation"] = []
    papers["Action / Activity Recognition"]["Test Time Training (Adaptation)"] = []
    papers["Action / Activity Recognition"]["Zero-Shot Learning"] = []

    papers["Action Anticipation"]["Short-Term Action Anticipation"] = []
    papers["Action Anticipation"]["Long-Term Action Anticipation"] = []
    papers["Action Anticipation"]["Future Gaze Prediction"] = []
    papers["Action Anticipation"]["Trajectory prediction"] = []
    papers["Action Anticipation"]["Region prediction"] = []

    papers["Multi-Modalities"]["Audio-Visual"] = []
    papers["Multi-Modalities"]["Depth"] = []
    papers["Multi-Modalities"]["Thermal"] = []
    papers["Multi-Modalities"]["Event"] = []
    papers["Multi-Modalities"]["IMU"] = []

    papers["Popular Architectures"]["2D"] = []
    papers["Popular Architectures"]["3D"] = []
    papers["Popular Architectures"]["RNN"] = []
    papers["Popular Architectures"]["Transformer"] = []

    def set_surveys(
            self,
            df: pd.DataFrame
    ) -> None:
        df_tmp = df.__deepcopy__()
        df_tmp = df_tmp[df_tmp["Category"] == "Surveys"].sort_values(["Year", "Conference"], ascending=False)
        list(df_tmp["Git Command"])
        self.surveys = list(df_tmp["Git Command"])

    def set_papers(
            self,
            df: pd.DataFrame,
    ) -> None:
        df_tmp = df.__deepcopy__()
        df_tmp = df_tmp[df_tmp["Category"] == "Papers"].sort_values(["Year", "Conference"], ascending=False)

        for section in self.papers.keys():
            if isinstance(self.papers[section], list):
                # prendi ed butta dentro
                df_tmp_section = df_tmp.__deepcopy__()
                df_tmp_section = df_tmp_section[df_tmp_section["Section"] == section].sort_values(
                    ["Year", "Conference"], ascending=False)
                self.papers[section] = list(df_tmp_section["Git Command"])
            else:
                # look to the subsection
                for subsection in self.papers[section].keys():
                    if isinstance(self.papers[section][subsection], list):
                        df_tmp_section = df_tmp.__deepcopy__()
                        df_tmp_section = df_tmp_section[df_tmp_section["Sub-section"] == subsection].sort_values(
                            ["Year", "Conference"], ascending=False)
                        self.papers[section][subsection] = list(df_tmp_section["Git Command"])
                    else:
                        logging.ERROR("It should be a list")

    def set_challenges(
            self,
            df: pd.DataFrame
    ) -> None:
        df_tmp = df.__deepcopy__()
        df_tmp = df_tmp[df_tmp["Category"] == "Challenges"]
        self.challenges = list(df_tmp["Git Command"])

    def set_devices(
            self,
            df: pd.DataFrame
    ) -> None:
        df_tmp = df.__deepcopy__()
        df_tmp = df_tmp[df_tmp["Category"] == "Devices"]
        self.devices = list(df_tmp["Git Command"])

    def set_init_readme(self):
        self.init_readme += "# [Egocentric Vision](https://egocentricvision.github.io/EgocentricVision/)" + \
                            "\n" + \
                            "better view here -> https://egocentricvision.github.io/EgocentricVision/" + "\n" + \
                            "\n" + "- [Surveys](#surveys)" + \
                            " \n" + "- [Papers](#papers)" + \
                            " \n" + "- [Datasets](#datasets)" + \
                            " \n" + "- [Challenges](#challenges)" + \
                            " \n" + "- [Devices](#devices)" + \
                            "\n"

    def set_body(self) -> None:

        # Surveys
        self.body += "" + "\n"
        self.body += "" + "\n"
        self.body += "" + "\n"
        self.body += "" + "\n"
        self.body += "## Surveys" + "\n"
        self.body += "" + "\n"

        for element in self.surveys:
            self.body += element + "\n"
            self.body += "" + "\n"

        # Papers
        marker_category = "##"
        marker_section = "###"
        marker_subsection = "####"

        self.body += "" + "\n"
        self.body += marker_category + " Papers" + "\n"
        self.body += "" + "\n"

        for element in self.papers.keys():
            if isinstance(self.papers[element], list):
                self.body += marker_section + " " + element + "\n"
                for paper in self.papers[element]:
                    self.body += paper + "\n"
                    self.body += "" + "\n"
            else:
                self.body += marker_section + " " + element + "\n"
                for sub_element in self.papers[element].keys():
                    if isinstance(self.papers[element][sub_element], list):
                        self.body += marker_subsection + " " + sub_element + "\n"
                        for paper in self.papers[element][sub_element]:
                            self.body += paper + "\n"
                            self.body += "" + "\n"
                    else:
                        logging.ERROR("It should be a list!!!")

        # Challenges
        self.body += "" + "\n"
        self.body += "## Challenges" + "\n"
        self.body += "" + "\n"

        for element in self.challenges:
            self.body += element + "\n"
            self.body += "" + "\n"

        # Devices
        self.body += "" + "\n"
        self.body += "## Devices" + "\n"
        self.body += "" + "\n"

        for element in self.devices:
            self.body += element + "\n"
            self.body += "" + "\n"


df = pd.read_csv('egodata.csv')
df = strip_dataframe(df)
df = add_git_command(df)

egoindex = Egoindex()
egoindex.set_surveys(df=df)
egoindex.set_papers(df=df)
egoindex.set_challenges(df=df)
egoindex.set_devices(df=df)

egoindex.set_init_readme()

print(egoindex.init_readme)
egoindex.set_body()
print(egoindex.body)

readme = egoindex.init_readme + egoindex.body + egoindex.final

with open("./README.md", 'w') as file:
    # Write the content to the file
    file.write(readme)
