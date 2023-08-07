import requests
import time
import json
import re
import urllib
# Webdriver
from selenium.webdriver import Firefox
from selenium.webdriver.firefox.service import Service
from selenium.webdriver.firefox.options import Options
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
# Automatic firefox selenium driver
from webdriver_manager.firefox import GeckoDriverManager
# Get environment variables
from dotenv import dotenv_values
# Utility
from utils import fetch_profile_path

url = 'https://www.facebook.com/api/graphql/'
base_referrer = "https://www.facebook.com/groups/{GROUP_ID}/members"
query = "GroupsCometMembersPageNewMembersSectionRefetchQuery"
doc_id = 6708203862579771

config = dotenv_values(".env")

friends_panel_class = "x9f619 x1n2onr6 x1ja2u2z x2bj2ny x1qpq9i9 xdney7k xu5ydu1 xt3gfkd xh8yej3 x6ikm8r x10wlt62 xquyuld"
friends_panel_selector = f"div[class='{friends_panel_class}']"

friend_link_class = (
    "x1i10hfl xjbqb8w x6umtig x1b1mbwd xaqea5y xav7gou x9f619 x1ypdohk xt0psk2 "
    "xe8uvvx xdj266r x11i5rnm xat24cr x1mh8g0r xexx8yu x4uap5 x18d9i69 xkhd6sd "
    "x16tdsg8 x1hl2dhg xggy1nq x1a2a7pz x1heor9g xt0b8zv"
) 
friend_link_selector = f"a[class='{friend_link_class}']"

loading_friends_panel_class = "x1a2a7pz x78zum5 x1q0g3np x1a02dak x1qughib"
loading_friends_panel_selector = f"div[class='{loading_friends_panel_class}'][data-visualcompletion='loading-state']"

# Functions:

