import jinja2

from mail.impl import sandinblue_service


def render_mail(template_name, **template_vars):
    env = jinja2.Environment(
        loader=jinja2.PackageLoader('mail', 'templates')
    )
    template = env.get_template(template_name)
    return template.render(**template_vars)


def send(to, name, content, subject="IsraelWay team", _tags=None, sender=None, cc=None, attachments=None):
    sandinblue_service.send(to, name, content, subject, _tags, sender, cc=cc, attachments=attachments)

