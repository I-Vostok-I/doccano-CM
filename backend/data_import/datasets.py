import abc
from typing import List, Type

from django.contrib.auth.models import User

from .models import DummyLabelType
from .pipeline.catalog import RELATION_EXTRACTION, TRAIT_EXTRACTION, RELATION_TRAIT_EXTRACTION, AWS_CM_IMPORT, Format
from .pipeline.data import BaseData, BinaryData, TextData
from .pipeline.examples import Examples
from .pipeline.exceptions import FileParseException
from .pipeline.factories import create_parser
from .pipeline.label import CategoryLabel, Label, RelationLabel, TraitLabel, SpanLabel, TextLabel
from .pipeline.label_types import LabelTypes
from .pipeline.labels import Categories, Labels, Relations, Traits, Spans, Texts
from .pipeline.makers import BinaryExampleMaker, ExampleMaker, LabelMaker, AwsCmMaker
from .pipeline.readers import (
    DEFAULT_LABEL_COLUMN,
    DEFAULT_TEXT_COLUMN,
    FileName,
    Reader,
)
from label_types.models import CategoryType, LabelType, RelationType, TraitType, SpanType
from projects.models import (
    BOUNDING_BOX,
    DOCUMENT_CLASSIFICATION,
    IMAGE_CAPTIONING,
    IMAGE_CLASSIFICATION,
    INTENT_DETECTION_AND_SLOT_FILLING,
    SEGMENTATION,
    SEQ2SEQ,
    SEQUENCE_LABELING,
    SPEECH2TEXT,
    Project,
)
from auto_labeling.pipeline.execution import automated_labeling_import


class Dataset(abc.ABC):
    def __init__(self, reader: Reader, project: Project, **kwargs):
        self.reader = reader
        self.project = project
        self.kwargs = kwargs

    def save(self, user: User, batch_size: int = 1000):
        raise NotImplementedError()

    @property
    def errors(self) -> List[FileParseException]:
        raise NotImplementedError()


class PlainDataset(Dataset):
    def __init__(self, reader: Reader, project: Project, **kwargs):
        super().__init__(reader, project, **kwargs)
        self.example_maker = ExampleMaker(project=project, data_class=TextData)

    def save(self, user: User, batch_size: int = 1000):
        for records in self.reader.batch(batch_size):
            examples = Examples(self.example_maker.make(records))
            examples.save()

    @property
    def errors(self) -> List[FileParseException]:
        return self.reader.errors + self.example_maker.errors


class DatasetWithSingleLabelType(Dataset):
    data_class: Type[BaseData]
    label_class: Type[Label]
    label_type = LabelType
    labels_class = Labels

    def __init__(self, reader: Reader, project: Project, **kwargs):
        super().__init__(reader, project, **kwargs)
        self.types = LabelTypes(self.label_type)
        self.example_maker = ExampleMaker(
            project=project,
            data_class=self.data_class,
            column_data=kwargs.get("column_data") or DEFAULT_TEXT_COLUMN,
            exclude_columns=[kwargs.get("column_label") or DEFAULT_LABEL_COLUMN],
        )
        self.label_maker = LabelMaker(
            column=kwargs.get("column_label") or DEFAULT_LABEL_COLUMN, label_class=self.label_class
        )

    def save(self, user: User, batch_size: int = 1000):
        for records in self.reader.batch(batch_size):
            # create examples
            examples = Examples(self.example_maker.make(records))
            examples.save()

            # create label types
            labels = self.labels_class(self.label_maker.make(records), self.types)
            labels.clean(self.project)
            labels.save_types(self.project)

            # create Labels
            labels.save(user, examples)

    @property
    def errors(self) -> List[FileParseException]:
        return self.reader.errors + self.example_maker.errors + self.label_maker.errors


class BinaryDataset(Dataset):
    def __init__(self, reader: Reader, project: Project, **kwargs):
        super().__init__(reader, project, **kwargs)
        self.example_maker = BinaryExampleMaker(project=project, data_class=BinaryData)

    def save(self, user: User, batch_size: int = 1000):
        for records in self.reader.batch(batch_size):
            examples = Examples(self.example_maker.make(records))
            examples.save()

    @property
    def errors(self) -> List[FileParseException]:
        return self.reader.errors + self.example_maker.errors


