# -*- coding: utf-8 -*-
from django import template
import re
register = template.Library()

tag_phrase = re.compile("\B#(\w+)")

@register.filter("blipify")
def blipify(value):
    value = tag_phrase.sub('#<a class="tagged" href="http://blip.pl/tags/\\1">\\1</a>', value)
    return value

