import codecs
import itertools
import json
import re
import time
from datetime import datetime
from urllib import parse as urlparse
from selenium.common.exceptions import NoSuchElementException, ElementNotInteractableException, WebDriverException

from requests import RequestException
from requests_html import HTML, HTMLSession

from selenium import webdriver


driver = webdriver.Chrome('chromedriver.exe')


__all__ = ['get_posts']


_base_url = 'https://facebook.com'
_user_agent = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
               "AppleWebKit/537.36 (KHTML, like Gecko) "
               "Chrome/76.0.3809.87 Safari/537.36")
_headers = {'User-Agent': _user_agent, 'Accept-Language': 'en-US,en;q=0.5'}

_session = None
_timeout = None

_likes_regex = re.compile(r'([0-9,.]+)\s+Like')
_comments_regex = re.compile(r'([0-9,.]+)\s+bình luận')
_shares_regex = re.compile(r'([0-9,.]+)\s+Shares')
_link_regex = re.compile(r"href=\"https:\/\/lm\.facebook\.com\/l\.php\?u=(.+?)\&amp;h=")

_cursor_regex = re.compile(r'href:"(/page_content[^"]+)"')  # First request
_cursor_regex_2 = re.compile(r'href":"(\\/page_content[^"]+)"')  # Other requests

_photo_link = re.compile(r"<a href=\"(/[^\"]+/photos/[^\"]+?)\"")
_image_regex = re.compile(
    r"<a href=\"([^\"]+?)\" target=\"_blank\" class=\"sec\">View Full Size<\/a>"
)
_image_regex_lq = re.compile(r"background-image: url\('(.+)'\)")
_post_url_regex = re.compile(r'/story.php\?story_fbid=')


def get_posts(account, pages=10, timeout=5, sleep=0):
    """Gets posts for a given account."""
    global _session, _timeout

    # _url = f'{_base_url}/{account}/posts/'
    url = f'{_base_url}/pg/{account}/posts/'
    print("\n==== url:{} ====".format(url))
    _session = HTMLSession()
    _session.headers.update(_headers)

    _timeout = timeout
    response = _session.get(url, timeout=_timeout)
    html = response.html
    cursor_blob = html.html


    # ********** Selenium *********** #
    driver.get(url)
    # ********** ******** *********** #

    while True:
        for article in html.find('._4-u2 ._4-u8'):
            # print("\n==== article:{} ====".format(article))
            yield _extract_post(article,html)

        pages -= 1
        if pages == 0:
            return

        cursor = _find_cursor(cursor_blob)
        next_url = f'{_base_url}{cursor}'

        if sleep:
            time.sleep(sleep)

        try:
            response = _session.get(next_url, timeout=timeout)
            response.raise_for_status()
            data = json.loads(response.text.replace('for (;;);', '', 1))
        except (RequestException, ValueError):
            return

        for action in data['payload']['actions']:
            if action['cmd'] == 'replace':
                html = HTML(html=action['html'], url=_base_url)
            elif action['cmd'] == 'script':
                cursor_blob = action['code']

# ********** Selenium *********** #
def expand_comment(_url):
    # print("\n==== _url:{} ====".format(_url))
    driver.get(_url)
    
    try:
        # time.sleep(5)
        elem = driver.find_element_by_xpath(
        "//span[@class='_1j-c']")
        print("===== IN ====")
        elem.click()
    except:
        print("===== OUT ====")

def get_posts_comment():
    return None

# ********** ******** *********** #

def _extract_post(article,html):
    chrome_options = webdriver.ChromeOptions()
    # chrome_options.add_argument('headless')
    driver = webdriver.Chrome(executable_path=settings.CHROME_DRIVER, chrome_options=chrome_options)
    post_url = _extract_post_url(article)
    # print("\n==== post_url:{} ====".format(post_url))
    # expand_comment(post_url)
    text, post_text, shared_text = _extract_text(article)
    return {
        'post_id': _extract_post_id(article),
        'text': text,
        'post_text': post_text,
        'shared_text': shared_text,
        'time': _extract_time(article),
        # 'link': _extract_link(article),


        # Start to code with these function:
        # 'image': _extract_image():    get image
        # 'likes': _find_and_search():  get number of likes, shares(options), comments
        # 'post_comments': _get_post_comments(): get all the comments from the post
        # 'image': _extract_image(article),
        # 'likes': _find_num_react(article) or 0, ### get number of react ##
        # 'comments': _find_num_cmt(article) or 0, ### get number of cmts ##
        # 'shares':  _find_and_search(article, '._3rwx ._42ft', _shares_regex, _parse_int) or 0,
        'post_url': post_url,
        
        'post_comments': crawl_comm()

        # with these 3 function above,
        # you can remove and replace the exists function
        # to easy way to your code
    }

