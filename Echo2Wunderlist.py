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
import sched
import time

# Look for the require arguments to the script
if len(sys.argv) < 7:
  print "Usage: python Echo2Wunderlist.py <echo_email> <echo_password> <wunderlist_client_id> <wunderlist_access_token> <wunderlist_shopping_list_name> <wunderlist_todo_list_name> [<scheduler_frequency_s>]\n"
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
scheduler_priority = 1
list_tag = "(added by Alexa)"

print "Starting Echo2Wunderlist..."

print "Logging in to Amazon Echo..."
echo = PyEcho.PyEcho(echo_email, echo_password)

print "Setting up client session to Wunderlist..."
wunderlist_api = wunderpy2.WunderApi()
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

# Main function, runs on a scheduler, takes the next scheduler object as a parameter
def echo2wunderlist(next_scheduler):
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

  next_scheduler.enter(scheduler_frequency_s, 1, echo2wunderlist, (next_scheduler,))

# If the object creation was successful, start the scheduler to run forever
if echo and wunderlist:
  print "Starting Echo2Wunderlist scheduler\n"
  echo2wunderlist_scheduler = sched.scheduler(time.time, time.sleep)
  echo2wunderlist_scheduler.enter(scheduler_frequency_s, scheduler_priority, echo2wunderlist, (echo2wunderlist_scheduler,))
  echo2wunderlist_scheduler.run()
else:
  print "Error setting up Echo and/or wWnderlist - check username/passwords/tokens\n"
