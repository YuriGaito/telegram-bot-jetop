from __future__ import print_function
from apiclient import discovery
from oauth2client import client
from oauth2client import tools
from oauth2client.file import Storage
from telepot.namedtuple import InlineKeyboardMarkup, InlineKeyboardButton
import calendar
from datetime import datetime
import sys, time, datetime
import httplib2
import os
import locale
loc = locale.getlocale()
locale.setlocale(locale.LC_ALL, loc)

try:
    import argparse
    flags = argparse.ArgumentParser(parents=[tools.argparser]).parse_args()
except ImportError:
    flags = None

# If modifying these scopes, delete your previously saved credentials
# at ~/.credentials/calendar-python-quickstart.json
SCOPES = 'https://www.googleapis.com/auth/calendar.readonly'
CLIENT_SECRET_FILE = 'client_secret.json'
APPLICATION_NAME = 'Google Calendar API Python Quickstart'


def get_credentials():
    """Gets valid user credentials from storage.

    If nothing has been stored, or if the stored credentials are invalid,
    the OAuth2 flow is completed to obtain the new credentials.

    Returns:
        Credentials, the obtained credential.
    """
    home_dir = os.path.expanduser('~')
    credential_dir = os.path.join(home_dir, '.credentials')
    if not os.path.exists(credential_dir):
        os.makedirs(credential_dir)
    credential_path = os.path.join(credential_dir,
                                   'calendar-python-quickstart.json')

    store = Storage(credential_path)
    credentials = store.get()
    if not credentials or credentials.invalid:
        flow = client.flow_from_clientsecrets(CLIENT_SECRET_FILE, SCOPES)
        flow.user_agent = APPLICATION_NAME
        if flags:
            credentials = tools.run_flow(flow, store, flags)
        else: # Needed only for compatibility with Python 2.6
            credentials = tools.run(flow, store)
        
    return credentials

def search_calendar(start_date, end_date):
            #ATTENZIONE: la data per queste API deve essere in formato RFC 3339
            credentials = get_credentials()
            http = credentials.authorize(httplib2.Http())
            service = discovery.build('calendar', 'v3', http=http)
       
            eventsResult = service.events().list(
              calendarId='primary', timeMin=start_date, timeMax=end_date, singleEvents=True,
              orderBy='startTime', maxResults = 10).execute()
            events = eventsResult.get('items', [])

            return_message = ""
            if not events:
             start = datetime.datetime.strptime(start_date, '%Y-%m-%dT%H:%M:%S.%WZ')
             return_message = "*"+(start.strftime('%A %d')).capitalize()+ " "+(start.strftime('%B')).capitalize()+"*\nNon hai nessun impegno (ufficiale)!"
            for event in events:
             start = event['start'].get('dateTime', event['start'].get('date'))    
             start = datetime.datetime.strptime(event['start']['dateTime'], '%Y-%m-%dT%H:%M:%S+%f:%W') #parsing da rivedere/fare meglio
             end = datetime.datetime.strptime(event['end']['dateTime'], '%Y-%m-%dT%H:%M:%S+%f:%W')
             summary = event['summary']
             return_message = '*'+(start.strftime('%A %d')).capitalize()+ " " +(start.strftime('%B')).capitalize()+'*'+'\n'+summary+'\n_Dalle {}:{} alle {}:{}_\n'.format(start.strftime("%H"), start.strftime("%M"), end.strftime("%H"), end.strftime("%M"))
            return return_message
                                                                                                                            
def create_calendar(year,month):
           
           keyboard = InlineKeyboardMarkup(inline_keyboard=[
                   [InlineKeyboardButton(text=(calendar.month_name[month]).capitalize()+" "+str(year), callback_data='ignore')],
               ])
           week_days=["L","M","M","G","V","S","D"]
           row=[]
           for day in week_days:
             row.append(InlineKeyboardButton(text=day,callback_data="ignore"))
           keyboard[0].append(row)
           
           my_calendar = calendar.monthcalendar(year, month)
           for week in my_calendar:
             row=[]
             for day in week:
              if(day==0):
                row.append(InlineKeyboardButton(text= " ",callback_data="ignore"))
              else:
                row.append(InlineKeyboardButton(text = str(day),callback_data="calendar-day-"+str(day)))
             keyboard[0].append(row)

           row=[]
           row.append(InlineKeyboardButton(text="<",callback_data="previous-month"))
           row.append(InlineKeyboardButton(text=" ",callback_data="ignore"))
           row.append(InlineKeyboardButton(text=">",callback_data="next-month"))
           keyboard[0].append(row)
           return keyboard
