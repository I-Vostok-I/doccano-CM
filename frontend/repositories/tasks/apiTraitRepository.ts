import { AnnotationRepository } from '@/domain/models/tasks/annotationRepository'
import { Trait } from '@/domain/models/tasks/trait'

export class APITraitRepository extends AnnotationRepository<Trait> {
  labelName = 'traits'

  toModel(item: { [key: string]: any }): Trait {
    return new Trait(item.id, item.type, item.state, item.entity_id)
  }

  toPayload(item: Trait): { [key: string]: any } {
    return {
      id: item.id,
      type: item.type,
      state: item.state,
      entity_id: item.entityId
    }
  }
}
