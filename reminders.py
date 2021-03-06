#! /usr/bin/env python

# Aha! webhook for Slack
# Cody King (Apes of Wrath 668)
# Jan 2018


# imports
import sys
from urllib import request
import requests, json
from datetime import datetime, timedelta
import time



def main():
    run()


# Check that number of days has been given
# call method to post message to Slack
def run():
    if len(sys.argv) > 2:
        print('Usage: ./reminders.py [days_until_deadline]')
        sys.exit(2)

    elif len(sys.argv) == 2:
        send_message_to_slack(sys.argv[1])
        #print('Success.')

    else:
        send_message_to_slack(7)
        #print('Success.')


# Posting to Slack channel
def send_message_to_slack(days):
    # Get upcoming tasks from Aha!
    slack_message = getFeatures(days)

    # Combine the array of strings into single string
    text = ''.join(slack_message)

    # JSON formatted attachment for Slack
    post = {
            	"fallback": 'Deadlines less than {} days away'.format(days),
            	#"text": "Daily reminder",
            	"pretext": "<https://apesofwrath668.aha.io/bookmarks/gantt_charts/6508438327823751704|Upcoming Deadlines>",
            	"color": 'warning', # Can either be one of 'good', 'warning', 'danger', or any hex color code

            	# Fields are displayed in a table on the message
            	"fields": [
            		{
            			"title": 'Here are the features with deadlines less than {} days away'.format(days), # The title may not contain markup and will be escaped for you
                        "value": '{}'.format(text),
            			"short": False # Optional flag indicating whether the `value` is short enough to be displayed side-by-side with other values
            		}
            	]
            }

    # send message to Slack
    try:
        json_data = json.dumps(post)

        req_sched = request.Request(get_url('apes_sched'),
                              data=json_data.encode('ascii'),
                              headers={'Content-Type': 'application/json'})

        req_gen = request.Request(get_url('apes_gen'),
                              data=json_data.encode('ascii'),
                              headers={'Content-Type': 'application/json'})

        request.urlopen(req_sched)
        request.urlopen(req_gen)

    except Exception as em:
        print("EXCEPTION: " + str(em))


# fetches features from Aha!
# returns an array of features that are due within <days> days
def getFeatures(days):
    # Get all features
    response_features = requests.get('https://secure.aha.io/api/v1/features/?per_page=100', headers=getHeaders())
    data = response_features.json()

    # get reference_nums of all features
    reference_nums = []
    names = []
    for i in range(len(data.get('features'))):
        reference_nums.append(data.get('features')[i].get('reference_num'))
        names.append(data.get('features')[i].get('name'))

    # using the reference_nums, fetch features and extract the due date and release name
    due_dates = []
    release_names = []
    for i in range(len(names)):
        response_indiv = requests.get('https://secure.aha.io/api/v1/features/{}'.format(reference_nums[i]), headers=getHeaders())
        data = response_indiv.json()
        due_dates.append(data.get('feature').get('due_date'))
        release_names.append(data.get('feature').get('release').get('name'))

    # composes message to be returned
    slack_message = []
    for i in range(len(names)):
        if is_upcoming(due_dates[i], days):
            slack_message.append('\n{}, {} ({})'.format(release_names[i], names[i], due_dates[i]))

    # http status code returned by api call
    #print(response_indiv)

    return slack_message


# returns true if <date> is within <days> days from now
def is_upcoming(date, days):
    vals = date.split('-')
    today = time.localtime()
    date_format = "%Y/%m/%d"
    a = datetime.strptime('{}/{}/{}'.format(vals[0], vals[1], vals[2]), date_format)
    b = datetime.strptime('{}/{}/{}'.format(today[0], today[1], today[2]), date_format)
    delta = a - b

    num_days = delta / timedelta (days=1)

    if num_days <= int(days) and num_days >= 0:
        return True

    else:
        return False


# fetches webhook url, api keys, etc.
def get_url(index):
    with open('stuff.txt') as f:
        content = f.readlines()

    if index == 'king_testing':
        return content[7].rstrip('\n')

    if index == 'apes_sched':
        return content[10].rstrip('\n')

    if index == 'apes_gen':
        return content[13].rstrip('\n')

    if index == 'aha_api_key':
        return content[16].rstrip('\n')


# headers for Aha! api call
def getHeaders():
    return {
        'Authorization': 'Bearer {}'.format(get_url('aha_api_key')),
        'X-Aha-Account': 'apesofwrath668',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }


if __name__ == '__main__':
    main()
