export class Span {
  constructor(
    readonly id: number,
    private _label: number,
    private _state: string,
    readonly user: number,
    readonly startOffset: number,
    readonly endOffset: number
  ) {}

  get label(): number {
    return this._label
  }
  
  get state(): string {
    return this._state
  }

  changeLabel(label: number) {
    this._label = label
  }
  
  changeState(state: string) {
    this._state = state
  }
}
