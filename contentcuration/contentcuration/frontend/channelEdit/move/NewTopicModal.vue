<template>

  <MessageDialog v-model="dialog" :header="$tr('createTopic')">
    <VForm
      ref="form"
      lazy-validation
    >
      <VTextField
        v-model="title"
        :label="$tr('topicTitle')"
        outline
        :rules="titleRules"
        required
      />
    </VForm>
    <template #buttons="{close}">
      <VBtn flat data-test="close" @click="close">
        {{ $tr("cancel") }}
      </VBtn>
      <VBtn
        color="primary"
        data-test="create"
        @click="create"
      >
        {{ $tr("create") }}
      </VBtn>
    </template>
  </MessageDialog>

</template>

<script>

  import MessageDialog from 'shared/views/MessageDialog';

  export default {
    name: 'NewTopicModal',
    components: {
      MessageDialog,
    },
    props: {
      value: {
        type: Boolean,
        default: false,
      },
    },
    data() {
      return {
        title: '',
      };
    },
    computed: {
      dialog: {
        get() {
          return this.value;
        },
        set(value) {
          this.$emit('input', value);
        },
      },
      titleRules() {
        return [v => !!v || this.$tr('topicTitleRequired')];
      },
    },
    methods: {
      create() {
        if (this.$refs.form.validate()) {
          this.$emit('createTopic', this.title);
        }
      },
    },
    $trs: {
      topicTitle: 'Topic title',
      topicTitleRequired: 'Title is required',
      createTopic: 'Create new topic',
      cancel: 'Cancel',
      create: 'Create',
    },
  };

</script>

<style lang="less" scoped>
</style>
