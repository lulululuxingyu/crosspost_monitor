
import praw
from datetime import datetime
import datetime


# read all the accounts that the program want to monitor from the file account_list. each line should be an account name
def read_accounts(reddit):
    accounts = []
    with open('../input_data/account_list', 'r') as f:
        line = f.readline()
        while line:
            if line[-1] == '\n':
                line = line[:-1]
            accounts.append(reddit.redditor(line))
            line = f.readline()
    return accounts


def unix_time_to_eastern(time):
    return datetime.datetime.fromtimestamp(time).strftime('%Y.%m.%d.%H:%M:%S')


# given a file that store the ids of posts that have already been recorded, return a set of the ids
def load(filename):
    s = []
    with open(filename, 'r') as f:
        line = f.readline()
        while line:
            if line[-1] == '\n':
                line = line[:-1]
            s.append(line)
            line = f.readline()
    return s


# given a reddit account, and a filename, add all the new events to the file
def collect(reddit, account, num_post):
    filename = '../intermediate_data/collect_' + account.name + '_ids'
    collected = load(filename) # the list of submission ids that has already been collected
    # iterate through all the newest submissions(num_post)
    count = 0
    for target_submission in account.submissions.new(limit=num_post):
        if target_submission.id in collected:
            continue
        else:
            timestamp = unix_time_to_eastern(target_submission.created_utc)
            account_name = account.name
            target_subreddit = target_submission.subreddit
            target_subreddit_name = target_subreddit.display_name
            target_redditor_count = target_subreddit.subscribers
            target_redditor_active = target_subreddit.accounts_active
            target_url = 'https://www.reddit.com' + target_submission.permalink
            target_title = target_submission.title
            line = 'cr\t' + target_submission.id + '\t' + timestamp + '\t'
            line += account_name + '\t'
            try:  # crosspost
                original_submission = reddit.submission(target_submission.crosspost_parent.split('_')[1])
                original_subreddit = original_submission.subreddit
                original_subreddit_name = original_subreddit.display_name
                original_redditor_count = original_subreddit.subscribers
                original_redditor_active = original_subreddit.accounts_active
                original_url = 'https://www.reddit.com' + original_submission.permalink
                original_title = original_submission.title
                original_score = original_submission.score
                original_ratio = original_submission.upvote_ratio
                original_num_comments = original_submission.num_comments

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
                with open('../output_data/crosspost_data.tsv', 'a') as f:
                    f.write(line)
                    count += 1
            except:  # repost
                pass
            collected.append(target_submission.id)
    if len(collected) > num_post:
        collected = collected[-num_post:-1]
    with open(filename, 'a') as f:
        for c in collected:
            f.write(c + '\n')
    return count


# collect the events to different files
def main():
    # create a reddit object
    reddit = praw.Reddit(client_id="VnwzAaTRYXCxfg",
                         client_secret="rWHW9vGspXgHmGvHRdYtQcs30d0",
                         user_agent="wuliwala")

    accounts = read_accounts(reddit)
    # setup all the intermediate data files
    #filenames = []
    total_count = 0
    for account in accounts:
        #filenames.append('../intermediate_data/collect_' + account.name)
        filename = '../intermediate_data/collect_' + account.name + '_ids'
        with open(filename, 'a') as f:
            pass
        total_count += collect(reddit, account, 50)
    print(total_count)


if __name__ == '__main__':
    main()