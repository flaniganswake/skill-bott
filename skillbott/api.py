''' API implentation '''
from collections import OrderedDict
from django.shortcuts import get_object_or_404
from rest_framework.authentication import (
    BasicAuthentication, SessionAuthentication)
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.decorators import (
    api_view, authentication_classes, permission_classes)
from rest_framework.reverse import reverse
from rest_framework import status, viewsets
import serializers
from orm.models import (Answer, Category, Choice, Inventory, Topic, User)


@api_view(('POST',))
def auth_user(request, format=None):
    content = {
        'user': str(request.user),  # `django.contrib.auth.User` instance.
        'auth': str(request.auth),  # None
    }
    return Response(content)


@api_view(('GET',))
@authentication_classes((SessionAuthentication, BasicAuthentication))
@permission_classes((IsAuthenticated,))
def api_root(request, format=None):
    links = OrderedDict({})
    links['Inventories'] = \
        request.build_absolute_uri(reverse('api.inventory-list'))
    links['Categories'] = \
        request.build_absolute_uri(reverse('api.category-list'))
    links['Topics'] = \
        request.build_absolute_uri(reverse('api.topic-list'))
    links['Choices'] = \
        request.build_absolute_uri(reverse('api.choice-list'))
    links['Answers'] = \
        request.build_absolute_uri(reverse('api.answer-list'))
    links['Scores'] = \
        request.build_absolute_uri(reverse('api.scores-list'))
    links['Post Answer'] = \
        request.build_absolute_uri(reverse('api.answer-create'))
    # links['Auth User'] = \
    #     request.build_absolute_uri(reverse('api.auth-user'))
    links['Register User'] = \
        request.build_absolute_uri(reverse('api.register'))
    links['Gameplan Test'] = \
        request.build_absolute_uri(reverse(
            'api.inventory-list') + '?tag=gameplan')
    return Response(links)


@api_view(['POST'])
@authentication_classes((SessionAuthentication,))
@permission_classes((IsAuthenticated,))
def register(request):
    VALID_USER_FIELDS = [f.name for f in User._meta.fields]
    DEFAULTS = {"user_permissions": None, "groups": None}
    serialized = serializers.UserSerializer(data=request.DATA)
    if serialized.is_valid():
        user_data = {field: data for (field, data) in request.DATA.items()
                     if field in VALID_USER_FIELDS}
        user_data.update(DEFAULTS)
        user = User.objects.create_user(
            **user_data
        )
        return Response(serializers.UserSerializer(instance=user).data,
                        status=status.HTTP_201_CREATED)
    else:
        return Response(serialized._errors,
                        status=status.HTTP_400_BAD_REQUEST)


