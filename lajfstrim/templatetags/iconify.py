from django import template
register = template.Library()

tag_phrase = re.compile("\B#([A-Za-z0-9_\-]+)")

@register.filter("iconify")
def blipify(value):
    value = tag_phrase.sub('#<a class="tagged" href="http://blip.pl/tags/\\1">\\1</a>', value)
    return value

