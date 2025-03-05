import requests


def fetch_url(url):
    response = requests.get(url)
    return response.text


if __name__ == "__main__":
    url = "https://naver.com"
    content = fetch_url(url)
    print(f"Response from {url}: {content[:100]}...")  # 응답의 처음 100자만 출력
