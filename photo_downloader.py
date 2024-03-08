import requests
import time
import concurrent.futures
import os
from pathlib import Path


class ImageDownloader:
    def __init__(self):
        self.directory = str(Path(__file__).parent)

    def req(self, links, index):
        r = requests.get(links[index]).content
        with open("Photos/image_{}.jpg".format(index), 'wb') as write_image:
            write_image.write(r)

    def threaded_downloader(self, links):
        os.makedirs("Photos", exist_ok=True)
        start = time.perf_counter()
        with concurrent.futures.ThreadPoolExecutor() as executor:
            for index in range(len(links)):
                print("Fetching link: {}".format(links[index]))
                executor.submit(self.req, links, index)
        end = time.perf_counter()
        total = end - start
        print("Fetched {} links in {:.2f}".format(len(links), total))
        input("Press Enter to return.")