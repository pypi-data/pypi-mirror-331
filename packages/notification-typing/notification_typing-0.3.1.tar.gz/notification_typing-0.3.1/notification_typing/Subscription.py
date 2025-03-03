from typing import TypedDict
from notification_typing.NotificationCondition import NotificationCondition
from notification_typing.NotificationType import NotificationType, valid_notification_type
from notification_typing.NotificationFrequency import NotificationFrequency, valid_notification_frequency
from notification_typing.NotificationConditionEvaluator import valid_condition
import logging

class Subscription(TypedDict):
    ticker: str
    notification_condition: NotificationCondition
    notification_type: NotificationType
    frequency: NotificationFrequency
    phone_number: str
    email: str

def valid_phone_number(phone_number) -> bool:
    import re
    pattern = r'^\+?(\d{1,3})?[-.\s]?\(?\d{1,4}\)?[-.\s]?\d{1,4}[-.\s]?\d{1,9}$'
    return re.match(pattern, phone_number) is not None

def valid_subscription(subscription: Subscription) -> tuple[bool, str]:
    logging.info(f"Validating subscription: {subscription}")
    if not valid_phone_number(subscription["phone_number"]):
        return False, f"Invalid phone number: {subscription['phone_number']}"
    elif not valid_notification_frequency(subscription["frequency"]):
        return False, f"Invalid notification frequency: {subscription['frequency']}"
    elif not valid_notification_type(subscription["notification_type"]):
        return False, f"Invalid notification type: {subscription['notification_type']}"
    elif not valid_condition(subscription["notification_condition"]):
        return False, f"Invalid condition type: {subscription['notification_condition']}"
    else:
        return True, "valid"
    