import requests
from bs4 import BeautifulSoup
import pandas as pd
import re
from functools import reduce
import time

from functions.process_data import make_df, make_big_df

start_time = time.time()

"""
Data we need:
1. post id
2. name
3. date of the post
4. post body"""

post_id_and_name_data = []
post_date_data = []
post_body_data = []

postorder = range(0, 120 + 15, 15)
for order in postorder:
    # for order in [15]:
    order = str(order)
    url = f"https://www.oldclassiccar.co.uk/forum/phpbb/phpBB2/viewtopic.php?t=12591&postdays=0&postorder=asc&start={str(order)}"
    page = requests.get(url)
    soup = BeautifulSoup(page.content, "html.parser")
    results = soup.find("table", class_="forumline")

    # Get post id and name
    id_and_names = results.find_all("span", class_="name")
    for tag in id_and_names:
        tmp = {}
        tmp["id"] = tag.a["name"]
        tmp["name"] = tag.b.text
        post_id_and_name_data.append(tmp)

    post_bodies = results.find_all("span", class_="postbody")
    # quote = results.find_all("td", class_="quote")
    # print(quote)

    post_reg = "_________________"  # some posts include profile biography section
    for post in post_bodies:

        post_extra = post.text.strip()
        try:
            # Some forum posts are quotes which we want to exclude
            # and belong to the parent tag "td" and class "quote"
            parent = post.find_parent("td")
            if parent["class"]:
                continue
        except:
            pass

        try:
            tmp = {}

            if post_reg in post_extra:  # don't include biography section if present
                break_point = re.search(post_reg, post_extra).start()
                if post_extra[
                    :break_point
                ]:  # there are times where empty string is included
                    tmp["post_body"] = post_extra[:break_point]
                    post_body_data.append(tmp)
            else:
                if post_extra:  # catch empty string
                    tmp["post_body"] = post_extra
                    post_body_data.append(tmp)
        except:
            pass

    post_date_bodies = results.find_all("span", class_="postdetails")
    post_date_reg = "Posted: (.*?)Post subject:"
    for post_date in post_date_bodies:
        post_date_extra = post_date.text
        try:
            tmp = {}
            match = re.match(post_date_reg, post_date_extra)
            post_date = match.group(1)
            tmp["post_date"] = post_date.rstrip()
            post_date_data.append(tmp)

        except:
            pass

    assert (
        len(post_id_and_name_data) == len(post_date_data) == len(post_body_data)
    ), "Array length mismatch"

# combine dataframes in list for merges
dfList = []
dfList.append(pd.DataFrame(post_id_and_name_data))
dfList.append(pd.DataFrame(post_date_data))
dfList.append(pd.DataFrame(post_body_data))

df = reduce(lambda x, y: pd.merge(x, y, left_index=True, right_index=True), dfList)
print(df)

print("--- %s seconds ---" % (time.time() - start_time))
