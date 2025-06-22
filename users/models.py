from django.db import models
from django.contrib.auth.models import AbstractUser #  for extending the base User model

from django_rest_passwordreset.signals import reset_password_token_created
from django.dispatch import receiver
from django.urls import reverse
from django.template.loader import render_to_string
from django.core.mail import EmailMultiAlternatives  # Send mails with attachments
from django.utils.html import strip_tags


# Create your models here.
class CustomUser(AbstractUser):
    email = models.EmailField(max_length=200, unique=True)
    birthday = models.DateField(null=True, blank=True)
    REQUIRED_FIELDS = ['email']

# Trigger when a reset password token is created
@receiver(reset_password_token_created)
def password_reset_token_created(reset_password_token, *args, **kwargs):
    # sitelink = "http://localhost:5173/"
    sitelink = "https://lecturer-management-frontend.onrender.com/"
    token = "{}".format(reset_password_token.key)
    full_link = f"{sitelink}password_reset/{token}"
    context = {
        "full_link": full_link,
        'email_address': reset_password_token.user.email
    }
    # Render the email template
    html_message = render_to_string("backend/email.html", context=context)
    # Clear all HTML tags in the template
    plain_message = strip_tags(html_message)
    
    msg = EmailMultiAlternatives(
        subject="Request Resetting Password for {title}".format(title=reset_password_token.user.email),
        body=plain_message,
        from_email='your_email@example.com',
        to=[reset_password_token.user.email],
    )
    # Attach the HTML content to the email
    msg.attach_alternative(html_message, "text/html")
    msg.send()