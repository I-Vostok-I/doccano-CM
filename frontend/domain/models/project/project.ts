import { TagItem } from '~/domain/models/tag/tag'

export const DocumentClassification = 'DocumentClassification'
export const SequenceLabeling = 'SequenceLabeling'
export const SequenceRelationAndTraitLabeling = 'SequenceRelationAndTraitLabeling'
export const Seq2seq = 'Seq2seq'
export const IntentDetectionAndSlotFilling = 'IntentDetectionAndSlotFilling'
export const ImageClassification = 'ImageClassification'
export const ImageCaptioning = 'ImageCaptioning'
export const BoundingBox = 'BoundingBox'
export const Segmentation = 'Segmentation'
export const Speech2text = 'Speech2text'

export const allProjectTypes = <const>[
  DocumentClassification,
  SequenceLabeling,
  Seq2seq,
  IntentDetectionAndSlotFilling,
  ImageClassification,
  ImageCaptioning,
  BoundingBox,
  Segmentation,
  Speech2text
]
export type ProjectType = (typeof allProjectTypes)[number]
const MIN_LENGTH = 1
const MAX_PROJECT_NAME_LENGTH = 100

export const validateMinLength = (text: string): boolean => {
  return text.trim().length >= MIN_LENGTH
}

export const validateNameMaxLength = (name: string): boolean => {
  return name.trim().length <= MAX_PROJECT_NAME_LENGTH
}

export class Project {
  name: string
  description: string
  projectType: ProjectType
  constructor(
    readonly id: number,
    readonly _name: string,
    readonly _description: string,
    readonly guideline: string,
    readonly _projectType: string,
    readonly enableRandomOrder: boolean,
    readonly enableSharingMode: boolean,
    readonly exclusiveCategories: boolean,
    readonly allowOverlappingSpans: boolean,
    readonly enableGraphemeMode: boolean,
    readonly useRelation: boolean,
    readonly useTrait: boolean,
    readonly tags: TagItem[],
    readonly users: number[] = [],
    readonly createdAt: string = '',
    readonly updatedAt: string = '',
    readonly author: string = '',
    readonly isTextProject: boolean = false
  ) {
    if (!validateMinLength(_name)) {
      throw new Error('Project name is required')
    }
    if (!validateNameMaxLength(_name)) {
      throw new Error('Project name must be less than 100 characters')
    }
    if (!validateMinLength(_description)) {
      throw new Error('Project description is required')
    }
    if (!allProjectTypes.includes(_projectType as ProjectType)) {
      throw new Error(`Invalid project type: ${_projectType}`)
    }
    this.name = _name.trim()
    this.description = _description.trim()
    this.projectType = _projectType as ProjectType
  }

  static create(
    id: number,
    name: string,
    description: string,
    guideline: string,
    projectType: string,
    enableRandomOrder: boolean,
    enableSharingMode: boolean,
    exclusiveCategories: boolean,
    allowOverlappingSpans: boolean,
    enableGraphemeMode: boolean,
    useRelation: boolean,
    useTrait: boolean,
    tags: TagItem[]
  ) {
    return new Project(
      id,
      name,
      description,
      guideline,
      projectType,
      enableRandomOrder,
      enableSharingMode,
      exclusiveCategories,
      allowOverlappingSpans,
      enableGraphemeMode,
      useRelation,
      useTrait,
      tags
    )
  }

  get canDefineLabel(): boolean {
    return this.canDefineCategory || this.canDefineSpan
  }

  get canDefineCategory(): boolean {
    return [
      DocumentClassification,
      IntentDetectionAndSlotFilling,
      ImageClassification,
      BoundingBox,
      Segmentation
    ].includes(this.projectType)
  }

  get canDefineSpan(): boolean {
    return [SequenceLabeling, IntentDetectionAndSlotFilling].includes(this.projectType)
  }

  get canDefineRelation(): boolean {
    return this.useRelation
  }

  get canDefineTrait(): boolean {
    return this.useTrait
  }

  get taskNames(): string[] {
    if (this.projectType === IntentDetectionAndSlotFilling) {
      return [DocumentClassification, SequenceLabeling]
    }
    if (this.projectType === SequenceLabeling && this.allowOverlappingSpans && 
      this.useRelation && this.useTrait) {
      return [SequenceLabeling, SequenceRelationAndTraitLabeling];
    }
    // INSERTED CODE ABOUVE TO ADD NEW PROJECT TYPE.
    return [this.projectType]
  }

  get resourceType(): string {
    if (this.projectType === DocumentClassification) {
      return 'TextClassificationProject'
    }
    return `${this.projectType}Project`
  }
}
