from django.conf.urls.defaults import *

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
                       (r'^incoming_connection$','services.views.incoming_connection'), 
                       (r'^end_connection$','services.views.end_call'),
                       (r'^register_agent','services.views.agent_registration'),
                       (r'^unregister_agent','services.views.agent_unregistration'),
                       (r'^static/(?P<static_resource>.*)$','services.views.get_static_media'),
                       (r'^agent_phono','services.views.agent_client'),
                       (r'^agent_phone','services.views.phone_client'),
                       
                                                                      
    # Example:
    # (r'^cc_vector_webservices/', include('cc_vector_webservices.foo.urls')),

    # Uncomment the admin/doc line below and add 'django.contrib.admindocs' 
    # to INSTALLED_APPS to enable admin documentation:
    # (r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    # (r'^admin/', include(admin.site.urls)),
)
