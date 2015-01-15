# -*- coding: utf-8 -*-
from django import template
from django.utils.datastructures import SortedDict


register = template.Library()


@register.simple_tag
def render_solr_field(field):
    # these are options supported by solr but not by haystack
    non_default_field_options = [
        ('multiValued', 'multi_valued'),
        ('omitNorms', 'omit_norms'),
        ('termVectors', 'term_vectors'),
        ('termPositions', 'term_positions'),
        ('termOffsets', 'term_offsets'),
    ]

    # use sorted dict to keep consistency
    attributes = SortedDict()
    attributes['name'] = field['field_name']
    attributes['type'] = field['type']
    attributes['indexed'] = field['indexed']
    attributes['stored'] = field['stored']

    for field_name, option in non_default_field_options:
        if option in field:
            attributes[field_name] = field[option]

    flat = ''.join(' {0}="{1}"'.format(*attrs) for attrs in attributes.items())
    return '<field {}/>'.format(flat)
