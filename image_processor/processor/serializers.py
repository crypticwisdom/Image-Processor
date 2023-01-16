from rest_framework import serializers
from account.models import ValidatorBlock


class ValidatorBlockSerializer(serializers.ModelSerializer):
    allowed_extensions = serializers.SerializerMethodField()
    content_type = serializers.SerializerMethodField()
    file_threshold_size = serializers.SerializerMethodField()
    image_dimension_threshold = serializers.SerializerMethodField()

    def get_allowed_extensions(self, obj):
        if obj:
            return [extension.extension_name for extension in obj.allowed_extensions.all()]
        return None

    def get_content_type(self, obj):
        if obj:
            return [content.content_name for content in obj.content_type.all()]
        return None

    def get_file_threshold_size(self, obj):
        if obj:
            return f"{obj.file_threshold_size} KB"
        return None

    def get_image_dimension_threshold(self, obj):
        if obj:
            return f"{obj.image_dimension_threshold} Pixels"
        return None

    class Meta:
        model = ValidatorBlock
        fields = ['id', 'block_name', 'block_token', 'file_threshold_size', 'image_dimension_threshold',
                  'allowed_extensions', 'content_type', 'numb_of_images_per_process', 'created_on']
