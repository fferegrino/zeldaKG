config = dict()


def get_htmls_route(site):
    if not config:
        with open("config.txt", "r") as r:
            for line in r.readlines():
                l = line.split("=")
                config[l[0]] = l[1].strip()
    return config.get(site, None)