### show all comments ###
# from datetime import datetime
# from selenium.webdriver.common.keys import Keys

# from modules.PostInfo import PostInfo
# from modules.data_backup.store_data import store_data
# re_group_member  = r"member_id="                        # regex string to find whether the post's owner is group member
# re_post_owner_id = r"member_id=(\d+)"                   # regex string to find the id of post's owner

# re_group_post_id = r"groups\/(.+)\/permalink\/(.+)\/"   #regex string to find the group name and post id

# re_comm_user_id  = r"id=(.+)&extragetparams=(.+)"
# re_tag_user_id = r"id=(.+)"

# def crawl_comm(signin_driver, links):
#     """Crawl users' post and comment

#     :Args:
#      - links - link of posts found

#     :Returns:
#    """

#     # this list contains info of posts
#     posts_info = []


#     for link in links:       
#         signin_driver.get(link)

#         # chrome_options = webdriver.ChromeOptions()
#         # prefs = {"profile.default_content_setting_values.notifications": 2}
#         # chrome_options.add_experimental_option("prefs", prefs)
#         # chrome_options.add_argument("start-maximized")
#         # chrome_options.add_argument("start-maximized")
#         # signin_driver = webdriver.Chrome(settings.CHROME_DRIVER, chrome_options=chrome_options)
        
        
#         #### click to show cmt ####
#         body = signin_driver.find_element_by_tag_name('body')
#         try:
#             click_cmt_element = signin_driver.find_element_by_xpath("//a[@class='_3hg- _42ft' and @role='button']")
#             print(type(click_cmt_element).__name__)
#             # num_cmt_text = click_cmt_element.text
#             # tmp = num_cmt_text.split(" ")
#             # num_cmt = int(tmp[0])
#             try:
#                 click_cmt_element.click()
#                 sleep(1)
#             except WebDriverException:
#                 pass

#         except NoSuchElementException:
#             pass

#         while True:
#             try:
#                 # a[@class='_4sxc _42ft'] : "See more replies" button
#                 # a[@class='_5v47 fss'] : "Show more content" button
#                 a_tag = signin_driver.find_element_by_xpath("//a[(@class='_4sxc _42ft' or @class='_5v47 fss') and @role='button']")
#                 check = False

#                 try:
#                     a_tag.click()
#                     sleep(2)
#                     check = True
#                 except WebDriverException:
#                     pass
#                 if check == False:
#                     body.send_keys(Keys.PAGE_DOWN)

#                 try:
#                     require_login = signin_driver.find_element_by_xpath("//div[@class='_62up']//a[@role='button']")
#                     try:
#                         require_login.click()
#                         sleep(0.75)
#                     except WebDriverException:
#                         pass

#                 except NoSuchElementException:
#                     pass

#             except (NoSuchElementException, ElementNotInteractableException):
#                 break
#         ### number of react #####
#         try:
#             num_react_ele = signin_driver.find_element_by_xpath("//span[@class='_3dlh _3dli']")
#             num_react = num_react_ele.text
#             print(num_react)

#         except NoSuchElementException:
#             print("No react")
#             pass

#         ### number of share ###
#         try:
#             num_share_element = signin_driver.find_element_by_xpath("//a[@class='_3rwx _42ft']")
#             num_share = num_share_element.text
#             print(num_share)
#         except NoSuchElementException:
#             print("No share")
#             pass
#         # cmts = signin_driver.find_elements_by_xpath("//u1[@class='_7a9a']//li")
#         # for cmt in cmts:
#         #     print(cmt.text)
#         # print(len(cmts))
#         # Show all comments and replies
#         all_comments = signin_driver.find_elements_by_xpath("//li//div[@aria-label='Comment' or @aria-label='Comment reply' or @aria-label='Trả lời bình luận' or @aria-label='Bình luận']")
#         # for cmt in all_comments:
#         #     print(cmt.text)
#         # print(all_comments)
#         num_cmt = len(all_comments)
#         print(num_cmt)
#         list_cmt = []

#         if len(all_comments) > 0:
#             comm_count = 0
#             # flag_comment_reply = True                       # True: the current is comment, False: otherwise
#             comm_replies = []

#             cmt_rep_content = ""
#             cmt_rep_user = ""
#             cmt_rep_tag = ""

#             for comment_reply in all_comments:

#                 comm_count += 1


