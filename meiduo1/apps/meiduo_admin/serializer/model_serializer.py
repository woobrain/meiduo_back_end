from rest_framework.serializers import Serializer,ModelSerializer

from apps.user.models import User


class UserSerializer(ModelSerializer):


    class Meta:
        model = User
        fields = ('id','username','mobile','email','password')

        extra_kwargs = {
            'username': {
                'max_length': 20,
                'min_length': 5
            },
            'password': {
                'max_length': 20,
                'min_length': 8,
                'write_only': True
            }
        }

    def create(self, validated_data):

        return User.objects.create_user(**validated_data)




