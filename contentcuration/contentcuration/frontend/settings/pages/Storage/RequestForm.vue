<template>

  <form @submit.prevent="submit">

    <Banner
      :value="Boolean(errorCount())"
      error
      :text="errorText()"
      class="my-2"
    />

    <!-- Nature of content -->
    <h3>{{ $tr('natureOfYourContentLabel') }}</h3>
    <KTextbox
      v-model="storage"
      :label="$tr('storageAmountRequestedPlaceholder')"
      :invalid="errors.storage"
      :invalidText="$tr('fieldRequiredText')"
    />
    <KTextbox
      v-model="resource_count"
      :invalid="errors.resource_count"
      :invalidText="$tr('fieldRequiredText')"
      :label="$tr('approximatelyHowManyResourcesLabel')"
      :placeholder="$tr('numberOfResourcesPlaceholder')"
      :floatingLabel="false"
    />
    <KTextbox
      v-model="resource_size"
      :label="$tr('averageSizeOfResourceLabel')"
      :placeholder="$tr('sizePlaceholder')"
      :floatingLabel="false"
    />
    <KTextbox
      v-model="kind"
      :invalid="errors.kind"
      :invalidText="$tr('fieldRequiredText')"
      :label="$tr('kindOfContentQuestionLabel')"
      :placeholder="$tr('typeOfContentPlaceholder')"
      :floatingLabel="false"
      :textArea="true"
    />
    <KTextbox
      v-model="creators"
      :label="$tr('authorLabel')"
      :placeholder="$tr('responsePlaceholder')"
      :floatingLabel="false"
      :textArea="true"
    />
    <KTextbox
      v-model="sample_link"
      :invalid="errors.sample_link"
      :invalidText="$tr('fieldRequiredText')"
      :label="$tr('provideSampleLinkLabel')"
      :placeholder="$tr('pasteLinkPlaceholder')"
      :floatingLabel="false"
    />

    <!-- Who can use content -->
    <h3>{{ $tr('whoCanUseContentLabel') }}</h3>
    <div class="mt-2">
      <div v-if="errors.license" style="color: red">
        {{ $tr('fieldRequiredText') }}
      </div>
      <label>{{ $tr('licensingQuestionLabel') }}</label>
    </div>
    <KCheckbox
      v-for="license_name in licenseOptions"
      :key="license_name"
      :label="translateConstant(license_name)"
      :checked="license.includes(license_name)"
      @change="toggleLicense(license_name)"
    />

    <div class="mt-3 mb-1">
      <label>{{ $tr('willYouMakeYourChannelPublicLabel') }}</label>
    </div>
    <MultiSelect
      v-model="publicChannels"
      :label="$tr('selectAllThatApplyPlaceholder')"
      :items="publicChannelOptions"
      :item-value="channelName"
      item-text="name"
    />

    <!-- How are you using your content -->
    <h3>{{ $tr('howAreYouUsingYourContentLabel') }}</h3>
    <KTextbox
      v-model="audience"
      :invalid="errors.audience"
      :invalidText="$tr('fieldRequiredText')"
      :label="$tr('intendedAudienceLabel')"
      :placeholder="$tr('audiencePlaceholder')"
      textArea
    />
    <div class="mt-3 mb-1">
      <label>{{ $tr('targetRegionsLabel') }}</label>
    </div>
    <CountryField v-model="location" />
    <KTextbox
      v-model="import_count"
      :invalid="errors.import_count"
      :invalidText="$tr('fieldRequiredText')"
      :label="$tr('howOftenImportedToKolibriLabel')"
      :placeholder="$tr('storageAmountRequestedPlaceholder')"
      :floatingLabel="false"
    />

    <h3>{{ $tr('usageLabel') }}</h3>
    <div class="mt-2">
      <div v-if="errors.org_or_personal" style="color: red">
        {{ $tr('fieldRequiredText') }}
      </div>
      <label>{{ $tr('organizationalAffiliationLabel') }}</label>
    </div>
    <KRadioButton
      v-for="affiliation in affiliationOptions"
      :key="affiliation.value"
      v-model="org_or_personal"
      :value="affiliation.value"
      :invalid="errors.org_or_personal"
      :invalidText="$tr('fieldRequiredText')"
      :label="affiliation.text"
    />
    <KTextbox
      v-model="organization"
      :invalid="errors.organization"
      :invalidText="$tr('fieldRequiredText')"
      label=" "
      :placeholder="$tr('organizationNamePlaceholder')"
      :floatingLabel="false"
      style="margin-left: 36px;"
      :disabled="!orgSelected"
    />

    <div class="mt-3 mb-1">
      <div v-if="errors.organization_type" style="color: red">
        {{ $tr('fieldRequiredText') }}
      </div>
      <label :style="{color: orgSelected? 'black' : 'gray'}">
        {{ $tr('typeOfOrganizationLabel') }}
      </label>
    </div>
    <KRadioButton
      v-for="orgType in organizationTypeOptions"
      :key="orgType.value"
      v-model="organization_type"
      :value="orgType.value"
      :invalid="errors.organization_type"
      :invalidText="$tr('fieldRequiredText')"
      :label="orgType.text"
      :disabled="!orgSelected"
    />
    <KTextbox
      v-model="organization_other"
      :invalid="errors.organization_other"
      :invalidText="$tr('fieldRequiredText')"
      :label="' '"
      :placeholder="$tr('organizationNamePlaceholder')"
      :floatingLabel="false"
      style="margin-left: 36px;"
      :disabled="!orgSelected || !orgTypeOtherSelected"
    />

    <!-- Time constraint -->
    <div class="mb-1">
      <label>{{ $tr('timelineLabel') }}</label>
    </div>
    <KRadioButton
      v-for="constraint in timeConstraintOptions"
      :key="constraint.value"
      v-model="time_constraint"
      :value="constraint.value"
      :label="constraint.text"
    />

    <!-- Use case -->
    <div class="mt-4 mb-1">
      <label>{{ $tr('explainNeedsInDetailLabel') }}</label>
    </div>
    <KTextbox
      v-model="message"
      :invalid="errors.message"
      :invalidText="$tr('fieldRequiredText')"
      :floatingLabel="false"
      label=" "
      :placeholder="$tr('responsePlaceholder')"
      textArea
    />

    <div class="my-5">
      <KButton primary :text="$tr('sendRequestAction')" @click="submit" />
    </div>

  </form>