class TextClassificationDataset(DatasetWithSingleLabelType):
    data_class = TextData
    label_class = CategoryLabel
    label_type = CategoryType
    labels_class = Categories


class SequenceLabelingDataset(DatasetWithSingleLabelType):
    data_class = TextData
    label_class = SpanLabel
    label_type = SpanType
    labels_class = Spans


class Seq2seqDataset(DatasetWithSingleLabelType):
    data_class = TextData
    label_class = TextLabel
    label_type = DummyLabelType
    labels_class = Texts


class RelationExtractionDataset(Dataset):
    def __init__(self, reader: Reader, project: Project, **kwargs):
        super().__init__(reader, project, **kwargs)
        self.span_types = LabelTypes(SpanType)
        self.relation_types = LabelTypes(RelationType)
        self.example_maker = ExampleMaker(
            project=project,
            data_class=TextData,
            column_data=kwargs.get("column_data") or DEFAULT_TEXT_COLUMN,
            exclude_columns=["entities", "relations"],
        )
        self.span_maker = LabelMaker(column="entities", label_class=SpanLabel)
        self.relation_maker = LabelMaker(column="relations", label_class=RelationLabel)

    def save(self, user: User, batch_size: int = 1000):
        for records in self.reader.batch(batch_size):
            # create examples
            examples = Examples(self.example_maker.make(records))
            examples.save()

            # create label types
            spans = Spans(self.span_maker.make(records), self.span_types)
            spans.clean(self.project)
            spans.save_types(self.project)

            relations = Relations(self.relation_maker.make(records), self.relation_types)
            relations.clean(self.project)
            relations.save_types(self.project)

            # create Labels
            spans.save(user, examples)
            relations.save(user, examples, spans=spans)

    @property
    def errors(self) -> List[FileParseException]:
        return self.reader.errors + self.example_maker.errors + self.span_maker.errors + self.relation_maker.errors


class TraitExtractionDataset(Dataset):
    def __init__(self, reader: Reader, project: Project, **kwargs):
        super().__init__(reader, project, **kwargs)
        self.span_types = LabelTypes(SpanType)
        self.trait_types = LabelTypes(TraitType)
        self.example_maker = ExampleMaker(
            project=project,
            data_class=TextData,
            column_data=kwargs.get("column_data") or DEFAULT_TEXT_COLUMN,
            exclude_columns=["entities", "traits"],
        )
        self.span_maker = LabelMaker(column="entities", label_class=SpanLabel)
        self.trait_maker = LabelMaker(column="traits", label_class=TraitLabel)

    def save(self, user: User, batch_size: int = 1000):
        for records in self.reader.batch(batch_size):
            # create examples
            examples = Examples(self.example_maker.make(records))
            examples.save()

            # create label types
            spans = Spans(self.span_maker.make(records), self.span_types)
            spans.clean(self.project)
            spans.save_types(self.project)

            traits = Traits(self.trait_maker.make(records), self.trait_types)
            traits.clean(self.project)
            traits.save_types(self.project)

            # create Labels
            spans.save(user, examples)
            traits.save(user, examples, spans=spans)

    @property
    def errors(self) -> List[FileParseException]:
        return self.reader.errors + self.example_maker.errors + self.span_maker.errors + self.trait_maker.errors


class RelationAndTraitExtractionDataset(Dataset):
    def __init__(self, reader: Reader, project: Project, **kwargs):
        super().__init__(reader, project, **kwargs)
        self.span_types = LabelTypes(SpanType)
        self.relation_types = LabelTypes(RelationType)
        self.trait_types = LabelTypes(TraitType)
        self.example_maker = ExampleMaker(
            project=project,
            data_class=TextData,
            column_data=kwargs.get("column_data") or DEFAULT_TEXT_COLUMN,
            exclude_columns=["entities", "relations", "traits"],
        )
        self.span_maker = LabelMaker(column="entities", label_class=SpanLabel)
        self.relation_maker = LabelMaker(column="relations", label_class=RelationLabel)
        self.trait_maker = LabelMaker(column="traits", label_class=TraitLabel)

    def save(self, user: User, batch_size: int = 1000):
        for records in self.reader.batch(batch_size):
            # create examples
            examples = Examples(self.example_maker.make(records))
            examples.save()

            # create label types
            spans = Spans(self.span_maker.make(records), self.span_types)
            spans.clean(self.project)
            spans.save_types(self.project)

            relations = Relations(self.relation_maker.make(records), self.relation_types)
            relations.clean(self.project)
            relations.save_types(self.project)

            traits = Traits(self.trait_maker.make(records), self.trait_types)
            traits.clean(self.project)
            traits.save_types(self.project)

            # create Labels
            spans.save(user, examples)
            relations.save(user, examples, spans=spans)
            traits.save(user, examples, spans=spans)

    @property
    def errors(self) -> List[FileParseException]:
        return self.reader.errors + self.example_maker.errors + self.span_maker.errors + self.trait_maker.errors + self.relation_maker.errors
    
