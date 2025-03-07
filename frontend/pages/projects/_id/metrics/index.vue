<template>
  <v-row>
    <v-col cols="12">
      <member-progress />
    </v-col>
    <v-col v-if="!!project.canDefineCategory" cols="12">
      <label-distribution
        title="Category Distribution"
        :distribution="categoryDistribution"
        :label-types="categoryTypes"
      />
    </v-col>
    <v-col v-if="!!project.canDefineSpan" cols="12">
      <label-distribution
        title="Span Distribution"
        :distribution="spanDistribution"
        :label-types="spanTypes"
      />
    </v-col>
    <v-col v-if="!!project.canDefineRelation" cols="12">
      <label-distribution
        title="Relation Distribution"
        :distribution="relationDistribution"
        :label-types="relationTypes"
      />
    </v-col>
    <v-col v-if="!!project.canDefineTrait" cols="12">
      <label-distribution
        title="Trait Distribution"
        :distribution="traitDistribution"
        :label-types="traitTypes"
      />
    </v-col>
  </v-row>
</template>

<script>
import LabelDistribution from '~/components/metrics/LabelDistribution'
import MemberProgress from '~/components/metrics/MemberProgress'

export default {
  components: {
    LabelDistribution,
    MemberProgress
  },

  layout: 'project',

  validate({ params }) {
    return /^\d+$/.test(params.id)
  },

  data() {
    return {
      project: {},
      categoryTypes: [],
      categoryDistribution: {},
      relationTypes: [],
      relationDistribution: {},
      traitTypes: [],
      traitDistribution: {},
      spanTypes: [],
      spanDistribution: {}
    }
  },

  computed: {
    projectId() {
      return this.$route.params.id
    }
  },

  async created() {
    this.project = await this.$services.project.findById(this.projectId)
    if (this.project.canDefineCategory) {
      this.categoryTypes = await this.$services.categoryType.list(this.projectId)
      this.categoryDistribution = await this.$repositories.metrics.fetchCategoryDistribution(
        this.projectId
      )
    }
    if (this.project.canDefineSpan) {
      this.spanTypes = await this.$services.spanType.list(this.projectId)
      this.spanDistribution = await this.$repositories.metrics.fetchSpanDistribution(this.projectId)
    }
    if (this.project.canDefineRelation) {
      this.relationTypes = await this.$services.relationType.list(this.projectId)
      this.relationDistribution = await this.$repositories.metrics.fetchRelationDistribution(
        this.projectId
      )
    }
    if (this.project.canDefineTrait) {
      this.traitTypes = await this.$services.traitType.list(this.projectId)
      this.traitDistribution = await this.$repositories.metrics.fetchTraitDistribution(
        this.projectId
      )
    }
  }
}
</script>
