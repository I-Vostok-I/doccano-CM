<template>
  <v-menu :value="opened" :position-x="x" :position-y="y" absolute offset-y @input="close">
    <v-row no-gutters>
      <v-col cols="8">
        <v-sheet :width="'100%'" :height="'100%'" class="pa-4">
          <v-list dense min-width="150" max-height="400" class="overflow-y-auto">
            <v-list-item>
              <v-autocomplete
                ref="autocomplete"
                v-model="value"
                :items="labels"
                autofocus
                dense
                deletable-chips
                hide-details
                item-text="text"
                item-value="id"
                label="Select a label"
                small-chips
              />
            </v-list-item>
            <v-list-item v-for="(label, i) in labels" :key="i" @click="onLabelSelected(label.id)">
              <v-list-item-action v-if="hasAnySuffixKey">
                <v-chip
                  v-if="label.suffixKey"
                  :color="label.backgroundColor"
                  outlined
                  small
                  v-text="label.suffixKey"
                />
                <span v-else class="mr-8" />
              </v-list-item-action>
              <v-list-item-content>
                <v-list-item-title v-text="label.text" />
              </v-list-item-content>
            </v-list-item>  
          </v-list>
        </v-sheet>
      </v-col>
      <v-col cols="4">
        <v-sheet :width="'100%'" :height="'100%'" class="pa-4">
          <p>Label Options:</p>
          <input id="checkbox" v-model="removed" type="checkbox" 
          @change="onRemovedChanged(labelType)" />
          <label for="checkbox">Remove</label>
        </v-sheet>
      </v-col>
    </v-row>
  </v-menu>
</template>

<script lang="ts">
import Vue from 'vue'
export default Vue.extend({
  props: {
    labels: {
      type: Array,
      default: () => [],
      required: true
    },
    opened: {
      type: Boolean,
      default: false,
      required: true
    },
    selectedLabel: {
      type: Object,
      default: null,
      required: false
    },
    x: {
      type: Number,
      default: 0,
      required: true
    },
    y: {
      type: Number,
      default: 0,
      required: true
    },
    annotation: {
      type: Object,
      default: null,
      required: false
    }
  },

  data() {
    return {
      startOffset: 0,
      endOffset: 0,
      entity: null as any,
      fromEntity: null as any,
      toEntity: null as any,
      removed: false,
      stringBoi: "" as string
    }
  },

  computed: {
    hasAnySuffixKey(): boolean {
      return this.labels.some((label: any) => label.suffixKey !== null)
    },

    value: {
      get() {
        return this.selectedLabel
      },
      set(labelId: number) {
        this.onLabelSelected(labelId)
      }
    },

    labelType(): any {
      if (this.selectedLabel != null)
      {
        return this.selectedLabel.id
      }
      return null
    }
  },

  watch: {
    annotation(newVal) {
      if (newVal != null) {
        if (newVal.state === "removed") {
          this.removed = true
        } else {
          this.removed = false
        }
      }
    }
  },

  methods: {
    close() {
      // Todo: a bit hacky. I want to fix this problem.
      // https://github.com/vuetifyjs/vuetify/issues/10765
      this.$nextTick(() => {
        if (this.$refs.autocomplete) {
          ;(this.$refs.autocomplete as any).selectedItems = []
        }
      })
      // this.$emit('close')
    },

    onLabelSelected(labelId: number) {
      if (this.removed) {
        this.$emit('click:label', labelId, 'removed')
      } else {
        this.$emit('click:label', labelId, 'modified')
      }
      this.close()
    },

    onRemovedChanged(labelId: any) {
      this.stringBoi = "in"
      if (labelId == null) {
        return
      }
      this.stringBoi = "not null"
      if (this.annotation != null) {
        if (this.annotation.state === "removed" && this.removed) {
          return
        }
        if (this.annotation.state !== "removed" && !this.removed) {
          return
        }
      }
      this.stringBoi = labelId.toString()
      if (this.removed) {
        this.stringBoi = "Updateing label"
        this.$emit('click:label', labelId, 'removed')
      } else {
        this.$emit('click:label', labelId, 'modified')
      }
    }
  }
})
</script>
