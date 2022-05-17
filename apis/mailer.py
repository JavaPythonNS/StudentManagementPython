
from django.conf import settings
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings

class Mailer:
    
    def __init__(self, **kwargs):
        self.email = kwargs.get("email", None)
        self.host = kwargs.get("host", "127.0.0.1")
        self.hash = kwargs.get("hash", None)
        self.type = kwargs.get("type", None)

    def __call__(self):
        if self.type =="Verify":
            return self.verify_email()
        else:
            return self.mail_send()

    def mail_send(self):
        template_name = "forgot_password.html"
        template_data = {
            "link":"http://"+self.host+"/api/v1/set_password/?q={}".format(self.hash)
        }
       
        html_content = render_to_string(template_name, template_data)
        text_context = strip_tags(html_content)
        msg = EmailMultiAlternatives("test", text_context, settings.EMAIL_HOST, [self.email])
        msg.attach_alternative(html_content, 'text/html')
        return True if msg.send() else False