from bs4 import BeautifulSoup, Tag
from requests.compat import urljoin
import re


def getURLs() -> list[str]:
    postOrder = range(0, 120 + 15, 15)
    urls = [combineURL(x) for x in postOrder]
    return urls


def combineURL(x: int) -> str:
    base = "https://www.oldclassiccar.co.uk/forum/phpbb/phpBB2/"
    ext = f"viewtopic.php?t=12591&postdays=0&postorder=asc&start={str(x)}"
    return urljoin(base, ext)


def getSoup(text: str) -> Tag:
    soup = BeautifulSoup(text, "html.parser")
    targetedSoup = soup.find("table", class_="forumline")
    return targetedSoup


def getIdName(soup: Tag) -> list[dict]:
    post_id_and_name_data = []
    id_and_names = soup.find_all("span", class_="name")

    for tag in id_and_names:
        tmp = {}
        tmp["id"] = tag.a["name"]
        tmp["name"] = tag.b.text
        post_id_and_name_data.append(tmp)
    return post_id_and_name_data


def getPostBody(soup: Tag) -> list[dict]:
    post_body_data = []
    post_bodies = soup.find_all("span", class_="postbody")
    post_reg = "_________________"  # some posts include profile biography section which we want to exclude

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
    return post_body_data


def getPostDate(soup: Tag) -> list[dict]:
    post_date_data = []
    post_date_bodies = soup.find_all("span", class_="postdetails")
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
    return post_date_data
