from django.shortcuts import render_to_response
from django.shortcuts import get_object_or_404
from django.template import RequestContext
from django.core.urlresolvers import reverse
from django.views.generic import list_detail
from django.contrib.auth.decorators import user_passes_test
from django.http import Http404
from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.http import HttpResponseRedirect
from django.core.exceptions import SuspiciousOperation
from django.contrib.comments.models import Comment
from django.utils import simplejson
from django.conf import settings

from models import Document
from models import DocumentVersion
from models import DocumentElement
from forms import DocumentForm

# Get class to use for checking user permissions
from doccomment import get_permission_class
Permission = get_permission_class()
# Get class for parsing author input to HTML
from doccomment import get_parser_module
Parser = get_parser_module()


@user_passes_test(Permission.user_can_view_published)
def ajax_get_comment_count(request, v_id):
    version = get_object_or_404(DocumentVersion, pk=v_id)
    document = version.document

    # XHR calls only, unless in DEBUG mode
    if not request.is_ajax() and not settings.DEBUG:
        return HttpResponseForbidden('Are you lost?')

    # for each page element, get number of comment;
    page_elem = [{} for i in xrange(version.elem_count)]
    for de in version.documentelement_set.all():
        elem = page_elem[de.position]
        elem['id'] = de.position
        # TODO: handle comment count under DocumentElementManager (+cache)
        elem['ccount'] = Comment.objects.for_model(de).count()
        elem['url'] = reverse('doccomment_pub_comment', kwargs={
            'id': document.id,
            'slug': document.slug,
            'ver': version.version_string,
            'pos': de.position,
        })

    # prepare output data
    data = {
        'version_id': version.id,
        'elemCount': version.elem_count,
        'pageElements': page_elem,
    }

    # print out JSON for non-XHR calls in DEBUG mode.
    if not request.is_ajax() and settings.DEBUG:
        return HttpResponse("<pre>%s</pre>" % (simplejson.dumps(data, sort_keys=True, indent=4)))
    else:
        return HttpResponse(simplejson.dumps(data), 'application/json')


@user_passes_test(Permission.user_is_author)
def ajax_get_parser_preview(request):
    if not request.is_ajax() and not settings.DEBUG:
        return HttpResponseForbidden('Are you lost?')
    rendered = 'Johnny: "Need input!"'
    if request.POST:
        processed = Parser.parse(request.POST.get('data'))
    return HttpResponse(processed)


@user_passes_test(Permission.user_can_view_published)
def pub_list(request, template_name='doccomment/pub_list.html'):
    return render_to_response(template_name, {
        'doc_list': Document.objects.published(),
    }, context_instance=RequestContext(request))


# shortcut to pub_view with latest version. permission check on pub_view
def pub_view_latest(request, id, slug):
    doc = get_object_or_404(Document.objects.published(), pk=id)
    return pub_view(request, id, slug, doc.latest_version)


@user_passes_test(Permission.user_can_view_published)
def pub_view(request, id, slug, ver, template_name='doccomment/pub_view.html'):
    # slug is ignored
    dv = get_object_or_404(DocumentVersion,
        document=id,
        version_string=ver,
    )
    return render_to_response(template_name, {
        'version': dv,
    }, context_instance=RequestContext(request))


@user_passes_test(Permission.user_can_view_published)
def pub_view_comment(request, id, slug, ver, pos, template_name='doccomment/pub_comment.html'):
    version = get_object_or_404(DocumentVersion,
        document=id,
        version_string=ver,
    )
    element = get_object_or_404(version.documentelement_set, position=pos)
    url = reverse('doccomment_pub_view', kwargs={'id': id, 'slug': slug, 'ver': ver})
    return render_to_response(template_name, {
        'element': element,
        'version': version,
        'origin': "%s#DE-%s" % (url, pos),
    }, context_instance=RequestContext(request))


@user_passes_test(Permission.user_can_view_draft)
def draft_list(request, template_name='doccomment/draft_list.html'):
    return render_to_response(template_name, {
        'draft_list': Document.objects.all(),
    }, context_instance=RequestContext(request))


@user_passes_test(Permission.user_can_view_draft)
def draft_preview(request, id, template_name='doccomment/draft_preview.html'):
    return render_to_response(template_name, {
        'draft': get_object_or_404(Document, pk=id),
    }, context_instance=RequestContext(request))


@user_passes_test(Permission.user_is_author)
def draft_new(request, template_name='doccomment/doc_editor.html'):
    if request.method == 'POST':
        form = DocumentForm(request.POST)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.author = request.user
            doc.save()
            if request.POST.get('save-and-continue', None):
                url = reverse('doccomment_draft_edit', kwargs={'id': doc.id})
            else:
                url = reverse('doccomment_draft_list')
            # TODO: use django-messages to display "saved" message
            return HttpResponseRedirect(url)
    else:
        form = DocumentForm()
    return render_to_response(template_name, {
        'form': form,
    }, context_instance=RequestContext(request))


@user_passes_test(Permission.user_is_author)
def draft_edit(request, id, template_name='doccomment/doc_editor.html'):
    doc = get_object_or_404(Document, pk=id)
    if doc.author != request.user and not Permission.user_is_editor(request.user):
        return HttpResponseForbidden('You can only edit documents you created')
    if request.method == 'POST':
        form = DocumentForm(request.POST, instance=doc)
        if form.is_valid():
            doc = form.save(commit=False)
            doc.has_modification = True
            doc.save()
            if request.POST.get('save-and-continue', None):
                url = reverse('doccomment_draft_edit', kwargs={'id': doc.id})
            else:
                url = reverse('doccomment_draft_list')
            # TODO: use django-messages to display "saved" message
            return HttpResponseRedirect(url)
    else:
        form = DocumentForm(instance=doc)
    return render_to_response(template_name, {
        'form': form,
        'document': doc,
    }, context_instance=RequestContext(request))


@user_passes_test(Permission.user_is_author)
def draft_publish(request, id, ver):
    doc = get_object_or_404(Document, pk=id)
    if doc.author != request.user and not Permission.user_is_editor(request.user):
        return HttpResponseForbidden('You can only publish documents you created')
    if not ver in doc.next_version_choices:
        raise SuspiciousOperation
    pass

    # parse user input to HTML
    elements = Parser.parse_elements(doc.body)

    # create a snapshot of document as DocumentVersion
    dv = DocumentVersion(
        document=doc,
        title=doc.title,
        body=doc.body,
        author=doc.author,
        rendered="\n".join(elements),
        elem_count=len(elements),
        version_string=ver,
    )
    dv.save()

    # create records for each document elements
    for seq, txt in enumerate(elements):
        dv.documentelement_set.create(
            position=seq,
            text=txt,
        )

    # update version info in Document
    doc.published = True
    doc.date_published = dv.date_published
    doc.latest_version = dv.version_string
    doc.has_modification = False
    doc.save()

    # redirect to referring view, or fallback to preview page
    default_url = reverse('doccomment_draft_preview', kwargs={'id': doc.id})
    return HttpResponseRedirect(request.META.get('HTTP_REFERER', default_url))