#                 # this is comment
#                 if comment_reply.get_attribute('aria-label') == "Comment" or comment_reply.get_attribute('aria-label') == "Bình luận":
#                     # print("This is comment")
#                     # global flag_comment_reply
#                     flag_comment_reply = False
#                     # if this is not first comment
#                     # print(comm_count)
#                     if comm_count > 1:
#                         # print("found")
#                         # print(cmt_rep_content)
#                         # post_info.add_comment(cmt_rep_user, cmt_rep_content, cmt_rep_tag, comm_replies)
#                         # print(cmt_rep_content)
#                         list_cmt.append({
#                             "cmt_rep_user": cmt_rep_user,
#                             "cmt_rep_content": cmt_rep_content,
#                             "cmt_rep_tag": cmt_rep_tag,
#                             "comm_replies": comm_replies})
#                         comm_replies = []

#                 # this is reply of comment
#                 else:
#                     # print("This is reply")
#                     flag_comment_reply = True


#                 # extract data of reply or comment

#                 ## get comment's or reply's owner ID

#                 tmp = comment_reply.find_element_by_class_name('_6qw4')
#                 try:
#                     tmp_attr = tmp.get_attribute('data-hovercard')
#                     comm_rep_user = (findall(re_comm_user_id, tmp_attr)[0])[0]

#                 except TypeError:
#                     comm_rep_user = tmp.text

#                 # print("Comm user id: ", comm_rep_user)

#                 ## get content and (or) tagged user of comment or reply
#                 comm_rep_content = ""
#                 comm_rep_tag     = []
#                 try:
#                     comment_class = comment_reply.find_element_by_class_name('_3l3x')

#                     # get text in comment
#                     text = comment_class.text
#                     if text != None:
#                         comm_rep_content = comm_rep_content + text
#                     # print(comm_rep_content)
#                     # try:
#                     #     comm_rep_content = comment_class.find_element_by_tag_name('span').text
#                     #     # print("Text: ", comm_rep_content)
#                     # except NoSuchElementException:
#                     #     pass


#                     # get tag in comment
#                     try:

#                         tag = comment_class.find_element_by_tag_name('a').get_attribute('data-hovercard')

#                         comm_rep_tag.append(findall(re_tag_user_id, tag)[0])

#                         # print("Tag id: ", comm_rep_tag)
#                     except NoSuchElementException:
#                         pass
#                     except TypeError:
#                         pass

#                 except NoSuchElementException:
#                     pass


#                 # if the current is reply, add reply to list comm_replies
#                 if flag_comment_reply:
#                     comm_replies.append({
#                         'reply_user'   : comm_rep_user,
#                         'reply_comment': comm_rep_content,
#                         'reply_tag'    : comm_rep_tag
#                     })

#                 else:
#                     cmt_rep_user = comm_rep_user
#                     cmt_rep_tag = comm_rep_tag
#                     cmt_rep_content = comm_rep_content
#                     # print(cmt_rep_content)

#                 if comm_count >= num_cmt:
#                     # post_info.add_comment(cmt_rep_user, cmt_rep_content, cmt_rep_tag, comm_replies)
#                     list_cmt.append(
#                         {
#                             "cmt_rep_user": cmt_rep_user,
#                             "cmt_rep_content": cmt_rep_content,
#                             "cmt_rep_tag": cmt_rep_tag,
#                             "comm_replies": comm_replies}
#                     )

#         # append to posts_info
#             print(list_cmt)
#     #     posts_info.append(post_info)
#     sleep(3)

#     # signin_driver.quit()

def _expand_cmt(article):
    body = article.find('header body')
    
    click_cmt_element = article.find('a._3hg-._42ft')
    print("\n=== click_cmt_element:{} ===\n".format(click_cmt_element))
    try:
        click_cmt_element.click()
        time.sleep(0.5)
    except WebDriverException:
        pass

    while True:
        ### find all hidden cmt ###
        try:
            a_tag = article.find('a._4sxc._42ft' or 'a._5v47.fss')
            check = False

            try:
                a_tag.click()
                time.sleep(1)
                check = True
            except WebDriverException:
                pass

        ### if we found hidden commments, but we have not clicked, we scroll down to
        ### find that hidden comment
            if check == False:
                body.send_keys(Keys.PAGE_DOWN)

        ## when we scrape fb, fb display the table require us to log in,
        ## we click not now to skip it
            try: 
                require_login = article.find('a#expanding_cta_close_button._3j0u')
                try:
                    require_login.click()
                    time.sleep(0.25)
                except WebDriverException:
                    pass
            except NoSuchElementException:
                pass
            
        except (NoSuchElementException, ElementNotInteractableException):
            break
            

