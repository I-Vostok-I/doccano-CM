export class Relation {
  constructor(
    readonly id: number,
    readonly fromId: number,
    readonly toId: number,
    private _type: number,
    private _state: string
  ) {}

  get type(): number {
    return this._type
  }
  
  get state(): string {
    return this._state
  }

  changeType(type: number) {
    this._type = type
  }

  changeState(state: string) {
    this._state = state
  }
}
