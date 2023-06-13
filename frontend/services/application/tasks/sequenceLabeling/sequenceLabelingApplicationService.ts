import { AnnotationApplicationService } from '../annotationApplicationService'
import { TraitDTO } from './traitData'
import { RelationDTO } from './relationData'
import { SpanDTO } from './sequenceLabelingData'
import { APISpanRepository } from '@/repositories/tasks/apiSpanRepository'
import { APIRelationRepository } from '@/repositories/tasks/apiRelationRepository'
import { Span } from '@/domain/models/tasks/span'
import { Relation } from '@/domain/models/tasks/relation'
import { APITraitRepository } from '~/repositories/tasks/apiTraitRepository'
import { Trait } from '~/domain/models/tasks/trait'

export class SequenceLabelingApplicationService extends AnnotationApplicationService<Span> {
  constructor(
    readonly repository: APISpanRepository,
    readonly relationRepository: APIRelationRepository,
    readonly traitRepository: APITraitRepository
  ) {
    super(new APISpanRepository())
  }

  public async list(projectId: string, exampleId: number): Promise<SpanDTO[]> {
    const items = await this.repository.list(projectId, exampleId)
    return items.map((item) => new SpanDTO(item))
  }

  public async create(
    projectId: string,
    exampleId: number,
    labelId: number,
    startOffset: number,
    endOffset: number
  ): Promise<void> {
    const item = new Span(0, labelId, "added", 0, startOffset, endOffset)
    try {
      await this.repository.create(projectId, exampleId, item)
    } catch (e: any) {
      console.log(e.response.data.detail)
    }
  }

  public async changeLabel(
    projectId: string,
    exampleId: number,
    annotationId: number,
    labelId: number,
    newState: string
  ): Promise<void> {
    try {
      const span = await this.repository.find(projectId, exampleId, annotationId)
      span.changeLabel(labelId)
      span.changeState(newState)
      await this.repository.update(projectId, exampleId, annotationId, span)
    } catch (e: any) {
      console.log(e.response.data.detail)
    }
  }

  public async listRelations(projectId: string, exampleId: number): Promise<RelationDTO[]> {
    const items = await this.relationRepository.list(projectId, exampleId)
    return items.map((item) => new RelationDTO(item))
  }

  public async createRelation(
    projectId: string,
    exampleId: number,
    fromId: number,
    toId: number,
    typeId: number
  ): Promise<void> {
    const relation = new Relation(0, fromId, toId, typeId, "added")
    await this.relationRepository.create(projectId, exampleId, relation)
  }

  public async deleteRelation(
    projectId: string,
    exampleId: number,
    relationId: number
  ): Promise<void> {
    await this.relationRepository.delete(projectId, exampleId, relationId)
  }

  public async updateRelation(
    projectId: string,
    exampleId: number,
    relationId: number,
    typeId: number,
    newState: string
  ): Promise<void> {
    const relation = await this.relationRepository.find(projectId, exampleId, relationId)
    relation.changeType(typeId)
    relation.changeState(newState)
    await this.relationRepository.update(projectId, exampleId, relationId, relation)
  }

  public async listTraits(projectId: string, exampleId: number): Promise<TraitDTO[]> {
    const items = await this.traitRepository.list(projectId, exampleId)
    return items.map((item) => new TraitDTO(item))
  }

  public async createTrait(
    projectId: string,
    exampleId: number,
    typeId: number,
    entityId: number,
  ): Promise<void> {
    const trait = new Trait(0, typeId, "added", entityId)
    await this.traitRepository.create(projectId, exampleId, trait)
  }

  public async deleteTrait(
    projectId: string,
    exampleId: number,
    traitId: number
  ): Promise<void> {
    await this.traitRepository.delete(projectId, exampleId, traitId)
  }

  public async updateTrait(
    projectId: string,
    exampleId: number,
    traitId: number,
    typeId: number,
    newState: string
  ): Promise<void> {
    const trait = await this.traitRepository.find(projectId, exampleId, traitId)
    trait.changeType(typeId)
    trait.changeState(newState)
    await this.traitRepository.update(projectId, exampleId, traitId, trait)
  }
}
