# -*- coding: utf-8 -*-
import os
import sys
from optparse import make_option

from django.conf import settings
from django.core.management import BaseCommand

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
            default=['dev'],
        ),
    )
    option_list = BaseCommand.option_list + base_options

    def handle(self, *args, **options):
        for backend in settings.HAYSTACK_CONNECTIONS:
            for stage in options['stages']:
                filename = self.get_output_file_path(stage)
                schema_xml = self.build_template(using=backend)
                self.write_file(filename, schema_xml)

    def get_language(self, stage):
        return language_from_alias(stage) or settings.LANGUAGE_CODE

    def get_output_file_path(self, stage):
        from deployment import project_name

        output_folder = 'tmp/%(project)s-%(stage)s-%(language)s' % {
            'project': project_name,
            'stage': stage,
            'language': self.get_language(stage)
        }
        project_root = os.path.join(settings.PROJECT_ROOT, output_folder)
        if not os.path.isdir(project_root):
            os.makedirs(project_root)
        return os.path.join(project_root, 'schema.xml')

    def build_context(self, using):
        context = super(Command, self).build_context(using)
        context['current_language'] = self.get_language(using)
        return context