</template>


<script>

  import { mapActions, mapState } from 'vuex';
  import { generateFormMixin } from '../mixins';
  import { constantsTranslationMixin } from 'shared/mixins';
  import { LicensesList } from 'shared/leUtils/Licenses';
  import CountryField from 'shared/views/form/CountryField';
  import MultiSelect from 'shared/views/form/MultiSelect';
  import Banner from 'shared/views/Banner';

  const formMixin = generateFormMixin({
    storage: { required: true },
    kind: { required: true },
    resource_count: { required: true },
    resource_size: { required: false },
    creators: { required: true },
    sample_link: { required: false },
    license: {
      required: true,
      multiSelect: true,
    },
    publicChannels: {
      required: false,
      multiSelect: true,
    },
    audience: { required: true },
    location: {
      required: false,
      multiSelect: true,
    },
    import_count: { required: true },
    org_or_personal: { required: true },
    organization: {
      required: true,
      validator: (value, vm) => {
        return !vm.orgSelected || Boolean(value);
      },
    },
    organization_type: {
      required: true,
      validator(value, vm) {
        return !vm.orgSelected || Boolean(value);
      },
    },
    organization_other: {
      required: true,
      validator(value, vm) {
        return !vm.orgSelected || !vm.orgTypeOtherSelected || Boolean(value);
      },
    },
    time_constraint: { required: false },
    message: { required: true },
  });

  export default {
    name: 'RequestForm',
    components: {
      CountryField,
      MultiSelect,
      Banner,
    },
    mixins: [constantsTranslationMixin, formMixin],
    computed: {
      ...mapState({
        user: state => state.session.currentUser,
      }),
      orgSelected() {
        return this.org_or_personal === 'Organization';
      },
      orgTypeOtherSelected() {
        return this.organization_type === 'Other';
      },
      licenseOptions() {
        return LicensesList.map(l => l.license_name);
      },
      affiliationOptions() {
        return [
          { value: 'Not affiliated', text: this.$tr('notAffiliatedLabel') },
          { value: 'Organization', text: this.$tr('uploadingOnBehalfLabel') },
        ];
      },
      organizationTypeOptions() {
        return [
          { value: 'Grassroots and/or volunteer initiative', text: this.$tr('grassrootsLabel') },
          { value: 'Small NGO with annual budget < $25K', text: this.$tr('smallNgoLabel') },
          { value: 'Medium-sized NGO with budget < $500K', text: this.$tr('mediumNgoLabel') },
          {
            value: 'Larger INGO or other international agency',
            text: this.$tr('largeIntlNgoLabel'),
          },
          { value: 'For-profit or social enterprise company', text: this.$tr('forProfitLabel') },
          { value: 'Other', text: this.$tr('otherLabel') },
        ];
      },
      timeConstraintOptions() {
        return [
          { value: '1 week', text: this.$tr('oneWeekLabel') },
          { value: '2-4 weeks', text: this.$tr('twoToFourWeeksLabel') },
          { value: '1-2 months', text: this.$tr('coupleMonthsLabel') },
          { value: '3-6 months', text: this.$tr('threeToSixMonthsLabel') },
          { value: '6+ months', text: this.$tr('sixPlusMonthsLabel') },
          { value: 'Unknown', text: this.$tr('unknownLabel') },
        ];
      },
      publicChannelOptions() {
        return this.user.channels;
      },
    },
    methods: {
      ...mapActions('settings', ['requestStorage']),
      toggleLicense(license) {
        if (this.license.includes(license)) {
          this.license = this.license.filter(l => l !== license);
        } else {
          // Vue doesn't register push, so use explicit assignment
          this.license = this.license.concat([license]);
        }
      },
      channelName(channel) {
        return `${channel.name} (${channel.id})`;
      },

      // eslint-disable-next-line kolibri/vue-no-unused-methods
      onSubmit(formData) {
        // Convert list-based fields to comma-separated string
        // Can use commas as storage email needs to be in English
        formData.license = formData.license.join(', ');
        formData.public = formData.publicChannels.join(', ');
        formData.location = formData.location.join(', ');

        // Parse organization-related strings
        // Leave untranslated so request will be in English
        formData.organization_type = 'Not applicable';
        if (this.orgSelected) {
          formData.organization_type = this.orgTypeOtherSelected
            ? this.organization_other
            : this.organization_type;
        }
        formData.uploading_for = this.orgSelected
          ? `${this.organization} (organization)`
          : this.org_or_personal;

        // Send request
        this.requestStorage(formData)
          .then(() => {
            this.$store.dispatch('showSnackbar', { text: this.$tr('requestSent') });
            this.reset();
          })
          .catch(() => {
            this.$store.dispatch('showSnackbar', { text: this.$tr('requestFailed') });
          });
      },
    },
    $trs: {
      /* Nature of your content */
      natureOfYourContentLabel: 'Nature of your content',
      storageAmountRequestedPlaceholder: 'Storage amount requested (e.g. 10GB)',
      approximatelyHowManyResourcesLabel:
        'Approximately how many individual resources are you planning to upload?',
      numberOfResourcesPlaceholder: 'Number of resources',
      averageSizeOfResourceLabel: 'Average size of each resource',
      sizePlaceholder: 'Size',
      kindOfContentQuestionLabel: 'What kind of content are you uploading? Please specify',
      typeOfContentPlaceholder: 'Type of content',
      authorLabel:
        'Who is the author (creator), curator (organizer), and/or aggregator (maintainer) of your content? Please specify',
      responsePlaceholder: 'Response',
      provideSampleLinkLabel:
        'Please provide a link to a sample of your content (on Studio or from source site)',
      pasteLinkPlaceholder: 'Paste link here',

      /* Who can use your content */
      whoCanUseContentLabel: 'Who can use your content?',
      licensingQuestionLabel:
        'What is the licensing of the content you are uploading? (Check all that apply)',
      willYouMakeYourChannelPublicLabel:
        'If the content is openly licensed, would you be willing to consider making your channels public to other Kolibri users if requested in the future?',
      selectAllThatApplyPlaceholder: 'Select all that apply',

      /* How are you using your content */
      howAreYouUsingYourContentLabel: 'How are you using your content?',
      intendedAudienceLabel:
        'Who is the intended audience for your channel? How big is your audience?',
      audiencePlaceholder: 'In-school learners, adult learners, teachers, etc',
      targetRegionsLabel: 'What is the target region(s) for your content (if applicable)',
      howOftenImportedToKolibriLabel:
        'How many times will this content be imported from Studio into new Kolibri installations per month, on average?',

      /* Tell us more about your use of Kolibri */
      usageLabel: 'Tell us more about your use of Kolibri',
      organizationalAffiliationLabel: 'Organizational affiliation',
      notAffiliatedLabel: 'I am not affiliated with an organization for this work',
      uploadingOnBehalfLabel: 'I am uploading content on behalf of:',
      organizationNamePlaceholder: 'Organization name',
      typeOfOrganizationLabel:
        'What type of organization or group is coordinating the use of Kolibri (if applicable)?',
      grassrootsLabel: 'Grassroots and/or volunteer initiative',
      smallNgoLabel: 'Small NGO with annual budget < $25k',
      mediumNgoLabel: 'Medium-sized NGO with budget < $500k',
      largeIntlNgoLabel: 'Larger INGO or other international agency',
      forProfitLabel: 'For-profit or social enterprise company',
      otherLabel: 'Other',

      /* Time constraints */
      timelineLabel:
        'To better understand the time sensitive nature of your request, please indicate an approximate timeline by when you need this additional storage:',
      oneWeekLabel: '1 week',
      twoToFourWeeksLabel: '2-4 weeks',
      coupleMonthsLabel: '1-2 months',
      threeToSixMonthsLabel: '3-6 months',
      sixPlusMonthsLabel: '6+ months',
      unknownLabel: 'Unknown',

      /* Use case */
      explainNeedsInDetailLabel:
        'Please write a paragraph explaining your needs and use case for Kolibri Studio, and how it will integrate into your programs. Include information about who is curating, deploying, and using the content. Is this work being coordinated by an organization, as part of an educational program? Include justification for the additional space being requested and explanation of the time sensitive nature of your request.',

      /* Other strings */
      fieldRequiredText: '* This field is required',
      sendRequestAction: 'Send request',
      requestSent: 'Your storage request has been submitted for processing.',
      requestFailed: 'Unable to send request. Please try again.',
    },
  };

</script>


<style scoped>
  h3 {
    margin-top: 32px;
    margin-bottom: 8px;
  }
</style>
