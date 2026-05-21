import { describe, it, expect, beforeEach } from 'vitest';
import { get } from 'svelte/store';
import { tutorPersonaId, setPersona } from './tutorPersona';

describe('tutorPersona store', () => {
	beforeEach(() => localStorage.clear());

	it('changes the active persona', () => {
		setPersona('academic');
		expect(get(tutorPersonaId)).toBe('academic');
	});

	it('persists the choice in localStorage', () => {
		setPersona('concise');
		expect(localStorage.getItem('tutorPersona')).toBe('concise');
	});

	it('ignores an invalid persona id', () => {
		setPersona('academic');
		setPersona('does_not_exist');
		expect(get(tutorPersonaId)).toBe('academic');
	});
});