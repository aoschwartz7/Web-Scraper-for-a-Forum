import warnings
import argparse
from os.path import exists
from timeit import default_timer
import asyncio
from aiohttp import ClientSession


warnings.filterwarnings("ignore")


from functions.scraper import (
    getURLs,
    getSoup,
    getIdName,
    getPostBody,
    getPostDate,
)
from functions.process_data import make_df, make_big_df, flatten_data_lists

parser = argparse.ArgumentParser(description="Convert data to CSV or JSON.")
parser.add_argument(
    "-p",
    "--file-path",
    type=str,
    default="./",
    help="File path for export",
)
parser.add_argument(
    "-ft",
    "--file-type",
    type=str,
    default="csv",
    help="Export data as CSV or JSON [-ft='csv' or 'json'",
)
args = parser.parse_args()
assert exists(args.file_path), "File path does not exist."

start_time = default_timer()

"""
Data we need:
1. post id
2. name
3. date of the post
4. post body"""

post_id_and_name_data = []
post_date_data = []
post_body_data = []

data = []
urls = getURLs()


async def main():
    await get_site_content()


async def get_site_content():
    start_time_async = default_timer()

    async with ClientSession() as session:
        for url in urls:
            async with session.get(url) as response:
                print(f"[+] Getting Link [+] {url}  === {response.status} ")
                """ Get text from URLs, convert to soup object, gather data. """
                text = await response.text()
                soup = getSoup(str.encode(text))
                post_id_and_name_data.append(getIdName(soup))
                post_date_data.append(getPostDate(soup))
                post_body_data.append(getPostBody(soup))

    time_elapsed = default_timer() - start_time_async
    print("It took --- {} seconds --- for all the links".format(time_elapsed))


loop = asyncio.get_event_loop()
loop.run_until_complete(main())

# flatten our lists containing data
post_id_and_name_data_flat = flatten_data_lists(post_id_and_name_data)
post_date_data_flat = flatten_data_lists(post_date_data)
post_body_data_flat = flatten_data_lists(post_body_data)

# make sure arrays containing data match lengths
assert (
    len(post_id_and_name_data_flat)
    == len(post_date_data_flat)
    == len(post_body_data_flat)
), "Array length mismatch"

# make pandas dataframe
df1 = make_df(post_id_and_name_data_flat)
df2 = make_df(post_date_data_flat)
df3 = make_df(post_body_data_flat)
df = make_big_df([df1, df2, df3])

# export pandas dataframe to csv or json
path = args.file_path
if args.file_type == "csv":
    df.to_csv(path + "scraped_results.csv")
else:
    df.to_json(path + "scraped_results.json")


print("... and %s seconds total." % (default_timer() - start_time))
