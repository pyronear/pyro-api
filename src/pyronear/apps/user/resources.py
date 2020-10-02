from tastypie.resources import ModelResource
from tastypie.authorization import Authorization
from pyronear.apps.user.models import User


class UserResource(ModelResource):
    class Meta:
        queryset = User.objects.all()
        resource_name = 'user'
        authorization = Authorization()
        fields = ['username']
