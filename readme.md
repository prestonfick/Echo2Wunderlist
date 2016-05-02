# Echo2Wunderlist

###### Simple Python script to move items from your Echo lists in to specified Wunderlists

Tested and run using Python 2.7.11

This script was created to allow integration of Wunderlist with the Echo. This script is designed to be run on a server and simply monitors your native Echo shopping and to-do lists provided by the Echo service. You can add items to your lists like normal then this script will put them in your specified Wunderlists and remove them from the Echo lists. This script uses PyEcho, which screen scrapes the Echo/Alexa page to login and use the undocumented APIs to access the shopping and to-do lists. It also uses wunderpy2 to access the standard Wunderlist API to move the items from your Echo lists to your Wunderlists.

### Python Dependencies

* wunderpy2
* requests
* bs4 (BeautifulSoup)

This also uses PyEcho as a submodule (use `--recursive` when cloning to pull that in)

### Usage

`Usage: python Echo2Wunderlist.py <echo_email> <echo_password> <wunderlist_client_id> <wunderlist_access_token> <wunderlist_shopping_list_name> <wunderlist_todo_list_name> [<scheduler_frequency_s>]`

* `echo_email` = Email address tied to your Echo account
* `echo_password` = Password for your Echo account
* `wunderlist_client_id` = Client ID obtained from Wunderlist (see below)
* `wunderlist_access_token` = Access token obtained from Wunderlist (see below)
* `wunderlist_shopping_list_name` = The exact name of your shopping list in Wunderlist
* `wunderlist_todo_list_name` = The exact name of your to-do list in Wunderlist
* `scheduler_frequency_s` = Rate that the script polls the Echo API in seconds (optional, default is 10s)

#### Wunderlist API Access

To use the Wunderlist APIs you'll need to register an application to get the credentials supplied as arguments above. Here are the steps to do that:

* Visit [https://developer.wunderlist.com](https://developer.wunderlist.com)
* Click `Register Your App`
* Enter some info on your app, the IP addresses are unused in this case so you can enter your IP, ex:
  * Name: Echo2Wunderlist App
  * Description: Move Echo items to Wunderlist
  * App URL: http://[your_ip]
  * Auth Callback URL: http://[your_ip]/callback 
* Click `Save`
* Your App credentials will show up:
  * `Client ID` is the `wunderlist_client_id` used in the arguments above
  * Click `Create Access Token` to obtain the `wunderlist_access_token` used in the arguments above


