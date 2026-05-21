<!---

<script lang="ts">
	import { tutorPersonaId, getActivePersona } from '$lib/stores/tutorPersona';
	import { getContext } from 'svelte';

	const i18n: any = getContext('i18n');

	$: active = getActivePersona($tutorPersonaId);

	console.log(i18n);
	console.log(active);
</script>

<div class="mt-6">
	<div class="text-sm font-semibold text-gray-600 mb-2">
		{$i18n.t('Live preview')}
	</div>
	<div class="p-4 rounded-xl bg-gray-50 border-l-4 border-blue-500">
		<div class="flex items-center gap-2 mb-2">
			<span class="text-lg">{active.icon}</span>
			<span class="text-xs font-bold text-blue-600 uppercase">
				{$i18n.t(active.nameKey)}
			</span>
		</div>
		<p class="text-sm text-gray-700 leading-relaxed">
			{$i18n.t(active.previewKey)}
		</p>
	</div>
</div>
-->



<script lang="ts">
	import { tutorPersonaId, getActivePersona } from '$lib/stores/tutorPersona';
	import { getContext } from 'svelte';

	const i18n: any = getContext('i18n');
	$: active = getActivePersona($tutorPersonaId);
</script>

<div class="mt-8">
	<div class="flex items-center justify-between mb-4">
		<h3 class="text-base font-semibold text-gray-800">
			{$i18n.t('Live preview')}
		</h3>
		<span class="text-xs text-gray-500">
			{$i18n.t(active.nameKey)} {$i18n.t('mode active')}
		</span>
	</div>

	<div class="rounded-2xl bg-gray-50 border border-gray-200 p-5 space-y-4">
		<!-- User message bubble -->
		<div class="flex justify-end">
			<div class="max-w-[80%] rounded-2xl bg-blue-600 text-white px-4 py-2.5">
				<p class="text-sm">
					{$i18n.t('Sample question preview')}
				</p>
			</div>
		</div>

		<!-- Tutor response bubble -->
		<div class="flex justify-start">
			<div class="flex gap-3 max-w-[85%]">
				<div class="flex-shrink-0 w-9 h-9 rounded-full bg-white border border-gray-200 flex items-center justify-center text-lg">
					{active.icon}
				</div>
				<div class="flex-1">
					<div class="text-xs font-semibold text-blue-600 mb-1">
						{$i18n.t(active.nameKey)}
					</div>
					<div class="rounded-2xl bg-white border border-gray-200 px-4 py-3">
						<p class="text-sm text-gray-700 leading-relaxed">
							{$i18n.t(active.previewKey)}
						</p>
					</div>
				</div>
			</div>
		</div>
	</div>
</div>
