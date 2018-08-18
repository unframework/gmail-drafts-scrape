#!/usr/bin/env python3

import sys
from googleapiclient.discovery import build
from httplib2 import Http
from oauth2client import file, client, tools
from base64 import urlsafe_b64decode
from datetime import datetime
from pytz import timezone

from pprint import pprint

SCOPES = 'https://www.googleapis.com/auth/gmail.readonly'

def get_draft_list(service, next_token=None):
    draft_list_result = service.users().drafts().list(
        userId='me',
        pageToken=next_token,
    ).execute()

    for item in draft_list_result.get('drafts', []):
        yield item

    if 'nextPageToken' in draft_list_result:
        yield from get_draft_list(service, next_token=draft_list_result['nextPageToken'])

def get_untitled_drafts(service, raw_draft_data):
    local_tz = timezone('America/Toronto')

    for draft_item in raw_draft_data:
        draft_result = service.users().drafts().get(userId='me', id=draft_item['id']).execute()
        draft_message = draft_result['message']

        subject = ''.join(list(map(lambda header: header['value'], filter(
            lambda header: header['name'].lower() == 'subject',
            draft_message['payload']['headers']
        ))))

        if subject == '' and 'parts' in draft_message['payload']:
            item_timestamp = datetime.fromtimestamp(int(draft_message['internalDate']) / 1000, local_tz)
            item_message_parts = list(map(
                lambda part: urlsafe_b64decode(part['body']['data']).decode('utf-8'),
                filter(lambda part: part['mimeType'] == 'text/plain' and 'data' in part['body'], draft_message['payload']['parts'])
            ))

            print(item_timestamp, file=sys.stderr)

            yield (item_timestamp.isoformat(), ''.join(item_message_parts).strip())


def main():
    store = file.Storage('token.json')
    creds = store.get()
    if not creds or creds.invalid:
        flow = client.flow_from_clientsecrets('credentials.json', SCOPES)
        creds = tools.run_flow(flow, store)
    service = build('gmail', 'v1', http=creds.authorize(Http()))

    untitled_drafts = get_untitled_drafts(service, get_draft_list(service))
    reverse_list = list(untitled_drafts)
    reverse_list.reverse()

    for timestamp, message in reverse_list:
        if message != '':
            print('[%s]\r\n\r\n%s\r\n\r\n---\r\n' % (timestamp, message))

main()

