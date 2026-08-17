import json
import urllib.request

BASE = "http://127.0.0.1:5002"


def get(path: str):
    with urllib.request.urlopen(BASE + path) as r:
        return json.load(r)


def main():
    print("/features ->", get("/features"))
    print("/generate -> generating suites...")
    print(get("/generate"))
    print("/feature/a/loop ->", get("/feature/a/loop"))
    print("/feature/a/cases -> showing AC6 cases ->", get("/feature/a/cases?ac=AC6"))
    print("/feature/a/coverage ->", get("/feature/a/coverage"))
    print("/outputs ->", get("/outputs"))


if __name__ == "__main__":
    main()