@authentication_classes((SessionAuthentication,))
@permission_classes((IsAuthenticated,))
class InventoryViewSet(viewsets.ReadOnlyModelViewSet):

    def list(self, request):
        self.queryset = Inventory.objects.all()
        tag = self.request.query_params.get('tag', None)
        if tag:
            inv_pks = set()
            cat_pks = set()
            topics = Topic.objects.filter(tags__name__contains=tag)
            for topic in topics:
                if topic.category.inventory.pk not in inv_pks:
                    inv_pks.add(topic.category.inventory.pk)
                if topic.category.pk not in cat_pks:
                    cat_pks.add(topic.category.pk)
            self.queryset = self.queryset.filter(pk__in=inv_pks)
            for inv in self.queryset:
                categories = Category.objects.filter(inventory__pk=inv.pk)
                categories = categories.filter(pk__in=cat_pks)
                for cat in categories:
                    cat.topics.set(topics.filter(category__pk=cat.pk))
                inv.categories = categories
        else:
            for inv in self.queryset:
                categories = Category.objects.filter(inventory__pk=inv.pk)
                for cat in categories:
                    cat.topics.set(Topic.objects.filter(category__pk=cat.pk))
                inv.categories.set(categories)
        serializer = serializers.InventorySerializer(
            self.queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        self.queryset = Inventory.objects.all()
        inventory = get_object_or_404(self.queryset, pk=pk)
        serializer = serializers.InventorySerializer(
            inventory, context={'request': request})
        return Response(serializer.data)


@authentication_classes((SessionAuthentication,))
@permission_classes((IsAuthenticated,))
class CategoryViewSet(viewsets.ReadOnlyModelViewSet):

    def list(self, request):
        self.queryset = Category.objects.all()
        tag = self.request.query_params.get('tag', None)
        if tag:
            cat_pks = set()
            topics = Topic.objects.filter(tags__name__contains=tag)
            for topic in topics:
                if topic.category.pk not in cat_pks:
                    cat_pks.add(topic.category.pk)
            self.queryset = self.queryset.filter(pk__in=cat_pks)
            for cat in self.queryset:
                cat.topics.set(topics.filter(category__pk=cat.pk))
        else:
            for cat in self.queryset:
                cat.topics.set(Topic.objects.filter(category__pk=cat.pk))
        serializer = serializers.CategorySerializer(
            self.queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        self.queryset = Category.objects.all()
        category = get_object_or_404(self.queryset, pk=pk)
        serializer = serializers.CategorySerializer(
            category, context={'request': request})
        return Response(serializer.data)


@authentication_classes((SessionAuthentication,))
@permission_classes((IsAuthenticated,))
class TopicViewSet(viewsets.ReadOnlyModelViewSet):

    def list(self, request):
        self.queryset = Topic.objects.all()
        tag = self.request.query_params.get('tag', None)
        if tag:
            self.queryset = self.queryset.filter(tags__name__contains=tag)
        else:
            self.queryset = Topic.objects.all()
        serializer = serializers.TopicSerializer(
            self.queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        self.queryset = Topic.objects.all()
        topic = get_object_or_404(self.queryset, pk=pk)
        serializer = serializers.TopicSerializer(
            topic, context={'request': request})
        return Response(serializer.data)


@authentication_classes((SessionAuthentication,))
@permission_classes((IsAuthenticated,))
class AnswerViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.AnswerSerializer

    def list(self, request):
        self.queryset = Answer.objects.all()
        serializer = serializers.AnswerSerializer(
            self.queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def create(self, request):
        VALID_ANSWER_FIELDS = [f.name for f in Answer._meta.fields]
        DEFAULTS = {}
        serialized = serializers.AnswerSerializer(data=request.DATA)
        if serialized.is_valid():
            answer_data = {field: data for (field, data)
                           in request.DATA.items() if field
                           in VALID_ANSWER_FIELDS}
            answer_data.update(DEFAULTS)
            user = Answer.objects.create_answer(
                **answer_data
            )
            return Response(serializers.AnswerSerializer(
                instance=answer_data), status=status.HTTP_201_CREATED)
        else:
            return Response(serialized._errors,
                            status=status.HTTP_400_BAD_REQUEST) 


@authentication_classes((SessionAuthentication,))
@permission_classes((IsAuthenticated,))
class ChoiceViewSet(viewsets.ModelViewSet):

    def list(self, request):
        self.queryset = Choice.objects.all()
        serializer = serializers.ChoiceSerializer(
            self.queryset, many=True, context={'request': request})
        return Response(serializer.data)

    def retrieve(self, request, pk=None):
        self.queryset = Choice.objects.all()
        choice = get_object_or_404(self.queryset, pk=pk)
        serializer = serializers.ChoiceSerializer(
            choice, context={'request': request})
        return Response(serializer.data)


@authentication_classes((SessionAuthentication,))
@permission_classes((IsAuthenticated,))
class ScoresViewSet(viewsets.ModelViewSet):

    def list(self, request):
        cat_pks = [cat.type for cat in Category.objects.all()]
        scores = dict.fromkeys(cat_pks)
        for key, value in scores.items():
            scores[key] = {'green': 0, 'yellow': 0}
        for answer in Answer.objects.all():  # unfiltered/all for now
            if answer.green >= 0:
                scores[answer.category.type]['green'] += answer.green
            if answer.yellow >= 0:
                scores[answer.category.type]['yellow'] += answer.yellow
        return Response({'scores': scores})


inventory_list = InventoryViewSet.as_view({
    'get': 'list',
})
inventory_detail = InventoryViewSet.as_view({
    'get': 'retrieve',
})
category_list = CategoryViewSet.as_view({
    'get': 'list',
})
category_detail = CategoryViewSet.as_view({
    'get': 'retrieve',
})
topic_list = TopicViewSet.as_view({
    'get': 'list',
})
topic_detail = TopicViewSet.as_view({
    'get': 'retrieve',
})
answer_list = AnswerViewSet.as_view({
    'get': 'list',
})
answer_create = AnswerViewSet.as_view({
    'post': 'create',
})
choice_list = ChoiceViewSet.as_view({
    'get': 'list',
})
choice_detail = ChoiceViewSet.as_view({
    'get': 'retrieve',
})
scores_list = ScoresViewSet.as_view({
    'get': 'list',
})