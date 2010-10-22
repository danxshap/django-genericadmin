from django.shortcuts import render_to_response
from django.http import Http404, HttpResponse
from django.template import Context, Template

from django.contrib.contenttypes.models import ContentType

JSON_TEMPLATE = '''[{% for obj in objects %}{"contentTypeId":"{{ obj.content_type_id }}","contentTypeText":"{{ obj.content_type_text }}","objectId":"{{ obj.object_id }}","objectText":"{{ obj.object_text }}"}{% if not forloop.last %},{% endif %}{% endfor %}]'''

def get_obj(content_type_id, object_id):
    content_type = ContentType.objects.get(pk=content_type_id)
    try:
        obj = content_type.get_object_for_this_type(pk=object_id)
    except:
        obj = None
    content_type_text = unicode(content_type)

    if obj:
        object_text = unicode(obj)
    else:
        object_text = ""
    return {
        'content_type_text': content_type_text,
        'content_type_id': content_type_id,
        'object_text': object_text,
        'object_id': object_id
    }

def generic_lookup(request):
    if request.method == 'GET':
        objects = []
        if request.GET.has_key('content_type') and request.GET.has_key('object_id'):
            obj = get_obj(request.GET['content_type'], request.GET['object_id'])
            objects = (obj, )
        elif request.GET.has_key('lookup'):
            objs = eval(request.GET['lookup'])
            for obj in objs:
                objects.append(get_obj(obj[0], obj[1]))
        if objects:
            t = Template(JSON_TEMPLATE)
            c = Context({'objects': objects})
            ret = t.render(c)
            return HttpResponse(ret, mimetype='application/json')

def get_generic_rel_list(request):
    return_string = "{"
    for c in ContentType.objects.all().order_by('id'):
        return_string = '%s"%d": "%s/%s",' % (return_string, c.id, c.app_label, c.model)
    return_string = "%s}" % return_string[:-1]
    return HttpResponse(return_string, mimetype='application/json')
