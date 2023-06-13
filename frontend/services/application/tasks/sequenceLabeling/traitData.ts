import { Trait } from '@/domain/models/tasks/trait'

export class TraitDTO {
  id: number
  type: number
  state: string
  entityId: number

  constructor(item: Trait) {
    this.id = item.id
    this.type = item.type
    this.state = item.state
    this.entityId = item.entityId
  }
}
