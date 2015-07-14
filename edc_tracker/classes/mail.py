from django.core.mail import send_mail, send_mass_mail, EmailMessage
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.models import User


class Reciever(object):

    def __init__(self, *args, **kwargs):
        self._from = None
        self._to = None
        self._cc = ['tsetsiba@bhp.org.bw']
        self._bbc = []
        self._sender = None
        self._subject = None
        self._message = None
        self._recepient_list = []
        self._attachments = None

    @property
    def mail_from(self):
        return 'django@bhp.org.bw'

    @property
    def mail_to(self):
        self._to = 'tsetsiba@bhp.org.bw'
        return self._to

    @property
    def mail_cc(self):
        return self._cc

    @property
    def subject(self):
        self._subject = "<strong>Pima VL Stats</strong>"
        return self._subject

    @property
    def message(self):
        """ """
        self._message = "<p>Good Day Team.</p><br>Consider preparing the proposal using a single author or a team. It"
        " is a lot of work for one person, who needs to have all the required skills. Using multiple"
        " authors spreads theworkload, but requires careful control, communication, collaboration and proposal editing<br></p>"
        return self._message

    @property
    def footer(self):
        """EDC"""
        return ""

    @property
    def recipent_list(self):
        """ A list of strings, each an email address."""
        for user in User.objects.filter(groups__name='field_supervisor'):
            if user.email == 'tsetsiba@bhp.org.bw':
                self._recepient_list.append(user.email)
        return self._recepient_list

    @property
    def mail_bcc(self):
        """ blind carbon copy"""
        #self._bbc.append('ckgathi@bhp.org.bw')
        #self._bbc.append('opharatlhatlhe@bhp.org.bw')
        return self._bbc


class Mail(object):

    def __init__(self, receiver=None, *args, **kwargs):
        self.receiver = receiver

    def send_mail_with_cc_or_bcc(self):
        """ Send email including cc and bcc."""
        return EmailMessage(self.receiver.subject, self.receiver.message, self.receiver.mail_from,\
               self.receiver.recipent_list, self.receiver.mail_bcc, headers={"Cc": ','.join(self.receiver.mail_cc)}).send(fail_silently=False)

    def send_mail_with_cc_or_bcc_alt(self):
        """ """
        msg = EmailMultiAlternatives(self.receiver.subject, self.receiver.message, self.receiver.mail_from,\
               self.receiver.recipent_list, self.receiver.mail_bcc, headers={"Cc": ','.join(self.receiver.mail_cc)}).send(fail_silently=False)
        msg.content_subtype = "html"
        return msg.send()

    def send_mail(self):
        """ Send email without cc and bcc."""
        return send_mail(self.receiver.subject, self.receiver.message, self.receiver.mail_from, self.receiver.recipent_list)

    def send_mass_mail(self):
        """ is intended to handle mass emailing or send multiple emails using a single connection."""
        datatuple = (
            (self.receiver.subject, "Testing EDC Test Server", self.receiver.mail_from, self.receiver.recipent_list),
            (self.receiver.subject, "Testing EDC", self.receiver.mail_from, self.receiver.recipent_list),
        )
        return send_mass_mail(datatuple)

    def attach_file(self, file_path, *args, **kwargs):
        """ Override this method to attach files to """
        return self.send_mail().attach_file(file_path)


class Attachment(object):

    def __init__(self):
        self.filename = None
        self.content = None
        self.mimetype = None

    def attach_document(self):
        pass
