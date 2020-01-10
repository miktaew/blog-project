from django.template.defaultfilters import register


def fav_key_favs(favs):
    return favs['count']


def fav_key_alph(favs):
    return favs['blog'].name


def favs_adv_sort(favs):
    first = []  # those with count > 0
    second = [] # all others
    for item in favs:
        if item['count'] > 0:
            first.append(item)
        else:
            second.append(item)

    first.sort(key=fav_key_alph)
    second.sort(key=fav_key_alph)
    return [*first, *second]