#### get number of react ####
def _find_num_react(article):
    _expand_cmt(article)
    num_react_element = article.find('span._3dlg')
    return int(num_react_element.text)

#### get number of comment ###
# all_comments = signin_driver.find_elements_by_xpath("//li//div[@aria-label='Comment' or @aria-label='Comment reply' or @aria-label='Trả lời bình luận' or @aria-label='Bình luận']")
#         num_cmt = len(all_comments)
#         print(num_cmt)
def _find_num_cmt(article):
    all_cmts = article.find("div._4eek._7a9b._7a9c.clearfix")
    return len(all_cmts)

def _extract_post_id(article):

    try:
        print("==== IN post ====")
        post_id = article.find('.commentable_item > input[type=hidden]')
        print("==== post_id: {} ====".format(post_id[2].attrs['value']))
        # data_ft = json.loads(article.attrs['data-ft'])
        # return data_ft['mf_story_key']
        
        return post_id[2].attrs['value']
    except (KeyError, ValueError):
        print("==== OUT post ====")
        return None


def _extract_text(article):
    nodes = article.find('p')
    if nodes:
        post_text = []
        shared_text = []
        ended = False
        for node in nodes[1:]:
            if node.tag == "header":
                ended = True
            if not ended:
                post_text.append(node.text)
            else:
                shared_text.append(node.text)

        text = '\n'.join(itertools.chain(post_text, shared_text))
        print("==== text: {} ====".format(text))
        post_text = '\n'.join(post_text)
        shared_text = '\n'.join(shared_text)

        return text, post_text, shared_text

    return None


def _extract_time(article):
    try:
        post_time = article.find('._5pcq > abbr')
        timestamp = post_time[0].attrs['data-utime']
        print("==== timestamp: {} ====".format(timestamp))
        return timestamp
        # return datetime.fromtimestamp(timestamp)
    except :
        return None


def _extract_photo_link(article):
    match = _photo_link.search(article.html)
    if not match:
        return None

    url = f"{_base_url}{match.groups()[0]}"

    response = _session.get(url, timeout=_timeout)
    html = response.html.html
    match = _image_regex.search(html)
    if match:
        return match.groups()[0].replace("&amp;", "&")
    return None


def _extract_image(article):
    image_link = _extract_photo_link(article)
    if image_link is not None:
        return image_link
    return _extract_image_lq(article)


def _extract_image_lq(article):
    story_container = article.find('div.story_body_container', first=True)
    other_containers = story_container.xpath('div/div')

    for container in other_containers:
        image_container = container.find('.img', first=True)
        if image_container is None:
            continue

        style = image_container.attrs.get('style', '')
        match = _image_regex_lq.search(style)
        if match:
            return _decode_css_url(match.groups()[0])

    return None


def _extract_link(article):
    html = article.html
    match = _link_regex.search(html)
    if match:
        return urlparse.unquote(match.groups()[0])
    return None


def _extract_post_url(article):
    query_params = ('story_fbid', 'id')

    elements = article.find('header a')
    for element in elements:
        href = element.attrs.get('href', '')
        match = _post_url_regex.match(href)
        if match:
            path = _filter_query_params(href, whitelist=query_params)
            return f'{_base_url}{path}'

    return None


def _find_and_search(article, selector, pattern, cast=str,*html):
    container = article.find(selector, first=True)
    # c = html[0].xpath('//div[@class="_7f6e"]')
    c = article.find('div._7f6e')
    print(" === commemt:{} ===".format(c))
    text = container and container.text

    match = text and pattern.search(text)
    return match and cast(match.groups()[0])


def _find_cursor(text):
    match = _cursor_regex.search(text)
    if match:
        return match.groups()[0]

    match = _cursor_regex_2.search(text)
    if match:
        value = match.groups()[0]
        return value.encode('utf-8').decode('unicode_escape').replace('\\/', '/')

    return None


def _parse_int(value):
    return int(''.join(filter(lambda c: c.isdigit(), value)))


def _decode_css_url(url):
    url = re.sub(r'\\(..) ', r'\\x\g<1>', url)
    url, _ = codecs.unicode_escape_decode(url)
    return url


def _filter_query_params(url, whitelist=None, blacklist=None):
    def is_valid_param(param):
        if whitelist is not None:
            return param in whitelist
        if blacklist is not None:
            return param not in blacklist
        return True  # Do nothing

    parsed_url = urlparse.urlparse(url)
    query_params = urlparse.parse_qsl(parsed_url.query)
    query_string = urlparse.urlencode(
        [(k, v) for k, v in query_params if is_valid_param(k)]
    )
    return urlparse.urlunparse(parsed_url._replace(query=query_string))
