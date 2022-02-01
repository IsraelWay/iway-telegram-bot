from mail.impl import sandinblue_service


def send(to, name, content, subject="IsraelWay team", _tags=None, sender=None):
    sandinblue_service.send(to, name, content, subject, _tags, sender)