class AwsCmImportDataset(Dataset):
    def __init__(self, reader: Reader, project: Project, **kwargs):
        super().__init__(reader, project, **kwargs)
        self.example_maker = ExampleMaker(
            project=project,
            data_class=TextData,
            column_data=kwargs.get("column_data") or DEFAULT_TEXT_COLUMN,
            exclude_columns=["model", "annotations"],
        )
        self.request_maker = AwsCmMaker(column="annotations")

    def save(self, user: User, batch_size: int = 1000):
        for records in self.reader.batch(batch_size):
            # create examples
            examples = Examples(self.example_maker.make(records))
            examples.save()

            requests = self.request_maker.make(records)
            for request in requests:
                automated_labeling_import(self.project, examples[request["example_uuid"]], user, request)

            # create label types
            # automated_labeling_import(self.project, , user, )

    @property
    def errors(self) -> List[FileParseException]:
        return self.reader.errors + self.example_maker.errors + self.request_maker.errors



class CategoryAndSpanDataset(Dataset):
    def __init__(self, reader: Reader, project: Project, **kwargs):
        super().__init__(reader, project, **kwargs)
        self.category_types = LabelTypes(CategoryType)
        self.span_types = LabelTypes(SpanType)
        self.example_maker = ExampleMaker(
            project=project,
            data_class=TextData,
            column_data=kwargs.get("column_data") or DEFAULT_TEXT_COLUMN,
            exclude_columns=["cats", "entities"],
        )
        self.category_maker = LabelMaker(column="cats", label_class=CategoryLabel)
        self.span_maker = LabelMaker(column="entities", label_class=SpanLabel)

    def save(self, user: User, batch_size: int = 1000):
        for records in self.reader.batch(batch_size):
            # create examples
            examples = Examples(self.example_maker.make(records))
            examples.save()

            # create label types
            categories = Categories(self.category_maker.make(records), self.category_types)
            categories.clean(self.project)
            categories.save_types(self.project)

            spans = Spans(self.span_maker.make(records), self.span_types)
            spans.clean(self.project)
            spans.save_types(self.project)

            # create Labels
            categories.save(user, examples)
            spans.save(user, examples)

    @property
    def errors(self) -> List[FileParseException]:
        return self.reader.errors + self.example_maker.errors + self.category_maker.errors + self.span_maker.errors


def select_dataset(project: Project, task: str, file_format: Format) -> Type[Dataset]:
    mapping = {
        DOCUMENT_CLASSIFICATION: TextClassificationDataset,
        SEQUENCE_LABELING: SequenceLabelingDataset,
        RELATION_EXTRACTION: RelationExtractionDataset,
        RELATION_TRAIT_EXTRACTION: RelationAndTraitExtractionDataset,
        AWS_CM_IMPORT: AwsCmImportDataset,
        TRAIT_EXTRACTION: TraitExtractionDataset,
        SEQ2SEQ: Seq2seqDataset,
        INTENT_DETECTION_AND_SLOT_FILLING: CategoryAndSpanDataset,
        IMAGE_CLASSIFICATION: BinaryDataset,
        IMAGE_CAPTIONING: BinaryDataset,
        BOUNDING_BOX: BinaryDataset,
        SEGMENTATION: BinaryDataset,
        SPEECH2TEXT: BinaryDataset,
    }
    if task not in mapping:
        task = project.project_type
    if project.is_text_project and file_format.is_plain_text():
        return PlainDataset
    return mapping[task]


def load_dataset(task: str, file_format: Format, data_files: List[FileName], project: Project, **kwargs) -> Dataset:
    parser = create_parser(file_format, **kwargs)
    reader = Reader(data_files, parser)
    dataset_class = select_dataset(project, task, file_format)
    return dataset_class(reader, project, **kwargs)
