from django import template

register = template.Library()


@register.filter
def get_item(dictionary, key):
    """Dict dan kalit bo'yicha qiymat olish: dict|get_item:key"""
    if isinstance(dictionary, dict):
        return dictionary.get(key)
    return None
