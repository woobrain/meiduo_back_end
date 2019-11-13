from rest_framework import serializers
# from django.contrib.auth.models import
from apps.user.models import User


class AdminSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = '__all__'
        extra_kwargs = {
            'username': {
                'max_length': 20,
                'min_length': 5
            },
            'password': {
                'max_length': 20,
                'min_length': 8,
                'write_only': True,
                'required':False
            }
        }

    def create(self, validated_data):
        user = super().create(validated_data)
        user.set_password(validated_data['password'])
        user.is_staff = True
        user.save()

        return user

    def update(self, instance, validated_data):
        instance = super().update(instance,validated_data)
        passwd = validated_data.get('password')
        if passwd:
            instance.set_password(passwd)
            instance.save()
        return instance