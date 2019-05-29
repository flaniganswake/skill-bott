from rest_framework import serializers
from taggit.models import Tag
from orm.models import *


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User


class TagListSerializer(serializers.ModelSerializer):

    class Meta:
        model = Tag
        fields = ('name',)


class ChoiceSerializer(serializers.ModelSerializer):

    class Meta:
        model = Choice
        fields = ('text', 'hover', 'inventory')


class TopicSerializer(serializers.ModelSerializer):
    tags = serializers.StringRelatedField(many=True)

    class Meta:
        model = Topic
        fields = ('pk', 'name', 'hover', 'name2', 'hover2', 'tags', 'category')


class CategorySerializer(serializers.ModelSerializer):
    topics = TopicSerializer(many=True, read_only=True)

    class Meta:
        model = Category
        fields = ('pk', 'type', 'hover', 'inventory', 'topics', 'inventory')


class InventorySerializer(serializers.ModelSerializer):
    categories = CategorySerializer(many=True, read_only=True)
    yellow_choices = ChoiceSerializer(many=True, read_only=True)
    green_choices = ChoiceSerializer(many=True, read_only=True) 

    class Meta:
        model = Inventory
        fields = ('pk', 'type', 'title', 'tagline', 'description', 'instructions',
                  'yellow_choices', 'green_choices', 'categories')


class AnswerSerializer(serializers.ModelSerializer):

    class Meta:
        model = Answer
        fields = ('yellow', 'green', 'other', 'user', 'topic', 'category', 'inventory')


class ScoresSerializer(serializers.Serializer):
    data = {'green_scores', 'yellow_scores'}
