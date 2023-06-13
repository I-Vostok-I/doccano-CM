<template>
  <div v-shortkey="['esc']" @shortkey="cleanUp">
    <v-annotator
      :dark="$vuetify.theme.dark"
      :rtl="rtl"
      :text="text"
      :entities="entities"
      :entity-labels="entityLabels"
      :relations="relations"
      :relation-labels="relationLabels"
      :traits="traits"
      :trait-labels="traitLabels"
      :allow-overlapping="allowOverlapping"
      :grapheme-mode="graphemeMode"
      :selected-entities="selectedEntities"
      @add:entity="handleAddEvent"
      @click:entity="onEntityClicked"
      @click:relation="onRelationClicked"
      @click:trait="onTraitClicked"
      @contextmenu:entity="deleteEntity"
      @contextmenu:relation="deleteRelation"
      @contextmenu:trait="deleteTrait"
    />
    <labeling-menu
      :opened="entityMenuOpened"
      :x="x"
      :y="y"
      :selected-label="currentLabel"
      :labels="entityLabels"
      :annotation="entity"
      @close="cleanUp"
      @click:label="addOrUpdateEntity"
    />
    <labeling-menu
      :opened="relationMenuOpened"
      :x="x"
      :y="y"
      :selected-label="currentRelationLabel"
      :labels="relationLabels"
      :annotation="relation"
      @close="cleanUp"
      @click:label="addOrUpdateRelation"
    />
    <labeling-menu
      :opened="traitMenuOpened"
      :x="x"
      :y="y"
      :selected-label="currentTraitLabel"
      :labels="traitLabels"
      :annotation="trait"
      @close="cleanUp"
      @click:label="addOrUpdateTrait"
    />
  </div>
</template>

<script lang="ts">
import VAnnotator from 'v-annotator'
import type { PropType } from 'vue'
import Vue from 'vue'
import 'vue-virtual-scroller/dist/vue-virtual-scroller.css'
import LabelingMenu from './LabelingMenu.vue'
import { SpanDTO } from '~/services/application/tasks/sequenceLabeling/sequenceLabelingData'

