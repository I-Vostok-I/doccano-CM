from typing import Type, Dict, Any

from auto_labeling_pipeline.labels import (
    ClassificationLabels,
    Labels,
    Seq2seqLabels,
    SequenceLabels,
    SequenceRelAndTraitLabels,
)
from auto_labeling_pipeline.mappings import MappingTemplate
from auto_labeling_pipeline.models import RequestModelFactory
from auto_labeling_pipeline.pipeline import pipeline, pipeline_import
from auto_labeling_pipeline.postprocessing import PostProcessor
from projects.models import Project
from examples.models import Example
from django.contrib.auth.models import User

from .labels import create_labels
from auto_labeling.models import AutoLabelingConfig


def get_label_collection(task_type: str) -> Type[Labels]:
    return {"Category": ClassificationLabels, "Span": SequenceLabels, "Text": Seq2seqLabels,
            "SpanRelAndTrait": SequenceRelAndTraitLabels}[task_type]


def execute_pipeline(data: str, config: AutoLabelingConfig):
    label_collection = get_label_collection(config.task_type)
    model = RequestModelFactory.create(model_name=config.model_name, attributes=config.model_attrs)
    template = MappingTemplate(label_collection=label_collection, template=config.template)
    post_processor = PostProcessor(config.label_mapping)
    labels = pipeline(text=data, request_model=model, mapping_template=template, post_processing=post_processor)
    labels = create_labels(config.task_type, labels)
    return labels


def automated_labeling_import(project: Project, example: Example, user: User, modelImport: Dict[Any, Any]):
    configs = AutoLabelingConfig.objects.filter(project=project)
    for config in configs:
        if config.model_name == modelImport["model"]:  
            labels = execute_pipeline_import(example.data, config=config, annotations=modelImport["annotations"])
            labels.save(project, example, user)
    return


def execute_pipeline_import(data: str, config: AutoLabelingConfig, annotations: Dict[Any, Any]):
    label_collection = get_label_collection(config.task_type)
    model = RequestModelFactory.create(model_name=config.model_name, attributes=config.model_attrs)
    template = MappingTemplate(label_collection=label_collection, template=config.template)
    post_processor = PostProcessor(config.label_mapping)
    labels = pipeline_import(text=data, annotations=annotations, mapping_template=template, post_processing=post_processor)
    labels = create_labels(config.task_type, labels)
    return labels
