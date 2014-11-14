django-commonsearch
===================

The idea behind this app is to provide common utilities for the creation and maintenance of solr based cores.
We should rename this app to something solr specific like haystack-solr-extensions.

## Disclaimer

This app was made with Divio's project setup in mind and makes no effort to adapt to others (even though it can be done).

## Usage

With this app you get a command called ```build_language_aware_solr_schema``` which is a ***replacement*** of haystack's
```build_solr_schema```, this is because haystack's has no concept of languages so it will always spit the same ```schema.xml``` file
regardless of language.

Also this command aims at standardizing the look and configuration of schema.xml files across projects.

```build_solr_schema``` will create one solr core per connection in your settings ```HAYSTACK_CONNECTIONS```.

What I mean by core is a folder with a ```conf``` subfolder and inside ```conf``` there will be a ```schema.xml``` and ```solrconfig.xml``` files.


The command takes one optional parameter ```-s``` or ```--stage``` which specifies which stage to prefix the core with, by default the core name is in the following format ```{project-name}-{stage}-{language}```, project name will come from the ```deployment.py``` file at the root of the project and language is calculated based on the connection alias using ```aldryn-search```.

There's two parts to this command, one is the ```schema.xml``` generation and the other is the core creation and placement.

### Assumptions
Before continuing any further, know that this command assumes two things:

-  You have a ```deployment.py``` in your project root.
- There's a ```tmp``` folder in your project root. This is the path where the cores will be created.

### Core creation
This app comes with a default solr core *template* which is what gets copied over to each core folder per connection,
this core template folder will literally be copied over using python's shutil.copytree function, the reason for this is to take the hassle away of creating a core folder manually with all necessary files and making sure they are all in sync, instead by following this approach we have a single core template that then is used to create the actual cores. The most important file inside a core is ```solrconfig.xml``` , this file tells solr all the needed handlers your core will need to process a request, sometimes this file may need to access the core language ie. vector highlighter, it is because of cases like this that this file is actually read into memory and processed with django's template engine to provide the ```{{ language }}``` context variable.
Sometimes you need a tighter and more customized solr core, for these cases you can define:

```python
COMMONSEARCH_SOLR_CORE_TEMPLATES_ROOT = "path/to/solr/custom/core/template
```

The setting above allows you to use your own solr core template folder when generating cores using ```build_language_aware_solr_schema```, the path specified needs to be ***absolute***.
When defining this you need to make sure your core template folder is structurally correct, this means that it has a ```./conf``` subfolder and inside of ```./conf``` a ```solrconfig.xml``` file. These requirements are not mine, they are solr's, failure to comply will result in a broken or ignored core.

Last, you might have noticed that the ```schema.xml``` file does not live in the core template folder, which brings us to the next section.

### Schema generation & placement
haystack's ```build_solr_schema``` will use django template loader to look for ```search_configuration/solr.xml``` in your ```TEMPLATES``` directories, so to not reinvent the wheel, the ```build_language_aware_solr_schema``` will look for this same file and like haystack's it will process it using django template system but with an additional ```{{ language }}``` context variable.

In order for haystack to use this app's custom solr.xml template, you ***need*** to put this app ***before*** haystack in your ```INSTALLED_APPS```, otherwise haystack will always load it's own ```solr.xml``` template.

Once the template has been rendered, we then create a ```schema.xml``` file inside the created core's conf folder with the rendered contents for each haystack connection.
