# -*- coding: utf-8 -*-
import os
import shutil
import sys
from optparse import make_option

from django.conf import settings
from django.core.management import BaseCommand
from django.template import Context, Template
from django.template.loader import find_template
from django.utils.translation import override as force_language

from haystack.management.commands.build_solr_schema import Command as BuildSolrSchemaCommand


try:
    from aldryn_search.utils import language_from_alias
except ImportError:
    from ...utils import language_from_alias

# hack to import deployment.py file :(
sys.path.append(settings.PROJECT_ROOT)

DEFAULT_PATH = os.path.join(os.path.dirname(__file__), '../../conf/solr/core')

CORE_OUTPUT_FORMAT = getattr(settings, 'COMMONSEARCH_SOLR_CORE_OUTPUT_FORMAT', '%(project)s-%(stage)s-%(language)s')

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
        make_option(
            "-f",
            "--format",
            action="store",
            default=CORE_OUTPUT_FORMAT,
            type="string",
            dest="format",
        ),
        make_option(
            "-u",
            "--using",
            action="append",
            dest="using",
            default=[],
        ),
    )
    option_list = BaseCommand.option_list + base_options

    def handle(self, *args, **options):
        backends = options.get('using') or settings.HAYSTACK_CONNECTIONS.keys()
        stages = options.get('stages') or ['dev']

        for backend in backends:
            for stage in stages:
                self.build_core(backend, stage, **options)

    def get_language(self, stage):
        return language_from_alias(stage) or settings.LANGUAGE_CODE

    def build_core(self, backend, stage, **options):
        from deployment import project_name

        language = self.get_language(backend)

        core_name_format = options['format']

        core_name = core_name_format % {
            'project': project_name,
            'stage': stage,
            'language': language,
        }

        core_root = os.path.join(settings.PROJECT_ROOT, 'tmp', core_name)

        with force_language(language):
            core_conf_root = self.build_conf(core_root, language)

            schema_xml = self.build_template(using=backend)
            schema_xml_path = os.path.join(core_conf_root, 'schema.xml')
            self.write_file(schema_xml_path, schema_xml)

    def build_conf(self, core_path, language):
        if os.path.exists(SOLR_TEMPLATES_ROOT):
            if os.path.isdir(core_path):
                shutil.rmtree(core_path)
            shutil.copytree(SOLR_TEMPLATES_ROOT, core_path)

        conf_path = os.path.join(core_path, 'conf/')

        if not os.path.isdir(conf_path):
            os.makedirs(conf_path)

        solr_config_path = os.path.join(core_path, conf_path, 'solrconfig.xml')

        if os.path.exists(solr_config_path):
            # nasty but needed when some options like highlighting
            # are language dependant
            context = Context({'language': language})

            with open(solr_config_path) as solr_config_file:
                solr_config_template = Template(solr_config_file.read())
                solr_config = solr_config_template.render(context)

            self.write_file(solr_config_path, solr_config)
        return conf_path

    def build_context(self, using):
        context = super(Command, self).build_context(using)
        context['language'] = self.get_language(using)
        return context
