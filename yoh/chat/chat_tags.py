# chat/templatetags/chat_tags.py
from django import template

register = template.Library()

@register.filter
def unread_messages(messages):
    return messages.filter(is_read=False)