# -*- coding: utf-8 -*-
import os
import shutil
import sys
from optparse import make_option

from django.conf import settings
from django.core.management import BaseCommand
from django.template.loader import find_template

from haystack.management.commands.build_solr_schema import Command as BuildSolrSchemaCommand

from aldryn_search.utils import language_from_alias

sys.path.append(settings.PROJECT_ROOT)


class Command(BuildSolrSchemaCommand):
    can_import_settings = True
    base_options = (
        make_option(
            "-s",
            "--stage",
            action="append",
            type="string",
            dest="stages",
        ),
    )
    option_list = BaseCommand.option_list + base_options

    def handle(self, *args, **options):
        stages = options.get('stages', ['dev'])
        for backend in settings.HAYSTACK_CONNECTIONS:
            for stage in stages:
                schema_xml = self.build_template(using=backend)
                self.build_core(backend, stage, schema_xml)

    def get_language(self, stage):
        return language_from_alias(stage) or settings.LANGUAGE_CODE

    def build_core(self, backend, stage, schema_xml):
        from deployment import project_name

        output_folder = 'tmp/%(project)s-%(stage)s-%(language)s' % {
            'project': project_name,
            'stage': stage,
            'language': self.get_language(backend)
        }
        core_root = os.path.join(settings.PROJECT_ROOT, output_folder)
        if not os.path.isdir(core_root):
            os.makedirs(core_root)

        core_conf_root = self.build_conf(core_root)

        schema_xml_path = os.path.join(core_conf_root, 'schema.xml')
        self.write_file(schema_xml_path, schema_xml)

    def build_conf(self, core_path):
        conf_files = [
            'protwords.txt',
            'solrconfig.xml',
            'stopwords.txt',
            'synonyms.txt'
        ]
        conf_path = os.path.join(core_path, 'conf/')
        if not os.path.isdir(conf_path):
            os.makedirs(conf_path)

        for filename in conf_files:
            template_name = os.path.join('commonsearch/solr_core_template/conf', filename)
            template = find_template(template_name)[0]
            shutil.copy(template.origin.name, os.path.join(conf_path, filename))
        return conf_path

    def build_context(self, using):
        context = super(Command, self).build_context(using)
        context['current_language'] = self.get_language(using)
        return context
