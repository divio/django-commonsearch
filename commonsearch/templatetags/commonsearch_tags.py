# -*- coding: utf-8 -*-
from django import template
from django.utils.datastructures import SortedDict


register = template.Library()


@register.simple_tag
def render_solr_field(field):
    # use sorted dict to keep consistency
    attributes = SortedDict()
    attributes['name'] = field['field_name']
    attributes['type'] = field['type']
    attributes['indexed'] = field['indexed']
    attributes['stored'] = field['stored']
    attributes['multiValued'] = field['multi_valued']
    attributes['omitNorms'] = field['omit_norms']
    attributes['termVectors'] = field['term_vectors']
    attributes['termPositions'] = field['term_positions']
    attributes['termOffsets'] = field['term_offsets']

    flat = ''.join(' {0}="{1}"'.format(*attrs) for attrs in attributes.items())
    return '<field {}/>'.format(flat)
