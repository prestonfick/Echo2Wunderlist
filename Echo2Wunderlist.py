# Echo2Wunderlist
#
# By Preston Fick 4/30/16
#
# This is a simple python script designed to take items from your Amazon Echo
# lists, added by Alexa, and move them to your preferred Wunderlist

# Import PyEcho from submodule
import sys
sys.path.insert(0, './PyEcho')
import PyEcho

import wunderpy2
import requests
import sched
import time
import traceback
import smtplib
from email.mime.text import MIMEText

# Look for the required arguments to the script
if len(sys.argv) < 7:
  print "Usage: python Echo2Wunderlist.py <echo_email> <echo_password> <wunderlist_client_id> <wunderlist_access_token> <wunderlist_shopping_list_name> <wunderlist_todo_list_name> [<scheduler_frequency_s>] [<gmail_address> <gmail_app_password>]\n"
  sys.exit()

# Setup all the parameters
echo_email = sys.argv[1]
echo_password = sys.argv[2]
wunderlist_client_id = sys.argv[3]
wunderlist_access_token = sys.argv[4]
wunderlist_shopping_list_name = sys.argv[5]
wunderlist_todo_list_name = sys.argv[6]
scheduler_frequency_s = 10 # Default to 10 seconds
if len(sys.argv) >= 8:
  scheduler_frequency_s = int(sys.argv[7]) # Optional
gmail_address = None # Default to None, no email dump will occur
gmail_app_password = None # Default to None
if len(sys.argv) >= 10:
  gmail_address = sys.argv[8] # Optional
  gmail_app_password = sys.argv[9] # Optional
scheduler_priority = 1
list_tag = "(added by Alexa)"

# Globals
echo = None
wunderlist = None
shopping_wunderlist = None
todo_wunderlist = None

print "Starting Echo2Wunderlist...\n"

# Function to initialize our logins and lists
def initialize():
  global echo
  global wunderlist
  global shopping_wunderlist
  global todo_wunderlist

  print "Logging in to Amazon Echo..."
  echo = PyEcho.PyEcho(echo_email, echo_password)

  print "Setting up client session to Wunderlist..."
  wunderlist_api = wunderpy2.WunderApi()
  global wunderlist
  wunderlist = wunderlist_api.get_client(wunderlist_access_token, wunderlist_client_id)

  # Get our shopping list and to-do list objects from Wunderlist
  all_wunderlists = wunderlist.get_lists()
  for wunderlist_list in all_wunderlists:
    if wunderlist_list['title'] == wunderlist_shopping_list_name:
      shopping_wunderlist = wunderlist_list
      print "Found Wunderlist Shopping List: " + shopping_wunderlist['title']
    if wunderlist_list['title'] == wunderlist_todo_list_name:
      todo_wunderlist = wunderlist_list
      print "Found Wunderlist To-do List: " + todo_wunderlist['title']

# Function to move an item from an Echo list and put it in the Wunderlist
def move_echo_items_to_wunderlist(echo_items, target_wunderlist, echo_remove_function):
  moved_item = False
  for echo_item in echo_items:
    moved_item = True
    new_wunderlist_item = echo_item['text']
    print "Found new item for Wunderlist " + target_wunderlist['title'] + ": " + new_wunderlist_item
    wunderlist.create_task(target_wunderlist['id'], new_wunderlist_item.capitalize() + " " + list_tag)
    res = echo_remove_function(echo_item)
    print "Removed item from Echo list: " + res.text + "\n"
  return moved_item

# Function to email a message, used for crash notifications
def email_dump(dump_text):
  if (gmail_address is None) or (gmail_app_password is None):
    print "No email provided for crash notification"
    return
  dump_message = MIMEText(dump_text)
  dump_message['Subject'] = "Echo2Wunderlist Crash"
  dump_message['From'] = echo_email
  dump_message['To'] = gmail_address

  server = smtplib.SMTP('smtp.gmail.com:587')
  server.ehlo()
  server.starttls()
  server.login(gmail_address, gmail_app_password);
  server.sendmail(echo_email, gmail_address, dump_message.as_string())
  server.quit()
  print "Sent crash notification to " + gmail_address

# Main function, runs on a scheduler, takes the next scheduler object as a parameter
def echo2wunderlist(next_scheduler):
  global echo
  global wunderlist
  try:
    if (echo is None) and (wunderlist is None):
      initialize()
    print "Looking for new Echo Items..."
    new_items_added = False

    shopping_items = echo.shoppingitems()
    if move_echo_items_to_wunderlist(shopping_items, shopping_wunderlist, echo.deleteShoppingItem):
      new_items_added = True

    todo_items = echo.tasks()
    if move_echo_items_to_wunderlist(todo_items, todo_wunderlist, echo.deleteTask):
      new_items_added = True

    if new_items_added == False:
      print "No new items\n"
  except (requests.ConnectionError, requests.ReadTimeout, KeyError) as e:
    print e
    print "Setting objects to None in attempt to reinitialize the connection\n"
    dump_text = "e = {0}\n\nTraceback:\n{1}".format(e, traceback.format_exc())
    email_dump(dump_text)
    echo = None
    wunderlist = None
  except:
    print "Unexpected error"
    dump_text = "Unexpected Error\n\nTraceback:\n{0}".format(traceback.format_exc())
    email_dump(dump_text)
    raise

  next_scheduler.enter(scheduler_frequency_s, 1, echo2wunderlist, (next_scheduler,))

# Start the scheduler to run forever
print "Starting Echo2Wunderlist scheduler\n"
echo2wunderlist_scheduler = sched.scheduler(time.time, time.sleep)
echo2wunderlist_scheduler.enter(scheduler_frequency_s, scheduler_priority, echo2wunderlist, (echo2wunderlist_scheduler,))
echo2wunderlist_scheduler.run()