class Scraper:

    def __init__(self, group_id, members, friends_all=None):
        """
        Create the scraper.

        :param group_id: The Facebook id of the group to scrape
        :param members: An existing list of facebook group members
        :param friends: An existing dictionary of members mapped to their friends
        """
        self.group_id = group_id

        # Fetch the profile path
        path = fetch_profile_path()

        # Create path
        options = Options()
        options.set_preference('profile', r"" + path)

        # Create service
        service = Service(GeckoDriverManager().install())

        # Create the driver
        self.driver = Firefox(service=service, options=options)

        # Save given data
        self.members = members
        if friends_all is None:
            friends_all = {}
        self.friends_all = friends_all

    def login(self):
        """
        Login to Facebook using the Selenium webdriver.
        """
        # Open Facebook
        self.driver.get("https://www.facebook.com/")

        # Accept cookies
        accept_cookies_button = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button[data-testid='cookie-policy-manage-dialog-accept-button']")
            )
        )

        accept_cookies_button.click()

        # Fill the login fields with our user and password.
        user_css_selector = "input[name='email']"
        password_css_selector = "input[name='pass']"

        username_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, user_css_selector))
        )
        password_input = WebDriverWait(self.driver, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, password_css_selector))
        )

        username_input.clear()
        username_input.send_keys(config["user"])
        password_input.clear()
        password_input.send_keys(config["password"])

        # Click the login button
        time.sleep(1)
        WebDriverWait(self.driver, 2).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, "button[type='submit']"))
        ).click()

    def scrape(self):
        """
        Scrape all members of a Facebook group using the Selenium webdriver.

        :return: the array of group members
        """
        # Navigate to the group's member list
        referrer = base_referrer.replace('{GROUP_ID}', group_id)

        time.sleep(2)
        self.driver.get(referrer)

        # Create session
        session = requests.session()
        session.cookies.update({
            cookie["name"]: cookie["value"]
            for cookie in self.driver.get_cookies()
        })

        pattern = r'\["DTSGInitData",\[\],{"token":"\S+","async_get_token":"\S+?"},\d+\]'
        match = re.search(pattern, self.driver.page_source)
        fb_dtsg_token = json.loads(match.group())[2]["token"]

        headers = {
            "accept": "*/*",
            "accept-language": "en-GB,en;q=0.5",
            "content-type": "application/x-www-form-urlencoded",
            "sec-ch-ua": "\" Not;A Brand\";v=\"99\", \"Google Chrome\";v=\"91\", \"Chromium\";v=\"91\"",
            "sec-ch-ua-mobile": "?0",
            "sec-fetch-dest": "empty",
            "sec-fetch-mode": "cors",
            "sec-fetch-site": "same-origin",
            "x-fb-friendly-name": query,
            "referrer": referrer,
            "referrerPolicy": "strict-origin-when-cross-origin",
        }

        page_info = dict(has_next_page=True, end_cursor=None)
        members = []

        # Request friends until there are no more
        page = 1
        while page_info["has_next_page"]:
            num_members = len(members)
            print(f"Reading group page {page}. ({num_members} members found)")

            response = session.post(
                url,
                headers=headers,
                data=urllib.parse.urlencode(
                    {
                        "fb_dtsg": fb_dtsg_token,
                        "fb_api_req_friendly_name": query,
                        "variables": json.dumps(
                            {
                                "count": 10,
                                "cursor": page_info["end_cursor"],
                                "groupID": group_id,
                                "id": group_id,
                                "recruitingGroupFilterNonCompliant": False,
                                "scale": 1.5,
                            }
                        ).replace(" ", ""),
                        "doc_id": doc_id,
                    }
                )
            )

            response_dict = json.loads(response.content)
            member_objects = response_dict["data"]["node"]["new_members"]["edges"]

            members += [
                dict(
                    id=str(member["node"]["id"]),
                    name=member['node']['name'],
                    url=member['node']['url']
                )
                for member in member_objects
                if member["node"]["__typename"] == "User"
            ]

            page_info = response_dict["data"]["node"]["new_members"]["page_info"]
            page += 1

        num_members = len(members)
        print(f"Number of members: {num_members}.")

        # Save members to the file
        with open("members", "w") as outfile:
            json.dump(members, outfile)   

        self.members = members
        return members

    def crawl(self, start_pos=0, end_pos=None):
        """
        Scrape the friends for all members on Facebook using the Selenium webdriver.

        :param start_pos: The position of the group member to start with
        :param end_pos: The position of the group member to end with
        :return: the dictionary of members mapped to their friends
        """
        def visit_member_page(member):
            """
            Visit the url of a member.

            :param member: The member data
            """
            link = member["url"]
            url_parsed = urllib.parse.urlparse(link)

            if url_parsed.path == "/profile.php":
                member_link =  f"{link}&sk=friends"
            else:
                member_link = f"{link}/friends"

            self.driver.get(member_link)
            time.sleep(1.5)

        def wait_for_every_friend_to_load():
            loading_element = self.driver.find_elements_by_css_selector(
                loading_friends_panel_selector
            )

            while len(loading_element) > 0:
                self.driver.find_element_by_xpath('//body').send_keys(Keys.END)
                time.sleep(0.5)
                loading_element = self.driver.find_elements_by_css_selector(
                    loading_friends_panel_selector
                )

        def get_friend_by_url(url):
            for member in self.members:
                if member["url"] == url:
                    return member
                
            return None  

        friends_all = self.friends_all
        # Add onto the friends
        num_members = len(self.members)
        record = self.members[start_pos:end_pos]
        for i, member in enumerate(record, start=1):
            print(f"Reading friends of {member['name']}. ({start_pos + i} of {num_members})")
            
            # Check this member
            visit_member_page(member)

            wait_for_every_friend_to_load()
            
            friends_panel = self.driver.find_element_by_css_selector(
                friends_panel_selector
            )
            
            friend_links = friends_panel.find_elements_by_css_selector(
                friend_link_selector
            )

            friends = []
            for link in friend_links:
                # Use the friend's url as a unique identifier
                link = link.get_attribute("href")
                friend = get_friend_by_url(link)

                # Check if this friend is in the group
                if friend is not None:
                    friends.append(
                        dict(
                            id=friend["id"],
                            name=friend["name"],
                            url=link,
                        )
                    )
            
            friends_all[member["id"]] = friends

            # Save current friends to the file
            with open("friends", "w") as outfile:
                json.dump(friends_all, outfile)   

        self.friends_all = friends_all
        return friends_all