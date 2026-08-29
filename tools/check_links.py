"""Checks every Link paper / Link page / Link code / Link video URL in
egodata.csv and reports which ones are unreachable. Writes a Markdown report
to ./link_report.md and a `broken_count` GitHub Actions output. Never fails
the job by itself -- the workflow decides what to do with the count.

Run from inside tools/, same as read_cvs_generate_readme.py.
"""
import concurrent.futures as cf
import csv
import os

import requests

CSV_PATH = 'egodata.csv'
LINK_COLUMNS = ['Link paper', 'Link page', 'Link code', 'Link video']
TIMEOUT = 12
MAX_WORKERS = 12
USER_AGENT = 'Mozilla/5.0 (compatible; EgocentricVision-link-checker/1.0; +https://egocentricvision.github.io/EgocentricVision/)'


def check_url(url):
    headers = {'User-Agent': USER_AGENT}
    try:
        resp = requests.head(url, allow_redirects=True, timeout=TIMEOUT, headers=headers)
        if resp.status_code >= 400 or resp.status_code == 405:
            # Some servers don't support HEAD properly -- retry with GET before flagging it.
            resp = requests.get(url, allow_redirects=True, timeout=TIMEOUT, headers=headers, stream=True)
        return resp.status_code
    except requests.RequestException as e:
        return type(e).__name__


def collect_tasks():
    tasks = []
    with open(CSV_PATH, encoding='utf-8', newline='') as f:
        reader = csv.DictReader(f)
        for line_no, row in enumerate(reader, start=2):
            title = (row.get('Title') or '').strip()
            for col in LINK_COLUMNS:
                url = (row.get(col) or '').strip()
                if url.startswith('http'):
                    tasks.append((line_no, title or '(untitled)', col, url))
    return tasks


def main():
    tasks = collect_tasks()
    broken = []

    with cf.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        future_to_task = {executor.submit(check_url, t[3]): t for t in tasks}
        for future in cf.as_completed(future_to_task):
            line_no, title, col, url = future_to_task[future]
            result = future.result()
            if isinstance(result, int) and result < 400:
                continue
            broken.append({'line': line_no, 'title': title, 'column': col, 'url': url, 'result': result})

    broken.sort(key=lambda item: item['line'])

    with open('link_report.md', 'w', encoding='utf-8') as f:
        if not broken:
            f.write('No broken links found. ✅\n')
        else:
            f.write(f'Found **{len(broken)}** broken link(s) out of {len(tasks)} checked in `tools/egodata.csv`:\n\n')
            f.write('| Line | Title | Field | URL | Result |\n')
            f.write('|---|---|---|---|---|\n')
            for item in broken:
                f.write(f"| {item['line']} | {item['title']} | {item['column']} | {item['url']} | {item['result']} |\n")

    github_output = os.environ.get('GITHUB_OUTPUT')
    if github_output:
        with open(github_output, 'a', encoding='utf-8') as f:
            f.write(f'broken_count={len(broken)}\n')

    print(f'Checked {len(tasks)} link(s), {len(broken)} broken.')


if __name__ == '__main__':
    main()
