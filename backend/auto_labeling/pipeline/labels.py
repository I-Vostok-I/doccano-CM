import abc
from typing import List, Type

from auto_labeling_pipeline.labels import Labels
from django.contrib.auth.models import User

from examples.models import Example
from label_types.models import CategoryType, LabelType, SpanType, RelationType, TraitType
from labels.models import Category, Label, Span, TextLabel, Relation, Trait
from projects.models import Project


class LabelCollection(abc.ABC):
    label_type: Type[LabelType]
    model: Type[Label]

    def __init__(self, labels):
        self.labels = labels

    def transform(self, project: Project, example: Example, user: User) -> List[Label]:
        mapping = {c.text: c for c in self.label_type.objects.filter(project=project)}
        annotations = []
        for label in self.labels:
            if label["label"] not in mapping:
                continue
            label["example"] = example
            label["label"] = mapping[label["label"]]
            label["user"] = user
            label["state"] = "auto"
            annotations.append(self.model(**label))
        return annotations

    def save(self, project: Project, example: Example, user: User):
        labels = self.transform(project, example, user)
        labels = self.model.objects.filter_annotatable_labels(labels, project)
        self.model.objects.bulk_create(labels)


class Categories(LabelCollection):
    label_type = CategoryType
    model = Category


class Spans(LabelCollection):
    label_type = SpanType
    model = Span


class SpansRelsAndTraits(LabelCollection):
    label_type = SpanType
    model = Span
    rel_label_type = RelationType
    rel_model = Relation
    trait_label_type = TraitType
    trait_model = Trait

    def __init__(self, labels):
        self.unprocessed_labels = labels
        labels = [{key: label[key] for key in ["label", "start_offset", "end_offset"]}
                  for label in self.unprocessed_labels]
        super().__init__(labels)
        self.labels_relations = [{"from_id": relation["from_id"], "to_id": item["to_id"],
                                  "type": relation["relation_type"]}
                                 for item in self.unprocessed_labels for relation in item["relations"]]
        self.labels_traits = [{"entity_id": trait["entity_id"], "type": trait["trait_type"]} 
                              for item in self.unprocessed_labels for trait in item["traits"]]

    def save(self, project: Project, example: Example, user: User):
        labels = self.transform(project, example, user)
        labels = self.model.objects.filter_annotatable_labels(labels, project)
        _records = self.model.objects.bulk_create(labels)
        _idMap = {}
        for i, span in enumerate(self.unprocessed_labels):
            _idMap[span['to_id']] = _records[i]
        
        for relation in self.labels_relations:
            relation['to_id'] = _idMap[relation['to_id']]
            relation['from_id'] = _idMap[relation['from_id']]
        
        for trait in self.labels_traits:
            trait['entity_id'] = _idMap[trait['entity_id']]

        labels_relations = self.transform_relations(project, example, user)
        labels_relations = self.rel_model.objects.filter_annotatable_labels(labels_relations, project)
        self.rel_model.objects.bulk_create(labels_relations)

        labels_traits = self.transform_traits(project, example, user)
        labels_traits = self.trait_model.objects.filter_annotatable_labels(labels_traits, project)
        self.trait_model.objects.bulk_create(labels_traits)

    def transform_relations(self, project: Project, example: Example, user: User) -> List[Label]:
        mapping = {c.text: c for c in self.rel_label_type.objects.filter(project=project)}
        annotations = []
        for rel_label in self.labels_relations:
            if rel_label["type"] not in mapping:
                continue
            rel_label["example"] = example
            rel_label["type"] = mapping[rel_label["type"]]
            rel_label["user"] = user
            rel_label["state"] = "auto"
            annotations.append(self.rel_model(**rel_label))
        return annotations

    def transform_traits(self, project: Project, example: Example, user: User) -> List[Label]:
        mapping = {c.text: c for c in self.trait_label_type.objects.filter(project=project)}
        annotations = []
        for trait_label in self.labels_traits:
            if trait_label["type"] not in mapping:
                continue
            trait_label["example"] = example
            trait_label["type"] = mapping[trait_label["type"]]
            trait_label["user"] = user
            trait_label["state"] = "auto"
            annotations.append(self.trait_model(**trait_label))
        return annotations


class Texts(LabelCollection):
    model = TextLabel

    def transform(self, project: Project, example: Example, user: User) -> List[Label]:
        annotations = []
        for label in self.labels:
            label["example"] = example
            label["user"] = user
            annotations.append(self.model(**label))
        return annotations


def create_labels(task_type: str, labels: Labels) -> LabelCollection:
    return {"Category": Categories, "Span": Spans, "Text": Texts, "SpanRelAndTrait": SpansRelsAndTraits}[task_type](labels.dict())
