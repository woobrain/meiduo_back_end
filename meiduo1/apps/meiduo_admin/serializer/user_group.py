from rest_framework import serializers
from django.contrib.auth.models import Group, Permission


class UserGroupSerializer(serializers.ModelSerializer):

    class Meta:
        model = Group
        fields = '__all__'


class GroupPerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Permission
        fields = '__all__'