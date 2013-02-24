from django.conf.urls.defaults import *


urlpatterns = patterns('',

    # ----- Public pages -----

    url(r'^$',
        view='doccomment.views.pub_list',
        name='doccomment_pub_list',
    ),

    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/$',
        view='doccomment.views.pub_view_latest',
        name='doccomment_pub_view_latest',
    ),

    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/(?P<ver>\d+\.\d+\.\d+)/$',
        view='doccomment.views.pub_view',
        name='doccomment_pub_view',
    ),

    url(r'^(?P<id>\d+)/(?P<slug>[\w-]+)/(?P<ver>\d+\.\d+\.\d+)/c(?P<pos>\d+)/$',
        view='doccomment.views.pub_view_comment',
        name='doccomment_pub_comment',
    ),

    # ----- Authors' pages -----

    url(r'^draft/list/$',
        view='doccomment.views.draft_list',
        name='doccomment_draft_list',
    ),

    url(r'^draft/new/$',
        view='doccomment.views.draft_new',
        name='doccomment_draft_new',
    ),

    url(r'^draft/(?P<id>\d+)/edit/$',
        view='doccomment.views.draft_edit',
        name='doccomment_draft_edit',
    ),

    url(r'^draft/(?P<id>\d+)/preview/$',
        view='doccomment.views.draft_preview',
        name='doccomment_draft_preview',
    ),

    url(r'^draft/(?P<id>\d+)/publish/(?P<ver>\d+\.\d+\.\d+)/$',
        view='doccomment.views.draft_publish',
        name='doccomment_draft_publish',
    ),

    # ----- AJAX only -----

    url(r'^ajax/get-comment-count/(?P<v_id>\d+)/$',
        view='doccomment.views.ajax_get_comment_count',
        name='doccomment_ajax_get_comment_count',
    ),
    url(r'^ajax/get-parser-preview/$',
        view='doccomment.views.ajax_get_parser_preview',
        name='doccomment_ajax_get_parser_preview',
    ),
)
