import { writable } from 'svelte/store';
import { DEFAULT_PERSONA_ID, TUTOR_PERSONAS } from '$lib/constants/tutorPersonas';
import type { TutorPersona } from '$lib/constants/tutorPersonas';

const STORAGE_KEY = 'tutorPersona';

function loadInitial(): string {
	if (typeof localStorage === 'undefined') return DEFAULT_PERSONA_ID;
	const saved = localStorage.getItem(STORAGE_KEY);
	const isValid = TUTOR_PERSONAS.some((p) => p.id === saved);
	return isValid && saved ? saved : DEFAULT_PERSONA_ID;
}

export const tutorPersonaId = writable<string>(loadInitial());

export function setPersona(id: string): void {
	if (!TUTOR_PERSONAS.some((p) => p.id === id)) return;
	tutorPersonaId.set(id);
	if (typeof localStorage !== 'undefined') {
		localStorage.setItem(STORAGE_KEY, id);
	}
}

export function getActivePersona(id: string): TutorPersona {
	return TUTOR_PERSONAS.find((p) => p.id === id) ?? TUTOR_PERSONAS[0];
}