<script lang="ts">
  import TutorSelector from '$lib/components/tutor/TutorSelector.svelte';
  import TutorPreview from '$lib/components/tutor/TutorPreview.svelte';
  import { tutorPersonaId, getActivePersona } from '$lib/stores/tutorPersona';
  import { goto } from '$app/navigation';
  import { getContext } from 'svelte';
  import { v4 as uuidv4 } from 'uuid';
  

  const i18n: any = getContext('i18n');

  $: active = getActivePersona($tutorPersonaId);

  function startNewChat() {
    const newChatId = uuidv4();
    goto(`/student/c/${newChatId}`);
  }
</script>

<div class="p-6 max-w-4xl mx-auto">
  <TutorSelector />
  <TutorPreview />

  <div class="mt-8 flex flex-col sm:flex-row items-center justify-between gap-4 p-5 rounded-2xl bg-blue-50 border border-blue-100">
    <div class="text-sm text-gray-700">
      {$i18n.t('Ready to chat with')}
      <span class="font-semibold text-blue-700">{$i18n.t(active.nameKey)}</span>
      {$i18n.t('tutor?')}
    </div>
    <button
      type="button"
      on:click={startNewChat}
      class="inline-flex items-center gap-2 px-5 py-2.5 rounded-xl bg-blue-600 text-white text-sm font-semibold hover:bg-blue-700 transition shadow-sm"
    >
      {active.icon}
      {$i18n.t('Start a new conversation')}
    </button>
  </div>
</div>