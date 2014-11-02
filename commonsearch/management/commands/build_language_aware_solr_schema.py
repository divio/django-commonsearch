# -*- coding: utf-8 -*-
import os
import shutil
import sys
from optparse import make_option

from django.conf import settings
from django.core.management import BaseCommand
from django.template.loader import find_template
from django.utils.translation import override as force_language

from haystack.management.commands.build_solr_schema import Command as BuildSolrSchemaCommand

from aldryn_search.utils import language_from_alias

# hack to import deployment.py file :(
sys.path.append(settings.PROJECT_ROOT)

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), '../../conf/solr/core')

SOLR_TEMPLATES_ROOT = getattr(settings, 'COMMONSEARCH_SOLR_CORE_TEMPLATES_ROOT', DEFAULT_PATH)


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
        stages = options.get('stages') or ['dev']

        for backend in settings.HAYSTACK_CONNECTIONS:
            for stage in stages:
                self.build_core(backend, stage)

    def get_language(self, stage):
        return language_from_alias(stage) or settings.LANGUAGE_CODE

    def build_core(self, backend, stage):
        from deployment import project_name

        language = self.get_language(backend)

        output_folder = 'tmp/%(project)s-%(stage)s-%(language)s' % {
            'project': project_name,
            'stage': stage,
            'language': language,
        }
        core_root = os.path.join(settings.PROJECT_ROOT, output_folder)

        with force_language(language):
            core_conf_root = self.build_conf(core_root)

            schema_xml = self.build_template(using=backend)
            schema_xml_path = os.path.join(core_conf_root, 'schema.xml')
            self.write_file(schema_xml_path, schema_xml)

    def build_conf(self, core_path):
        conf_files = []

        if os.path.exists(SOLR_TEMPLATES_ROOT):
            if os.path.isdir(core_path):
                shutil.rmtree(core_path)
            shutil.copytree(SOLR_TEMPLATES_ROOT, core_path)
        else:
            conf_files = [
                'conf/protwords.txt',
                'conf/solrconfig.xml',
                'conf/stopwords.txt',
                'conf/synonyms.txt'
            ]

        conf_path = os.path.join(core_path, 'conf/')

        if not os.path.isdir(conf_path):
            os.makedirs(conf_path)

        for filename in conf_files:
            template_name = os.path.join('commonsearch/solr_core_template', filename)
            template = find_template(template_name)[0]
            shutil.copy(template.origin.name, os.path.join(conf_path, filename))
        return conf_path

    def build_context(self, using):
        context = super(Command, self).build_context(using)
        context['current_language'] = self.get_language(using)
        return context
