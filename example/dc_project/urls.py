from django.conf import settings
from django.conf.urls.defaults import *
from django.contrib import admin


admin.autodiscover()

urlpatterns = patterns('',

    # Uncomment the next line to enable the admin:
    (r'^admin/', include(admin.site.urls)),

    # assign names to login/logout views
    url(r'^accounts/login/$',
        view='django.contrib.auth.views.login',
        name='auth_login',
    ),
    url(r'^accounts/logout/$',
        view='django.contrib.auth.views.logout',
        kwargs={'next_page': '/'},
        name='auth_logout',
    ),

    # django.contrib.comments
    (r'^comments/', include('django.contrib.comments.urls')),

    # redirect all other urls to doccomment
    (r'^', include('doccomment.urls')),
)

# serve static files if running DEBUG mode
if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^media/(?P<path>.*)$',
            view='django.views.static.serve',
            kwargs={
                'document_root': settings.MEDIA_ROOT,
                'show_indexes': True,
            },
        ),
    )
