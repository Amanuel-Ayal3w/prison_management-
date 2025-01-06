# templatetags/notification_tags.py
from django import template
from ..models import Notification

register = template.Library()

@register.inclusion_tag('notifications/notification_list.html', takes_context=True)
def show_notifications(context):
    request = context['request']
    notifications = Notification.objects.filter(user=request.user, is_read=False)
    num_unread_notifications = notifications.filter(is_read=False).count()
    return {'notifications': notifications,'num_unread_notifications': num_unread_notifications}
