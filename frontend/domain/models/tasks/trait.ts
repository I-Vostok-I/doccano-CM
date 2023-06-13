export class Trait {
    constructor(
      readonly id: number,
      private _type: number,
      private _state: string,
      readonly entityId: number
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
  