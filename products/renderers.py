from rest_framework.renderers import BrowsableAPIRenderer
from .forms import ProductCreateForm

class CustomBrowsableAPIRenderer(BrowsableAPIRenderer):
    def get_context(self, data, accepted_media_type, renderer_context):
        context = super().get_context(data, accepted_media_type, renderer_context)
        
        if renderer_context['request'].method in ('POST', 'PUT', 'PATCH'):
            context['form'] = ProductCreateForm()
            context['display_edit_forms'] = True
        
        return context