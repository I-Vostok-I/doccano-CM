<template>
  <form-import :error-message="errorMessage" @clear="clearErrorMessage" @upload="upload" />
</template>

<script lang="ts">
import Vue from 'vue'
import FormImport from '~/components/label/FormImport.vue'
import { Project } from '~/domain/models/project/project'

export default Vue.extend({
  components: {
    FormImport
  },

  layout: 'project',

  validate({ params, query, app }) {
    if (!['category', 'span', 'relation', 'trait'].includes(query.type as string)) {
      return false
    }
    if (/^\d+$/.test(params.id)) {
      return app.$services.project.findById(params.id).then((res: Project) => {
        return res.canDefineLabel
      })
    }
    return false
  },

  data() {
    return {
      errorMessage: ''
    }
  },

  computed: {
    projectId(): string {
      return this.$route.params.id
    },

    service(): any {
      const type = this.$route.query.type
      if (type === 'category') {
        return this.$services.categoryType
      } else if (type === 'span') {
        return this.$services.spanType
      } else if (type === 'relation') {
        return this.$services.relationType
      } else {
        return this.$services.traitType
      }
    }
  },

  methods: {
    async upload(file: File) {
      try {
        await this.service.upload(this.projectId, file)
        this.$router.push(`/projects/${this.projectId}/labels`)
      } catch (e) {
        this.errorMessage = e.message
      }
    },

    clearErrorMessage() {
      this.errorMessage = ''
    }
  }
})
</script>
