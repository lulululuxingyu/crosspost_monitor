from __future__ import print_function

import sys
import pickle
import os.path
import praw
from praw import exceptions
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from datetime import datetime
import datetime

SCOPES = ['https://www.googleapis.com/auth/drive']

# create a reddit object
reddit = praw.Reddit(client_id="6T-JNcqFtQiKuw",
                     client_secret="NCxAb6ubsnr56tQdUE3Kc6_wNUE",
                     user_agent="jiliguala")


class WrongParentURL(Exception):
    pass


class WrongPostURL(Exception):
    pass


class SameURL(Exception):
    pass


def unix_time_to_eastern(time):
    return datetime.datetime.fromtimestamp(time).strftime('%Y.%m.%d.%H:%M:%S')


def collect(filename, parent, post):
    if parent == post:
        raise SameURL
    try:
        target_submission = reddit.submission(url=post)
    except praw.exceptions.InvalidURL:
        raise WrongPostURL
    try:
        original_submission = reddit.submission(url=parent)
    except praw.exceptions.InvalidURL:
        raise WrongParentURL

    timestamp = unix_time_to_eastern(target_submission.created_utc)
    line = 're\t' + target_submission.id + '\t' + timestamp + '\t' + str(target_submission.author) + '\t'

    original_subreddit = original_submission.subreddit
    original_subreddit_name = original_subreddit.display_name
    original_redditor_count = original_subreddit.subscribers
    original_redditor_active = original_subreddit.accounts_active
    original_url = 'https://www.reddit.com' + original_submission.permalink
    original_title = original_submission.title
    original_score = original_submission.score
    original_ratio = original_submission.upvote_ratio
    original_num_comments = original_submission.num_comments

    target_subreddit = target_submission.subreddit
    target_subreddit_name = target_subreddit.display_name
    target_redditor_count = target_subreddit.subscribers
    target_redditor_active = target_subreddit.accounts_active
    target_url = 'https://www.reddit.com' + target_submission.permalink
    target_title = target_submission.title

    line += original_subreddit_name + '\t'
    line += str(original_redditor_count) + '\t'
    line += str(original_redditor_active) + '\t'
    line += original_url + '\t'
    line += original_title + '\t'
    line += str(original_score) + '\t'
    line += str(original_ratio) + '\t'
    line += str(original_num_comments) + '\t'

    line += target_subreddit_name + '\t'
    line += str(target_redditor_count) + '\t'
    line += str(target_redditor_active) + '\t'
    line += target_url + '\t'
    line += target_title + '\n'

    with open(filename, 'a') as f:
        f.write(line)


def read_sheet(filename, spreadsheet_id):
    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file('credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
            # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)

    # range
    read_range = 'Sheet1!A:C'

    # Call the Sheets API
    sheet = service.spreadsheets()
    result = sheet.values().get(spreadsheetId=spreadsheet_id, range=read_range).execute()
    values = result.get('values', [])

    if not values:
        pass
    else:
        """candidates = []
        for i in range(0, len(values)):
            if (len(values[i]) == 2) or (len(values[i]) > 2 and values[i][2] != 'succeed'):
                candidates.append([i + 1, values[i][0], values[i][1]])
        s, f = split_candidates(candidates)
        requests = generate_requests(f, s)
        if len(requests) > 0:
            body = {
                'requests': requests
            }
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body).execute()
        for succeed in s:
            collect(filename, values[succeed - 1][0], values[succeed - 1][1])
        """
        f = []
        s = []
        for i in range(1, len(values)):
            if len(values[i]) < 2 or values[i][0] == '' or values[i][1] == '':
                f.append((i, 'not completed!'))
            elif len(values[i]) == 2 or (len(values[i]) > 2 and values[2] != 'succeed'):
                try:
                    collect(filename, values[i][0], values[i][1])
                    s.append(i)
                except WrongParentURL:
                    f.append((i, 'wrong parent url!'))
                except WrongPostURL:
                    f.append((i, 'wrong post url!'))
                except SameURL:
                    f.append((i, 'parent url and post url are the same!'))
                except:
                    f.append((i, 'unexpected error happened ' + str(sys.exc_info()[0])))
        requests = generate_requests(f, s)
        if len(requests) > 0:
            body = {
                'requests': requests
            }
            service.spreadsheets().batchUpdate(
                spreadsheetId=spreadsheet_id,
                body=body).execute()


def generate_requests(f, s):
    requests = []
    for fails in f:
        requests.append(write_request((fails[0], 3), fails[1]))
        requests.append(paint_request((fails[0], fails[0] + 1), False))
    for succeed in s:
        requests.append(write_request((succeed, 2), 'succeed'))
        requests.append(write_request((succeed, 3), ''))
        requests.append(paint_request((succeed, succeed + 1), True))
        requests.append(protect_request((succeed, succeed + 1)))
    return requests


def write_request(cell, message):
    """
    :param cell: (row, column)
    :param message: string
    :return request that write message to cell
    """
    request = {
        "updateCells": {
            "rows": {
                "values": [
                    {
                        "userEnteredValue": {
                            "stringValue": message
                        }
                    }
                ]
            },
            "fields": "userEnteredValue",
            "range": {
                "startRowIndex": cell[0],
                "endRowIndex": cell[0] + 1,
                "startColumnIndex": cell[1],
                "endColumnIndex": cell[1] + 1
            }
        }
    }
    return request


def protect_request(row_range):
    """
    :param row_range: (start row, end row); inclusion: [start_row, end_row)
    :return: addProtectedRangeRequest
    """
    request = {
        "addProtectedRange": {
            "protectedRange": {
                "range": {
                    "startRowIndex": row_range[0],
                    "endRowIndex": row_range[1],
                    "startColumnIndex": 0,
                    "endColumnIndex": 4,
                },
                "description": "Protecting total row",
                "warningOnly": True,
                "requestingUserCanEdit": False,
            }
        }
    }
    return request


def paint_request(row_range, success):
    """
    :param row_range: (start row, end row); inclusion: [start_row, end_row)
    :param success: whether the rows are a success
    :return: updateCellRequest
    """
    if success:
        color = {
            "green": 0.8,
            "red": 0.2
        }
    else:
        color = {
            "red": 0.8,
            "green": 0.2
        }
    row = []
    for i in range(0, 4):
        row.append({
            "userEnteredFormat": {
                "backgroundColor": color
            }
        })
    rows = []
    for i in range(row_range[0], row_range[1]):
        rows.append({
            "values": row
        })
    request = {
        "updateCells": {
            "rows": rows,
            "fields": "userEnteredFormat",
            "range": {
                "startRowIndex": row_range[0],
                "endRowIndex": row_range[1],
                "startColumnIndex": 0,
                "endColumnIndex": 4
            }
        }
    }
    return request


def main():
    spreadsheet_ids = []
    with open('../input_data/spreadsheet_ids', 'r') as f:
        line = f.readline()
        while line:
            if line[-1] == '\n':
                line = line[:-1]
            spreadsheet_ids.append(line)
            line = f.readline()
    for spreadsheet_id in spreadsheet_ids:
        read_sheet('../output_data/crosspost_data.tsv', spreadsheet_id)


if __name__ == '__main__':
    main()