export default Vue.extend({
  components: {
    VAnnotator,
    LabelingMenu
  },

  props: {
    dark: {
      type: Boolean,
      default: false
    },
    rtl: {
      type: Boolean,
      default: false
    },
    text: {
      type: String,
      default: '',
      required: true
    },
    entities: {
      type: Array as PropType<SpanDTO[]>,
      default: () => [],
      required: true
    },
    entityLabels: {
      type: Array,
      default: () => [],
      required: true
    },
    relations: {
      type: Array,
      default: () => []
    },
    relationLabels: {
      type: Array,
      default: () => []
    },
    traits: {
      type: Array,
      default: () => []
    },
    traitLabels: {
      type: Array,
      default: () => []
    },
    allowOverlapping: {
      type: Boolean,
      default: false,
      required: false
    },
    graphemeMode: {
      type: Boolean,
      default: false
    },
    selectedLabel: {
      type: Object,
      default: null,
      required: false
    },
    relationMode: {
      type: Boolean,
      default: false
    },
    traitMode: {
      type: Boolean,
      default: false
    }
  },

  data() {
    return {
      entityMenuOpened: false,
      relationMenuOpened: false,
      traitMenuOpened: false,
      x: 0,
      y: 0,
      startOffset: 0,
      endOffset: 0,
      entity: null as any,
      relation: null as any,
      trait: null as any,
      selectedEntities: [] as SpanDTO[]
    }
  },

  computed: {
    currentLabel(): any {
      if (this.entity) {
        const label = this.entityLabels.find((label: any) => label.id === this.entity!.label)
        return label
      } else {
        return null
      }
    },

    currentRelationLabel(): any {
      if (this.relation) {
        const label = this.relationLabels.find((label: any) => label.id === this.relation.labelId)
        return label
      } else {
        return null
      }
    },

    currentTraitLabel(): any {
      if (this.trait) {
        const label = this.traitLabels.find((label: any) => label.id === this.trait.type)
        return label
      } else {
        return null
      }
    }
  },

  methods: {
    setOffset(startOffset: number, endOffset: number) {
      this.startOffset = startOffset
      this.endOffset = endOffset
    },

    setEntity(entityId: number) {
      this.entity = this.entities.find((entity: any) => entity.id === entityId)
    },

    setRelation(relationId: number) {
      this.relation = this.relations.find((relation: any) => relation.id === relationId)
    },

    setTrait(traitId: number) {
      this.trait = this.traits.find((trait: any) => trait.id === traitId)
    },

    setEntityForRelation(e: Event, entityId: number) {
      const entity = this.entities.find((entity) => entity.id === entityId)!
      const index = this.selectedEntities.findIndex((e) => e.id === entity.id)
      if (index === -1) {
        this.selectedEntities.push(entity)
      } else {
        this.selectedEntities.splice(index, 1)
      }
      if (this.selectedEntities.length === 2) {
        if (this.selectedLabel) {
          this.addRelation(this.selectedLabel.id)
          this.cleanUp()
        } else {
          this.showRelationLabelMenu(e)
        }
      }
    },

    setEntityForTrait(e: Event, entityId: number) {
      const entity = this.entities.find((entity) => entity.id === entityId)!
      const index = this.selectedEntities.findIndex((e) => e.id === entity.id)
      if (index === -1) {
        this.selectedEntities.push(entity)
      } else {
        this.selectedEntities.splice(index, 1)
      }
      if (this.selectedEntities.length === 1) {
        if (this.selectedLabel) {
          this.addTrait(this.selectedLabel.id)
          this.cleanUp()
        } else {
          this.showTraitLabelMenu(e)
        }
      }
    },

    showEntityLabelMenu(e: any) {
      e.preventDefault()
      this.entityMenuOpened = false
      this.x = e.clientX || e.changedTouches[0].clientX
      this.y = e.clientY || e.changedTouches[0].clientY
      this.$nextTick(() => {
        this.entityMenuOpened = true
      })
    },

    showRelationLabelMenu(e: any) {
      e.preventDefault()
      this.relationMenuOpened = false
      this.x = e.clientX || e.changedTouches[0].clientX
      this.y = e.clientY || e.changedTouches[0].clientY
      this.$nextTick(() => {
        this.relationMenuOpened = true
      })
    },

    showTraitLabelMenu(e: any) {
      e.preventDefault()
      this.traitMenuOpened = false
      this.x = e.clientX || e.changedTouches[0].clientX
      this.y = e.clientY || e.changedTouches[0].clientY
      this.$nextTick(() => {
        this.traitMenuOpened = true
      })
    },

    handleAddEvent(e: any, startOffset: number, endOffset: number) {
      this.setOffset(startOffset, endOffset)
      if (this.selectedLabel) {
        this.addOrUpdateEntity(this.selectedLabel.id, 'added')
      } else {
        this.showEntityLabelMenu(e)
      }
    },

    onEntityClicked(e: any, entityId: number) {
      if (this.relationMode) {
        this.setEntityForRelation(e, entityId)        
      } else if (this.traitMode) {
        this.setEntityForTrait(e, entityId)
      } else {
        this.setEntity(entityId)
        this.showEntityLabelMenu(e)
      }
    },

    onRelationClicked(e: any, relation: any) {
      this.setRelation(relation.id)
      this.showRelationLabelMenu(e)
    },

    onTraitClicked(e: any, trait: any) {
      this.setTrait(trait.id)
      this.showTraitLabelMenu(e)
    },

    addOrUpdateEntity(labelId: number, newState: string) {
      if (labelId) {
        if (this.entity) {
          this.updateEntity(labelId, newState)
        } else {
          this.addEntity(labelId)
        }
      } else {
        this.deleteEntity(this.entity)
      }
      this.cleanUp()
    },

    addOrUpdateRelation(labelId: number, newState: string) {
      if (labelId) {
        if (this.relation) {
          this.updateRelation(labelId, newState)
        } else {
          this.addRelation(labelId)
        }
      } else {
        this.deleteRelation(this.relation)
      }
      this.cleanUp()
    },

    addOrUpdateTrait(type: number, newState: string) {
      if (type) {
        if (this.trait) {
          this.updateTrait(type, newState)
        } else {
          this.addTrait(type)
        }
      } else {
        this.deleteTrait(this.trait)
      }
      this.cleanUp()
    },

    addEntity(labelId: number) {
      this.$emit('addEntity', this.startOffset, this.endOffset, labelId)
    },

    updateEntity(labelId: number, newState: string) {
      this.$emit('click:entity', this.entity!.id, labelId, newState)
    },

    deleteEntity(entity: any) {
      this.$emit('contextmenu:entity', entity.id)
      this.cleanUp()
    },

    cleanUp() {
      this.entityMenuOpened = false
      this.relationMenuOpened = false
      this.traitMenuOpened = false
      this.entity = null
      this.relation = null
      this.trait = null
      this.startOffset = 0
      this.endOffset = 0
      this.selectedEntities = []
    },

    addRelation(labelId: number) {
      const [fromEntity, toEntity] = this.selectedEntities
      this.$emit('addRelation', fromEntity.id, toEntity.id, labelId)
    },

    updateRelation(labelId: number, newState: string) {
      this.$emit('click:relation', this.relation.id, labelId, newState)
    },

    deleteRelation(relation: any) {
      this.$emit('contextmenu:relation', relation.id)
    },

    addTrait(type: number) {
      const [boundEntity] = this.selectedEntities
      this.$emit('addTrait', type, boundEntity.id)
    },

    updateTrait(type: number, newState: string) {
      this.$emit('click:trait', this.trait.id, type, newState)
    },

    deleteTrait(trait: any) {
      this.$emit('contextmenu:trait', trait.id)
    }
  }
})
</script>
