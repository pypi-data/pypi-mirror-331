list_of_builds = {
    "2in-100": {
        "url": "https://www.youtube.com/watch?v=MxG22nbBNvQ",
        "size_in": 2.0,
        "cost_dollar": 100.0,
    },
    "3_5in-160": {
        "url": "https://www.youtube.com/watch?v=aXrrg48auhU",
        "size_in": 3.5,
        "cost_dollar": 160.0,
        "weight_gr": 250.0,
    },
    "5in": {
        "url": "https://www.youtube.com/watch?v=XB6b0HrDGeA",
        "size_in": 5.0,
        "build_year": 2023,
        "weight_gr": 767.0,
        "comments": "Amazon links ⚠️",
    },
    "5in-2": {
        "url": "https://www.youtube.com/watch?v=zj90LK8XR68",
        "size_in": 5.0,
        "cost_dollar": 816.38,
        "weight_gr": 426,
        "build_year": 2024,
        "purchase_link": "https://www.aliexpress.com/item/1005005105185798.html",
    },
    "7-in": {
        "url": "https://www.youtube.com/watch?v=0jOUTYBneVo",
        "size_in": 7.0,
        "cost_dollar": 150.0,
        "build_year": 2024,
    },
    "9-in": {
        "url": "https://www.youtube.com/watch?v=o8_5ppHROJ4",
        "size_in": 9.0,
        "build_year": 2025,
    },
    "unknown": {
        "url": "https://www.youtube.com/watch?v=u_ArriXbrR0",
        "weight_gr": 25.0,
        "build_year": 2024,
    },
    "unknown-2": {
        "url": "https://www.youtube.com/watch?v=SfFl_-tof4Y",
        "weight_gr": 371,
        "build_year": 2021,
    },
    "7-in-2": {
        "url": "https://www.youtube.com/watch?v=d2NiH5ciV5c",
        "size_in": 7.0,
        "build_year": 2023,
    },
}

build_count = len(
    [build_name for build_name in list_of_builds if build_name != "template"]
)

list_of_columns = {
    "marquee": "",
    "url": "",
    "size_in": "size",
    "cost_dollar": "cost",
    "weight_gr": "weight",
    "build_year": "build",
    "comments": "",
    "purchase_link": "🛒",
}
items = list(list_of_columns.values())
for build_name, build in list_of_builds.items():
    if build_name == "template":
        continue

    for column in list_of_columns:
        if column == "marquee":
            items += [
                "[![image](https://github.com/kamangir/assets/blob/main/blue-flie/fpv/{}.png?raw=true)]({})".format(
                    build_name,
                    build["url"],
                )
            ]
        elif column == "url":
            items += [build["url"]]
        elif column == "size_in":
            items += ['{:.1f}"'.format(build["size_in"]) if "size_in" in build else "?"]
        elif column == "cost_dollar":
            items += [
                (
                    "${:.1f}".format(build["cost_dollar"])
                    if "cost_dollar" in build
                    else "?"
                )
            ]
        elif column == "weight_gr":
            items += [
                (
                    "{:.1f} gr".format(build["weight_gr"])
                    if "weight_gr" in build
                    else "?"
                )
            ]
        elif column == "build_year":
            items += [str(build.get("build_year", ""))]
        elif column == "purchase_link":
            items += [
                (
                    "[🛒]({})".format(build["purchase_link"])
                    if "purchase_link" in build
                    else ""
                )
            ]
        elif column == "comments":
            items += [build.get("comments", "")]
