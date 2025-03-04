'''
https://stackoverflow.com/questions/60132733/django-include-templates-in-markdown
https://stackoverflow.com/questions/73807788/python-django-render-to-string-outpu-rendered-as-text-with-html-entities
'''
from django import template
from django.template.loader import render_to_string
from django.utils.safestring import mark_safe
import markdown as md

register = template.Library()

@register.simple_tag(takes_context=True)
def include_md(context, template_name):
    rendered = render_to_string(template_name, context={})
    return mark_safe(md.markdown(rendered))


'''
from django.template.defaultfilters import stringfilter
import markdown as md

@register.filter()
@stringfilter
def markdown(value):
    return md.markdown(value, extensions=['markdown.extensions.fenced_code'])

# https://docs.djangoproject.com/en/dev/howto/custom-template-tags/#code-layout
# https://learndjango.com/tutorials/django-markdown-tutorial
'''