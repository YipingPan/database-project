# database-project
Author: YipingPan, Charlene Lau
PostgreSQL account: yp2524
PW:  HIDED

## URL of web application: http://35.196.55.58:8111/ (currently virtual machine is stopped)

A Second-hand furniture market was created. Users are able to login, register, or log out if already logged in.
Users, once logged-in are able to view their profile pages, view posts, add items to cart and sell items.


## Two examples of webpages:

### POSTS web page:
This page allows users to view all the posts that have been posted. 
This information comes from the post table in our database.
The user then selects one and enters its post_id to view more information about the item the post contains.
After entering the post_id, the post_id is matched to its item_id in the containsitem table and details about the item_id are selected from the item table in our database.
If the user decides to purchase the item, he/she then enters the item_id and the item will be added to the cart.

### SELL web page:
This page allows users to sell items by creating a post.
All details about an item are entered into the fields of the form.
The item and post is then updated in the tables in our database.
When the user goes to view posts, the post will appear on the posts page.

More functions are available. Please check the files.
