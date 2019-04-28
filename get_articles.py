import json
import requests

# from graphql we get the start nodes
graphql_url = "https://www.jiqizhixin.com/graphql"
start_post = {
    "operationName":"Dailies",
    "query": """query Dailies($cursor: String) {
    dailies(first: 10, after: $cursor) {
        edges {
        node {
            ...DailyInfo
            __typename
        }
        __typename
        }
        pageInfo {
        ...PageInfo
        __typename
        }
        __typename
    }
    }

    fragment DailyInfo on Daily {
    id
    title
    content
    likes_count
    url
    created_at
    path
    __typename
    }

    fragment PageInfo on PageInfo {
    endCursor
    hasNextPage
    __typename
    }
    """,
    "variables": {"cursor": ""}
}

headers = {
    "Host": "www.jiqizhixin.com",
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; WOW64; rv:66.0) Gecko/20100101 Firefox/66.0",
    "Accept-Language": "zh-CN,zh;q=0.8,zh-TW;q=0.7,zh-HK;q=0.5,en-US;q=0.3,en;q=0.2",
    "Accept-Encoding": "gzip, deflate, br",
    "Referer": "https://www.jiqizhixin.com/dailies",
    "content-type": "application/json",
    "X-CSRF-Token": "TCxmhF2Wpxy0wYkNqlnmlGCN+3lWQhGBMAuTqwK+RBQ93EY/xMn9zQI4q45Z/i18a2ccoW+D6Pt6MWYV6Ccyqw==",
    "Origin": "https://www.jiqizhixin.com",
    "Content-Length": "525",
    "Connection": "keep-alive",
    "Cookie": "ahoy_visitor=ea7511e4-6666-46ca-a519-77bf8e0d36f5; _ga=GA1.2.837414726.1556152181; ahoy_visit=a99a0754-74e8-4abb-85fa-9a50e258d699; _gid=GA1.2.1914872163.1556452140; _gat=1; _Synced_session=tATY6Nue56ypYn6dDEOPjM1duAy5eQyehPwzmziHCbRzZBUcgaKHxGy60ybnyg%2BvKck%2BhgHyvC5y63N26TxfzrkLR1GHi29eZukv2SnD8Wz5sHUfHwHzSbtfuMgeBx%2B9UFr1My6J3y8nt9dyWKCcscBye3VSaxAR4dZ1W6c8QwyvJEMZFLNHvJK6CBit%2FGQ%2BMoftqtpYt2ZrOf2bOLTVRZsBeTSLVp5Glf3FidBOh3utfCwYvcHFaYakb%2Bn5gFQt3POugYr9ItrMqvXNYRuUZDpbHYjBLDpap6ckYlkgNHL2DUdbFo8sves0lWwQskxW5MSagqtcWQxbbZc1Dw%3D%3D--0kBQqBKKuY0DH2gb--85OyYJnwxNgKyxO%2BXCXpJg%3D%3D",
}
r = requests.post(graphql_url, json= start_post, headers = headers)
current_nodes = json.loads(r.text)
pageInfo = current_nodes['data']['dailies']["pageInfo"]

# find endcursor as the next request's post cursor
def get_next_page(pageInfo):
    endcursor = pageInfo['endCursor']
    post_data = start_post 
    post_data["variables"]["cursor"] = endcursor
    r = requests.post(graphql_url, json=post_data, headers=headers)
    new_nodes = json.loads(r.text)
    return new_nodes


# set n as search times, collect the nodes together into dailies
dailies = current_nodes["data"]["dailies"]["edges"]
n = 1000
for i in range(n):
    try:
        new_page = get_next_page(pageInfo)
    except:
        print(new_page.text)
        continue

    dailies += new_page.get('data',{}).get("dailies", {}).get("edges", [])
    pageInfo = new_page['data']['dailies']["pageInfo"]
    print(i)
json.dump(dailies, open("dailies.json", "w"))