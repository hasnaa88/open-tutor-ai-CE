<!-- src/lib/components/ClassroomSeatingChart.svelte -->
<script lang="ts">
	import { getContext, onMount, onDestroy, createEventDispatcher } from 'svelte';
	import { browser } from '$app/environment';
	import type { StudentOut } from '$lib/types/classroom';

	const i18n = getContext('i18n');
	const dispatch = createEventDispatcher();

	export let students: StudentOut[] = [];

	let container: HTMLDivElement;
	let webglUnavailable = false;
	let cleanup: (() => void) | null = null;

	// Same palette as StudentAvatar.svelte, expressed as Three.js hex colors.
	const AVATAR_COLORS = [
		0x3b82f6, // blue-500
		0x10b981, // emerald-500
		0xf59e0b, // amber-500
		0xa855f7, // purple-500
		0xec4899, // pink-500
		0x14b8a6, // teal-500
		0x6366f1, // indigo-500
		0xf43f5e // rose-500
	];

	const colorFor = (value: string) => {
		let hash = 0;
		for (let i = 0; i < value.length; i++) hash = (hash << 5) - hash + value.charCodeAt(i);
		return AVATAR_COLORS[Math.abs(hash) % AVATAR_COLORS.length];
	};

	const initialsOf = (value: string) =>
		value
			.trim()
			.split(/\s+/)
			.slice(0, 2)
			.map((part) => part[0]?.toUpperCase() ?? '')
			.join('');

	async function setupScene() {
		const THREE = await import('three');
		const { OrbitControls } = await import('three/examples/jsm/controls/OrbitControls.js');

		const width = container.clientWidth;
		const height = container.clientHeight;

		const scene = new THREE.Scene();
		scene.background = new THREE.Color(0xf4f7fe);

		const camera = new THREE.PerspectiveCamera(50, width / height, 0.1, 100);
		camera.position.set(0, 4.5, 6.5);

		const renderer = new THREE.WebGLRenderer({ antialias: true });
		renderer.setSize(width, height);
		renderer.setPixelRatio(Math.min(window.devicePixelRatio, 2));
		container.appendChild(renderer.domElement);

		const controls = new OrbitControls(camera, renderer.domElement);
		controls.target.set(0, 0.6, 0);
		controls.maxPolarAngle = Math.PI / 2.1;
		controls.minDistance = 3;
		controls.maxDistance = 14;
		controls.update();

		scene.add(new THREE.AmbientLight(0xffffff, 0.8));
		const dirLight = new THREE.DirectionalLight(0xffffff, 0.6);
		dirLight.position.set(3, 6, 4);
		scene.add(dirLight);

		const floor = new THREE.Mesh(
			new THREE.PlaneGeometry(24, 24),
			new THREE.MeshStandardMaterial({ color: 0xe2e8f0 })
		);
		floor.rotation.x = -Math.PI / 2;
		scene.add(floor);

		const board = new THREE.Mesh(
			new THREE.BoxGeometry(3.2, 1.1, 0.08),
			new THREE.MeshStandardMaterial({ color: 0x334155 })
		);
		board.position.set(0, 1.3, -2.8);
		scene.add(board);

		const cols = Math.max(1, Math.ceil(Math.sqrt(students.length)));
		const spacingX = 1.8;
		const spacingZ = 1.5;
		const avatarSprites: any[] = [];

		const buildDesk = (x: number, z: number) => {
			const group = new THREE.Group();

			const tableMat = new THREE.MeshStandardMaterial({ color: 0xe2e8f0 });
			const table = new THREE.Mesh(new THREE.BoxGeometry(1.4, 0.08, 0.8), tableMat);
			table.position.set(0, 0.5, 0);
			group.add(table);

			const legMat = new THREE.MeshStandardMaterial({ color: 0x94a3b8 });
			const legGeo = new THREE.BoxGeometry(0.06, 0.5, 0.06);
			for (const [lx, lz] of [
				[0.6, 0.32],
				[-0.6, 0.32],
				[0.6, -0.32],
				[-0.6, -0.32]
			]) {
				const leg = new THREE.Mesh(legGeo, legMat);
				leg.position.set(lx, 0.25, lz);
				group.add(leg);
			}

			const baseMat = new THREE.MeshStandardMaterial({ color: 0x475569 });
			const base = new THREE.Mesh(new THREE.BoxGeometry(0.18, 0.05, 0.12), baseMat);
			base.position.set(0, 0.565, -0.2);
			group.add(base);

			const screen = new THREE.Mesh(
				new THREE.BoxGeometry(0.42, 0.28, 0.03),
				new THREE.MeshStandardMaterial({ color: 0x1e293b })
			);
			screen.position.set(0, 0.78, -0.25);
			group.add(screen);

			const glow = new THREE.Mesh(
				new THREE.PlaneGeometry(0.36, 0.22),
				new THREE.MeshStandardMaterial({
					color: 0x3b82f6,
					emissive: 0x3b82f6,
					emissiveIntensity: 0.4
				})
			);
			glow.position.set(0, 0.78, -0.235);
			group.add(glow);

			const chairMat = new THREE.MeshStandardMaterial({ color: 0x64748b });
			const seat = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.06, 0.4), chairMat);
			seat.position.set(0, 0.3, 0.55);
			group.add(seat);
			const back = new THREE.Mesh(new THREE.BoxGeometry(0.4, 0.4, 0.06), chairMat);
			back.position.set(0, 0.5, 0.74);
			group.add(back);

			group.position.set(x, 0, z);
			return group;
		};

		const makeAvatarTexture = (name: string) => {
			const canvas = document.createElement('canvas');
			canvas.width = 128;
			canvas.height = 128;
			const ctx = canvas.getContext('2d');
			if (ctx) {
				const hex = '#' + colorFor(name).toString(16).padStart(6, '0');
				ctx.fillStyle = hex;
				ctx.beginPath();
				ctx.arc(64, 64, 60, 0, Math.PI * 2);
				ctx.fill();
				ctx.fillStyle = '#ffffff';
				ctx.font = 'bold 48px sans-serif';
				ctx.textAlign = 'center';
				ctx.textBaseline = 'middle';
				ctx.fillText(initialsOf(name), 64, 68);
			}
			const texture = new THREE.CanvasTexture(canvas);
			texture.needsUpdate = true;
			return texture;
		};

		students.forEach((student, i) => {
			const row = Math.floor(i / cols);
			const col = i % cols;
			const rowCount = Math.min(cols, students.length - row * cols);
			const x = (col - (rowCount - 1) / 2) * spacingX;
			const z = row * spacingZ - 0.5;

			scene.add(buildDesk(x, z));

			const sprite = new THREE.Sprite(
				new THREE.SpriteMaterial({ map: makeAvatarTexture(student.name) })
			);
			sprite.scale.set(0.5, 0.5, 1);
			sprite.position.set(x, 1.15, z + 0.5);
			sprite.userData.student = student;
			scene.add(sprite);
			avatarSprites.push(sprite);
		});

		const raycaster = new THREE.Raycaster();
		const pointer = new THREE.Vector2();

		const onPointerDown = (event: PointerEvent) => {
			const rect = renderer.domElement.getBoundingClientRect();
			pointer.x = ((event.clientX - rect.left) / rect.width) * 2 - 1;
			pointer.y = -((event.clientY - rect.top) / rect.height) * 2 + 1;
			raycaster.setFromCamera(pointer, camera);
			const hits = raycaster.intersectObjects(avatarSprites);
			if (hits.length > 0) {
				dispatch('selectStudent', hits[0].object.userData.student as StudentOut);
			}
		};
		renderer.domElement.addEventListener('pointerdown', onPointerDown);

		let animationId: number;
		const animate = () => {
			animationId = requestAnimationFrame(animate);
			controls.update();
			renderer.render(scene, camera);
		};
		animate();

		const handleResize = () => {
			const w = container.clientWidth;
			const h = container.clientHeight;
			camera.aspect = w / h;
			camera.updateProjectionMatrix();
			renderer.setSize(w, h);
		};
		const resizeObserver = new ResizeObserver(handleResize);
		resizeObserver.observe(container);

		return () => {
			cancelAnimationFrame(animationId);
			resizeObserver.disconnect();
			renderer.domElement.removeEventListener('pointerdown', onPointerDown);
			scene.traverse((obj: any) => {
				obj.geometry?.dispose?.();
				if (obj.material) {
					const materials = Array.isArray(obj.material) ? obj.material : [obj.material];
					for (const mat of materials) {
						mat.map?.dispose?.();
						mat.dispose?.();
					}
				}
			});
			renderer.dispose();
			if (renderer.domElement.parentElement === container) {
				container.removeChild(renderer.domElement);
			}
		};
	}

	onMount(() => {
		if (!browser || students.length === 0) return;
		setupScene()
			.then((dispose) => {
				cleanup = dispose;
			})
			.catch(() => {
				webglUnavailable = true;
			});
	});

	onDestroy(() => {
		cleanup?.();
	});
</script>

<div data-testid="seating-chart" class="space-y-2">
	{#if students.length === 0}
		<p class="text-center text-sm text-gray-500 dark:text-gray-400 py-8">
			{$i18n.t('No students enrolled yet')}
		</p>
	{:else if webglUnavailable}
		<p class="text-center text-sm text-gray-500 dark:text-gray-400 py-8">
			{$i18n.t('3D view is not available in this browser')}
		</p>
	{:else}
		<p class="text-xs text-gray-400 dark:text-gray-500 text-center">
			{$i18n.t('Drag to rotate · Scroll to zoom · Click a student to view their info')}
		</p>
		<div
			bind:this={container}
			data-testid="seating-chart-3d"
			class="w-full h-[420px] rounded-lg overflow-hidden cursor-grab active:cursor-grabbing"
		></div>
	{/if}
</div>
