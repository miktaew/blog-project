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


def private_message_date(message):
    return message['message'].creation_date


def private_message_unread_old_sort(request, messages):
    first = []
    second = []
    for message in messages:
        if not message['message'].read and message['message'].receiver == request.user:
            first.append(message)
        else:
            second.append(message)

    first.sort(key=private_message_date)
    second.sort(key=private_message_date)
    return [*first, *second]


def private_message_unread_new_sort(request, messages):
    first = []
    second = []
    for message in messages:
        if not message['message'].read and message['message'].receiver == request.user:
            first.append(message)
        else:
            second.append(message)

    first.sort(key=private_message_date, reverse=True)
    second.sort(key=private_message_date, reverse=True)
    return [*first, *second]