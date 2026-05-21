<script lang="ts">
	import { tutorPersonaId, setPersona, getActivePersona } from '$lib/stores/tutorPersona';
	import { TUTOR_PERSONAS } from '$lib/constants/tutorPersonas';
	import { getContext } from 'svelte';

	const i18n: any = getContext('i18n');
	let saved = false;

	function choose(id: string) {
		setPersona(id);
		saved = true;
		setTimeout(() => (saved = false), 2000);
	}

	$: active = getActivePersona($tutorPersonaId);
</script>

<div class="p-4">
	<h2 class="text-xl font-semibold mb-1">
		{$i18n.t('Tutor Personalization')}
	</h2>
	<p class="text-sm text-gray-500 mb-4">
		{$i18n.t("Adjust your AI's personality to match your learning style.")}
	</p>

	<div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
		{#each TUTOR_PERSONAS as persona}
			<button
				type="button"
				on:click={() => choose(persona.id)}
				class="text-left p-4 rounded-xl border transition
					{$tutorPersonaId === persona.id
						? 'border-blue-500 ring-2 ring-blue-200'
						: 'border-gray-200 hover:border-gray-300'}"
			>
				<div class="flex items-center justify-between">
					<span class="text-2xl">{persona.icon}</span>
					{#if $tutorPersonaId === persona.id}
						<span class="text-xs font-bold text-blue-600">
							{$i18n.t('ACTIVE')}
						</span>
					{/if}
				</div>
				<div class="font-semibold mt-2">{$i18n.t(persona.nameKey)}</div>
				<div class="text-sm text-gray-500">{$i18n.t(persona.descKey)}</div>
			</button>
		{/each}
	</div>

	{#if saved}
		<div class="text-sm text-green-600 mt-3">
			{$i18n.t('Preferences saved')}
		</div>
	{/if}
</div>