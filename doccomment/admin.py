from django.contrib import admin

from .models import CommentStatus, Document, DocumentElement, DocumentVersion


class CommentStatusAdmin(admin.ModelAdmin):
    raw_id_fields = ['comment']


class DocumentAdmin(admin.ModelAdmin):
    raw_id_fields = ['author']


class DocumentElementAdmin(admin.ModelAdmin):
    raw_id_fields = ['parent']


class DocumentVersionAdmin(admin.ModelAdmin):
    raw_id_fields = ['author', 'document']


admin.site.register(CommentStatus, CommentStatusAdmin)
admin.site.register(Document, DocumentAdmin)
admin.site.register(DocumentElement, DocumentElementAdmin)
admin.site.register(DocumentVersion, DocumentVersionAdmin)
