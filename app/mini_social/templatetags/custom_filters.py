from django import template
import re


register = template.Library()

@register.filter
def youtube_code(url):
    youtube_regex = (
        r'(https?://)?(www\.)?'
        '(youtube|youtu|youtube-nocookie)\.(com|be)/'
        '(watch\?v=|embed/|v/|.+\?v=)?([^&=%\?]{11})'
    )

    youtube_match = re.match(youtube_regex, url)
    if not youtube_match:
        return None

    return youtube_match.group(6)

@register.filter(name='get_item')
def get_item(dictionary, key):
    return dictionary.get(key)

@register.filter
def get_previous(value, arg):
    try:
        return value[arg - 1]
    except IndexError:
        return None
    
@register.filter
def get_next(value, arg):
    try:
        return value[arg + 1]
    except IndexError:
        return None