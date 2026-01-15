
import re
from datetime import datetime

# Source - https://stackoverflow.com/a
# Posted by Mark, modified by community. See post 'Timeline' for change history
# Retrieved 2026-01-15, License - CC BY-SA 4.0
from wtforms.fields  import SelectField
from wtforms.widgets import Select, html_params
from markupsafe import Markup

from flask import session, url_for
from flask_paginate import Pagination


def get_locale():
    lang = session.get('lang', 'fr')
    return lang

def default_deadline():
    now = datetime.now()
    return f'{now.year}/12/31'

def paginate_items(items, page, per_page=10):
    offset = (page - 1) * per_page
    page_items = items[offset: offset + per_page]
    page_total = len(page_items)
    total = len(items)
    info = f'{offset+1} à {offset + page_total} résultats sur {total}'
    options = dict(page=page, per_page=per_page, total=total,
                   css_framework='bootstrap5', display_msg=info)
    return page_items, Pagination(**options)

def url_for_entry(entry, default='#'):
    if 'point' in entry:
        kwargs = entry.get('kwargs', {})
        return url_for(entry['point'], **kwargs)
    return entry.get('url', default)


class AttribSelect(Select):
    """
    Renders a select field that supports options including additional html params.

    The field must provide an `iter_choices()` method which the widget will
    call on rendering; this method must yield tuples of
    `(value, label, selected, html_attribs)`.
    """

    def __call__(self, field, **kwargs):
        kwargs.setdefault('id', field.id)
        if self.multiple:
            kwargs['multiple'] = True
        html = ['<select %s>' % html_params(name=field.name, **kwargs)]
        for val, label, selected, html_attribs in field.iter_choices():
            html.append(self.render_option(val, label, selected, **html_attribs))
        html.append('</select>')
        return Markup(''.join(html))


class AttribSelectField(SelectField):

    widget = AttribSelect()

    def iter_choices(self):
        for value, label, render_args in self.choices:
            yield (value, label, self.coerce(value) == self.data, render_args)

    def pre_validate(self, form):
         if self.choices:
             for v, _, _ in self.choices:
                 if self.data == v:
                     break
             else:
                 if self.data:
                    msg = f'{self.data} Is Not a valid choice for {self.id}'
                    raise ValueError(self.gettext(msg))
