from typing import Dict, List, Type

from django.db.models import QuerySet

from . import catalog, formatters, labels, writers
from .labels import Labels
from data_export.models import ExportedExample
from projects.models import (
    DOCUMENT_CLASSIFICATION,
    IMAGE_CLASSIFICATION,
    INTENT_DETECTION_AND_SLOT_FILLING,
    SEQ2SEQ,
    SEQUENCE_LABELING,
    SPEECH2TEXT,
)


def select_writer(file_format: str) -> Type[writers.Writer]:
    mapping = {
        catalog.CSV.name: writers.CsvWriter,
        catalog.JSON.name: writers.JsonWriter,
        catalog.JSONL.name: writers.JsonlWriter,
        catalog.FastText.name: writers.FastTextWriter,
    }
    if file_format not in mapping:
        ValueError(f"Invalid format: {file_format}")
    return mapping[file_format]


def select_formatter(project, file_format: str) -> List[Type[formatters.Formatter]]:
    use_relation = getattr(project, "use_relation", False)
    mapping: Dict[str, Dict[str, List[Type[formatters.Formatter]]]] = {
        DOCUMENT_CLASSIFICATION: {
            catalog.CSV.name: [formatters.JoinedCategoryFormatter],
            catalog.JSON.name: [formatters.ListedCategoryFormatter],
            catalog.JSONL.name: [formatters.ListedCategoryFormatter],
            catalog.FastText.name: [formatters.FastTextCategoryFormatter],
        },
        SEQUENCE_LABELING: {
            catalog.JSONL.name: [formatters.DictFormatter, formatters.DictFormatter]
            if use_relation
            else [formatters.TupledSpanFormatter]
        },
        SEQ2SEQ: {
            catalog.CSV.name: [formatters.JoinedCategoryFormatter],
            catalog.JSON.name: [formatters.ListedCategoryFormatter],
            catalog.JSONL.name: [formatters.ListedCategoryFormatter],
        },
        IMAGE_CLASSIFICATION: {
            catalog.JSONL.name: [formatters.ListedCategoryFormatter],
        },
        SPEECH2TEXT: {
            catalog.JSONL.name: [formatters.ListedCategoryFormatter],
        },
        INTENT_DETECTION_AND_SLOT_FILLING: {
            catalog.JSONL.name: [formatters.ListedCategoryFormatter, formatters.TupledSpanFormatter]
        },
    }
    return mapping[project.project_type][file_format]


def select_label_collection(project):
    use_relation = getattr(project, "use_relation", False)
    mapping = {
        DOCUMENT_CLASSIFICATION: [labels.Categories],
        SEQUENCE_LABELING: [labels.Spans, labels.Relations] if use_relation else [labels.Spans],
        SEQ2SEQ: [labels.Texts],
        IMAGE_CLASSIFICATION: [labels.Categories],
        SPEECH2TEXT: [labels.Texts],
        INTENT_DETECTION_AND_SLOT_FILLING: [labels.Categories, labels.Spans],
    }
    return mapping[project.project_type]


def create_labels(label_collection_class: Type[Labels], examples: QuerySet[ExportedExample], user=None):
    return label_collection_class(examples, user)
