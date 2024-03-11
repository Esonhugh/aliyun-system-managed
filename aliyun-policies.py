import requests
import json
import os
from bs4 import BeautifulSoup
import logging as log

requests.urllib3.disable_warnings()

log.basicConfig(level=log.DEBUG)


PROXIES = {
    # "http": "http://127.0.0.1:8080",
    # "https": "http://127.0.0.1:8080"
}


def filter_out_policy_url_index(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')  
    lists = soup.select("li")
    policy_index_list = {}
    for l in lists:
        link = l.find("a").get("href")
        policyname = l.find("a").text
        log.debug("Found link parsed: %s, %s, startswith /zh/ram: %s", link, link.__class__, link.startswith("/zh/ram"))
        if link.startswith("/zh/ram/"):
            log.info("Found policy %s at index: %s", policyname, link)
            policy_index_list.update({policyname: link})
    return policy_index_list

def get_policy_index(url="https://help.aliyun.com/zh/ram/developer-reference/system-policy-reference/"):
    response = requests.get(url, headers={
        #"User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.114 Safari/537.36"
        "User-Agent": "curl/8.4.0"
    },proxies=PROXIES, verify=False)
    if response.status_code == 200:
        return response.text
    else:
        return ""

def filter_out_policy_content(html_content):
    soup = BeautifulSoup(html_content, 'lxml')
    policy_content = soup.find_all("pre", {
        "class": "pre codeblock language-json"
    })
    if len(policy_content) < 0:
        return
    log.debug("Found policy content: %s", policy_content[0].text)
    return policy_content[0].text

def get_policy_content(url, prefix="https://help.aliyun.com"):
    response = requests.get(prefix + url, proxies=PROXIES, verify=False)
    if response.status_code == 200:
        return response.text
    else:
        return ""

def main():
    index_html = get_policy_index() 
    if index_html == "":
        os.exit(1)  
    policy_index_list = filter_out_policy_url_index(index_html)
    log.info("find policies: %s", policy_index_list)

    for k, v in policy_index_list.items():
        log.debug("policy name: %s, url: %s", k, v)
        policy_content = get_policy_content(v)
        if policy_content == "":
            log.error("Failed to get policy content for %s", k)
            continue
        policy_content = filter_out_policy_content(policy_content)
        log.debug("the final policy %s content is: %s", k,policy_content)

        with open(k + ".json", "w") as f:
            f.write(policy_content)
            log.info("Write policy %s to file %s", k, k + ".json")

    log.info("All policies are fetched and saved to file")


if __name__ == "__main__":
    main()