<script lang="ts">
	import { createEventDispatcher, getContext } from 'svelte';
	import { fade } from 'svelte/transition';
	import type { SessionSummary } from '$lib/types/classroom';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let sessions: SessionSummary[] = [];
	export let selectedId: string | null = null;

	const formatDate = (iso: string) =>
		new Intl.DateTimeFormat(navigator.language || 'en-US', {
			year: 'numeric',
			month: 'short',
			day: 'numeric'
		}).format(new Date(iso));

	const formatTime = (iso: string) =>
		new Intl.DateTimeFormat(navigator.language || 'en-US', {
			hour: '2-digit',
			minute: '2-digit'
		}).format(new Date(iso));
</script>

<div data-testid="session-list" class="space-y-2 max-h-96 overflow-y-auto">
	{#each sessions as session (session.id)}
		<!-- svelte-ignore a11y-click-events-have-key-events -->
		<!-- svelte-ignore a11y-no-static-element-interactions -->
		<div
			in:fade={{ duration: 150 }}
			data-testid="session-item"
			data-session-id={session.id}
			class="p-3 rounded-lg border cursor-pointer transition-colors {selectedId === session.id
				? 'border-blue-500 bg-blue-50 dark:bg-blue-900/20'
				: 'border-gray-100 dark:border-gray-700 hover:bg-gray-50 dark:hover:bg-gray-700'}"
			on:click={() => dispatch('select', session.id)}
		>
			<div class="flex items-center justify-between text-sm">
				<span class="font-medium text-gray-900 dark:text-white">
					{formatDate(session.scheduled_at)}
				</span>
				<div class="flex items-center gap-2">
					<span class="text-gray-500 dark:text-gray-400">{formatTime(session.scheduled_at)}</span>
					{#if session.ended_at}
						<span
							class="inline-flex items-center px-2 py-0.5 rounded-full text-xs font-medium bg-gray-100 text-gray-600 dark:bg-gray-700 dark:text-gray-300"
						>
							{$i18n.t('Terminée')}
						</span>
					{:else}
						<span
							class="inline-flex items-center gap-1.5 px-2 py-0.5 rounded-full text-xs font-medium bg-green-100 text-green-700 dark:bg-green-900/30 dark:text-green-400"
						>
							<span class="relative flex w-1.5 h-1.5">
								<span
									class="absolute inline-flex w-full h-full rounded-full bg-green-500 opacity-75 animate-ping"
								></span>
								<span class="relative inline-flex w-1.5 h-1.5 rounded-full bg-green-500"></span>
							</span>
							{$i18n.t('En cours')}
						</span>
					{/if}
				</div>
			</div>
			<div class="flex items-center justify-between mt-1">
				<div class="text-xs text-gray-500 dark:text-gray-400">
					{session.present_count}
					{$i18n.t('présents')} · {session.absent_count}
					{$i18n.t('absents')} · {session.late_count}
					{$i18n.t('retards')}
				</div>
				{#if !session.ended_at}
					<button
						type="button"
						data-testid="end-session-button"
						on:click={(e) => {
							e.stopPropagation();
							dispatch('end', session.id);
						}}
						class="text-xs font-medium text-red-600 dark:text-red-400 hover:underline whitespace-nowrap"
					>
						{$i18n.t('Terminer')}
					</button>
				{/if}
			</div>
		</div>
	{/each}
</div>
