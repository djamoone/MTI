
from abc import ABC, abstractmethod


# Abstract Interface
class NotificationService(ABC):

    @abstractmethod
    def send(self, message):
        pass


# Concrete Implementations
class EmailService(NotificationService):

    def send(self, message):
        print(f"Sending email: {message}")


class SMSService(NotificationService):

    def send(self, message):
        print(f"Sending SMS: {message}")


class PushService(NotificationService):

    def send(self, message):
        print(f"Sending Push Notification: {message}")


# High-Level Module
class Notification:

    def __init__(self, service: NotificationService):
        self.service = service

    def send(self, message):
        self.service.send(message)


# Main
if __name__ == "__main__":

    # Email Notification
    email_service = EmailService()
    notification = Notification(email_service)
    notification.send("Hello via Email!")

    # SMS Notification
    sms_service = SMSService()
    notification = Notification(sms_service)
    notification.send("Hello via SMS!")

    # Push Notification
    push_service = PushService()
    notification = Notification(push_service)
    notification.send("Hello via Push!")
