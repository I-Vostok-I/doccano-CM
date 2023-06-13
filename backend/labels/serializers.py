from rest_framework import serializers

from .models import BoundingBox, Category, Relation, Segmentation, Span, TextLabel, Trait
from examples.models import Example
from label_types.models import CategoryType, RelationType, SpanType, TraitType


class CategorySerializer(serializers.ModelSerializer):
    label = serializers.PrimaryKeyRelatedField(queryset=CategoryType.objects.all())
    example = serializers.PrimaryKeyRelatedField(queryset=Example.objects.all())

    class Meta:
        model = Category
        fields = (
            "id",
            "prob",
            "user",
            "example",
            "created_at",
            "updated_at",
            "label",
            "state"
        )
        read_only_fields = ("user",)


class SpanSerializer(serializers.ModelSerializer):
    label = serializers.PrimaryKeyRelatedField(queryset=SpanType.objects.all())
    example = serializers.PrimaryKeyRelatedField(queryset=Example.objects.all())

    class Meta:
        model = Span
        fields = (
            "id",
            "prob",
            "user",
            "example",
            "created_at",
            "updated_at",
            "label",
            "start_offset",
            "end_offset",
            "state"
        )
        read_only_fields = ("user",)


class TextLabelSerializer(serializers.ModelSerializer):
    example = serializers.PrimaryKeyRelatedField(queryset=Example.objects.all())

    class Meta:
        model = TextLabel
        fields = (
            "id",
            "prob",
            "user",
            "example",
            "created_at",
            "updated_at",
            "text",
            "state"
        )
        read_only_fields = ("user",)


class RelationSerializer(serializers.ModelSerializer):
    example = serializers.PrimaryKeyRelatedField(queryset=Example.objects.all())
    type = serializers.PrimaryKeyRelatedField(queryset=RelationType.objects.all())

    class Meta:
        model = Relation
        fields = ("id", "prob", "user", "example", "created_at", "updated_at", "from_id", "to_id", "type", "state")
        read_only_fields = ("user",)

class TraitSerializer(serializers.ModelSerializer):
    example = serializers.PrimaryKeyRelatedField(queryset=Example.objects.all())
    type = serializers.PrimaryKeyRelatedField(queryset=TraitType.objects.all())

    class Meta:
        model = Trait
        fields = ("id", "prob", "user", "example", "created_at", "updated_at", "entity_id", "type", "state")
        read_only_fields = ("user",)

class BoundingBoxSerializer(serializers.ModelSerializer):
    example = serializers.PrimaryKeyRelatedField(queryset=Example.objects.all())
    label = serializers.PrimaryKeyRelatedField(queryset=CategoryType.objects.all())

    class Meta:
        model = BoundingBox
        fields = (
            "id",
            "uuid",
            "prob",
            "user",
            "example",
            "created_at",
            "updated_at",
            "state",
            "label",
            "x",
            "y",
            "width",
            "height",
        )
        read_only_fields = ("user",)


class SegmentationSerializer(serializers.ModelSerializer):
    example = serializers.PrimaryKeyRelatedField(queryset=Example.objects.all())
    label = serializers.PrimaryKeyRelatedField(queryset=CategoryType.objects.all())

    class Meta:
        model = Segmentation
        fields = (
            "id",
            "uuid",
            "prob",
            "user",
            "example",
            "created_at",
            "updated_at",
            "state",
            "label",
            "points",
        )
        read_only_fields = ("user",)
