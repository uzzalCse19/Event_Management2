# templatetags/month_filters.py
from django import template

register = template.Library()

@register.filter
def month_name(month_num):
    months = {
        1: "January", 2: "February", 3: "March", 4: "April",
        5: "May", 6: "June", 7: "July", 8: "August",
        9: "September", 10: "October", 11: "November", 12: "December"
    }
    return months.get(month_num, "")