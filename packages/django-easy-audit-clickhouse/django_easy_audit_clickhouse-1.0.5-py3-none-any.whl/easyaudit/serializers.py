from rest_framework import serializers


class CRUDEventSerializer(serializers.Serializer):
    event_type = serializers.IntegerField(read_only=True)
    object_id = serializers.CharField(read_only=True, default="")
    object_repr = serializers.CharField(read_only=True, default="")
    object_json_repr = serializers.CharField(read_only=True, default="")
    changed_fields = serializers.CharField(read_only=True, default="")
    user_id = serializers.SerializerMethodField(read_only=True)
    user_pk_as_string = serializers.SerializerMethodField(read_only=True)
    created_at = serializers.SerializerMethodField(read_only=True)

    def get_user_id(self, obj):
        return str(obj.user_id) if obj.user_id else ""

    def get_user_pk_as_string(self, obj):
        return str(obj.user_pk_as_string) if obj.user_pk_as_string else ""

    def get_created_at(self, obj):
        return obj.created_at


class LoginEventSerializer(serializers.Serializer):
    login_type = serializers.IntegerField(read_only=True)
    username = serializers.CharField(read_only=True, default="")
    user_id = serializers.SerializerMethodField(read_only=True)
    remote_ip = serializers.CharField(read_only=True, default="")
    created_at = serializers.SerializerMethodField(read_only=True)

    def get_user_id(self, obj):
        return str(obj.user_id) if obj.user_id else ""

    def get_created_at(self, obj):
        return obj.created_at
