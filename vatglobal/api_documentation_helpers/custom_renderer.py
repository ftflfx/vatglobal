import json

from django.http import JsonResponse
from rest_framework.schemas.openapi import SchemaGenerator


def custom_renderer_api(request):
    generator_class = SchemaGenerator
    generator = generator_class(
        url='',
        title='vatglobal Assessment API Documentation',
        description='',
        urlconf=None,
    )
    schema = generator.get_schema(request=None, public=True)

    for url in schema['paths']:
        for method in schema['paths'][url]:
            meta_description = schema['paths'][url][method]['description'].split('!')
            schema['paths'][url][method]['description'] = []
            schema['paths'][url][method]['tags'] = []
            for meta_objects in meta_description:
                meta_objects = meta_objects.replace('\n', '')
                if meta_objects != '':
                    meta_objects_json = json.loads(meta_objects)
                    key_name = list(meta_objects_json.keys())[0]

                    for meta_objects_json_value in meta_objects_json[key_name]:
                        try:
                            if type(schema['paths'][url][method][key_name]) == list:
                                schema['paths'][url][method][key_name] = schema['paths'][url][method][key_name] + \
                                                                         [meta_objects_json_value]

                            elif type(schema['paths'][url][method][key_name]) == dict:
                                schema['paths'][url][method][key_name][meta_objects_json_value] = \
                                    meta_objects_json[key_name][meta_objects_json_value]

                            elif type(schema['paths'][url][method][key_name]) == str:
                                if schema['paths'][url][method][key_name] == '':
                                    schema['paths'][url][method] = schema['paths'][url][method].pop(key_name, None)
                                else:
                                    schema['paths'][url][method][key_name] = str(meta_objects_json[key_name][0])
                        except KeyError:
                            schema['paths'][url][method][key_name] = []
                            for item in meta_objects_json[key_name]:
                                schema['paths'][url][method][key_name] = schema['paths'][url][method][key_name] + [item]

            if len(schema['paths'][url][method]['tags']) == 0:
                schema['paths'][url][method]['tags'] = ['General']

    return JsonResponse(data=schema)
