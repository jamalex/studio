<template>

  <div>
    <h1 class="subheading">
      {{ $tr('subtitlesHeader') }}
      <HelpTooltip :text="$tr('acceptedFormatsTooltip', {extensions})" bottom />
    </h1>
    <SupplementaryList
      :presetID="subtitlePreset.id"
      :addText="$tr('addSubtitleText')"
      :readonly="readonly"
      :nodeId="nodeId"
    />
  </div>

</template>

<script>

  import uniq from 'lodash/uniq';
  import SupplementaryList from './SupplementaryList';
  import FormatPresets from 'shared/leUtils/FormatPresets';
  import HelpTooltip from 'shared/views/HelpTooltip';

  export default {
    name: 'SubtitlesList',
    components: {
      SupplementaryList,
      HelpTooltip,
    },
    props: {
      nodeId: {
        type: String,
        required: true,
      },
      readonly: {
        type: Boolean,
        default: false,
      },
    },
    computed: {
      extensions() {
        return uniq(this.subtitlePreset.allowed_formats).join(', ');
      },
      subtitlePreset() {
        return FormatPresets.get('video_subtitle');
      },
    },
    $trs: {
      subtitlesHeader: 'Subtitles',
      acceptedFormatsTooltip: 'Accepted formats: {extensions}',
      addSubtitleText: 'Add subtitle',
    },
  };

</script>

<style lang="less" scoped>

  .v-icon {
    font-size: 14pt;
    vertical-align: top;
  }

</style>
