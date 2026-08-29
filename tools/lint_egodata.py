"""Flags egodata.csv rows that read_cvs_generate_readme.py would silently drop
from the generated README (unrecognized Category, or a Papers row that won't
match any section/sub-section grouping).

Important quirk of the generator this linter mirrors: for a *sub-sectioned*
top-level section (e.g. "Action / Activity Recognition"), the generator
classifies rows by matching the "Sub-section" column against that section's
known sub-section values -- it never actually checks the "Section" column for
those rows. So a row lands correctly as long as its Sub-section is one of the
known values, no matter what (or whether) "Section" says. Only *flat* (non
sub-sectioned) top-level sections like "Datasets" or "Retrieval" are matched by
the "Section" column. Sub-section is required, and must be exact, for every
sub-sectioned section; there is no flat fallback for those.

Prints GitHub Actions ::warning:: annotations and a summary; never exits
non-zero, so it never blocks the regeneration job on its own -- it's a report,
not a gate. Run from inside tools/, same as read_cvs_generate_readme.py.

Keep the SUBSECTIONED / FLAT_SECTIONS vocabulary here in sync with the
Egoindex class in read_cvs_generate_readme.py and with add-paper.html's
SECTIONS constant -- all three must agree (including the vocabulary's typos)
for a row to end up in the right place.
"""
import pandas as pd

VALID_CATEGORIES = {"Papers", "Surveys", "Challenges", "Devices"}

SUBSECTIONED = {
    "Action / Activity Recognition": ["Action Recognition", "Hand-Object Interactions", "Usupervised Domain Adaptation", "Domain Generalization", "Source Free Domain Adaptation", "Test Time Training (Adaptation)", "Zero-Shot Learning"],
    "Action Anticipation": ["Short-Term Action Anticipation", "Long-Term Action Anticipation", "Future Gaze Prediction", "Trajectory prediction", "Region prediction"],
    "Multi-Modalities": ["Audio-Visual", "Depth", "Thermal", "Event", "IMU"],
    "Popular Architectures": ["2D", "3D", "RNN", "Transformer"],
}

FLAT_SECTIONS = {
    "Temporal Segmentation (Action Detection)", "Retrieval", "Segmentation", "Video-Language",
    "Few-Shot Action Recognition", "Gaze", "From Third-Person to First-Person", "NeRF",
    "User Data from an Egocentric Point of View", "Localization", "Privacy protection", "Tracking",
    "Social Interactions", "Multiple Egocentric Tasks", "Activity-context", "Diffusion models",
    "Video summarization", "Applications", "Human to Robot", "Asssitive Egocentric Vision",
    "Other EGO-Context", "Datasets", "Not Yet Explored Task",
}

ALL_SUBSECTIONS = {s for subs in SUBSECTIONED.values() for s in subs}


def clean(value):
    return value.strip() if isinstance(value, str) else ''


def warn(line_no, message):
    print(f"::warning file=tools/egodata.csv,line={line_no}::{message}")


def check_papers_row(section, subsection):
    """Returns None if the row would be classified correctly, else a warning message."""
    if section == 'Datasets':
        return None  # flat list, matched by Section; Sub-section is irrelevant here

    if subsection:
        if subsection in ALL_SUBSECTIONS:
            return None  # matched by Sub-section alone -- Section's text doesn't matter to the generator
        return (
            f'Sub-section "{subsection}" is not one of the known sub-section values '
            f'-- this row will not appear in the Papers list.'
        )

    # Sub-section is empty: only an exact, flat (non sub-sectioned) Section can save it.
    if section in FLAT_SECTIONS:
        return None
    if section in SUBSECTIONED:
        return (
            f'Section "{section}" needs a Sub-section (one of {SUBSECTIONED[section]}) '
            f'but none was given -- this row will not appear in the Papers list.'
        )
    return f'Section "{section}" is not recognized and Sub-section is empty -- this row will not appear in the Papers list.'


def main():
    df = pd.read_csv('egodata.csv', dtype=str)
    issues = 0

    for idx, row in df.iterrows():
        line_no = idx + 2  # +1 for 0-index, +1 for the header row
        category = clean(row.get('Category'))
        section = clean(row.get('Section'))
        subsection = clean(row.get('Sub-section'))
        title = clean(row.get('Title')) or '(untitled)'

        if not category:
            continue  # fully blank rows are harmless, ignore them

        if category not in VALID_CATEGORIES:
            warn(line_no, f'"{title}": unrecognized Category "{category}" -- this row will not appear anywhere on the site.')
            issues += 1
            continue

        if category != 'Papers':
            continue  # Surveys/Challenges/Devices don't use Section/Sub-section

        message = check_papers_row(section, subsection)
        if message:
            warn(line_no, f'"{title}": {message}')
            issues += 1

    if issues:
        print(f"lint_egodata.py: {issues} row(s) would be silently dropped from the generated README (see warnings above).")
    else:
        print("lint_egodata.py: all rows look classifiable.")


if __name__ == '__main__':
    main()
