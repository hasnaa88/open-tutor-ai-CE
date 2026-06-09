# Contributing to Open TutorAI 🌟

🚀 **Welcome, Contributors!** 🚀

Your interest in contributing to Open TutorAI is greatly appreciated. This document is here to guide you through the process, ensuring your contributions enhance the project effectively. Let's make Open TutorAI even better, together!

### 🚨 Reporting Issues

Noticed something off? Have an idea? Check our [Issues tab](https://github.com/Open-TutorAi/open-tutor-ai-CE/issues) to see if it's already been reported or suggested. If not, feel free to open a new issue. When reporting an issue, please follow our issue templates. These templates are designed to ensure that all necessary details are provided from the start, enabling us to address your concerns more efficiently.

> [!IMPORTANT]
>
> - **Template Compliance:** Please be aware that failure to follow the provided issue template, or not providing the requested information at all, will likely result in your issue being closed without further consideration. This approach is critical for maintaining the manageability and integrity of issue tracking.
> - **Detail is Key:** To ensure your issue is understood and can be effectively addressed, it's imperative to include comprehensive details. Descriptions should be clear, including steps to reproduce, expected outcomes, and actual results. Lack of sufficient detail may hinder our ability to resolve your issue.

### 🧭 Scope of Support

We've noticed an uptick in issues not directly related to Open TutorAI but rather to the environment it's run in, especially Docker setups. While we strive to support Docker deployment, understanding Docker fundamentals is crucial for a smooth experience.

- **Docker Deployment Support**: Open TutorAI supports Docker deployment. Familiarity with Docker is assumed. For Docker basics, please refer to the [official Docker documentation](https://docs.docker.com/get-started/overview/).

- **Advanced Configurations**: Setting up reverse proxies for HTTPS and managing Docker deployments requires foundational knowledge. There are numerous online resources available to learn these skills. Ensuring you have this knowledge will greatly enhance your experience with Open TutorAI and similar projects.

## 💡 Contributing

Looking to contribute? Great! Here's how you can help:

### ⚙️ Setup local (obligatoire avant de contribuer)

Avant de soumettre un pull request, configure ton environnement local pour valider automatiquement ton code.

**1. Installer les dépendances de développement**

```bash
pip install pre-commit
```

**2. Installer les hooks git**

```bash
pre-commit install
```

Le hook s'exécutera automatiquement à chaque `git commit`. Il vérifie :
- Le formatage Python (Black 24.8.0)
- Le formatage frontend (Prettier — JS/TS/Svelte)
- Les fichiers mal terminés ou avec des espaces superflus

**3. Valider avant de pousser**

```bash
make check
```

Cette commande exécute `make lint` (format check complet) puis `make test` (pytest + vitest). **Un push sans avoir passé `make check` sera rejeté par la CI.**

---

### 🛠 Pull Requests

We welcome pull requests. Before submitting one, please:

1. Open a discussion regarding your ideas [here](https://github.com/Open-TutorAi/open-tutor-ai-CE/discussions/new/choose).
2. Follow the project's coding standards and include tests for new features.
3. Update documentation as necessary.
4. Write clear, descriptive commit messages.
5. It's essential to complete your pull request in a timely manner. We move fast, and having PRs hang around too long is not feasible. If you can't get it done within a reasonable time frame, we may have to close it to keep the project moving forward.

#### 📁 Project Structure Guidelines

The project uses a **root-driven architecture** since v1.0. Keep this layout in mind when adding new files:

**Python application — project root**

- Use the approved root packages: `accounts/`, `learning/`, `ai/`, `content/`, `governance/`, `system/`, `gateway/`, `data/`, `common/`, and `config/`
- Domain code follows the pattern: `repository.py` → `service.py` → `gateway/http/routers/<public_namespace>.py`
- Keep RAG knowledge bases under `ai/retrieval/knowledge/`, not under `content/`
- Keep AI audio/image capabilities under `ai/media/`, not as a root `media/` package
- New routes must be registered in `gateway/http/app.py` and covered by `tests/test_contract_coverage.py`

**Frontend (SvelteKit — `ui/` subdirectory)**

- ✅ Reusable or shared components go inside `ui/src/lib/components/`
  - Organize by feature or domain (e.g., `components/tutor/`, `components/dashboard/`)
- ✅ Route-specific pages go inside `ui/src/routes/`
- ✅ API client functions go inside `ui/src/lib/apis/<domain>/index.ts`
- ❌ Avoid placing components outside their designated folders

> **Tip:** Every new `fetch()` call in `ui/src/lib/apis/` must have a matching API endpoint — the contract test will catch the gap in CI.

### 📚 Documentation & Tutorials

Help us make Open TutorAI more accessible by improving documentation, writing tutorials, or creating guides on setting up and optimizing the Tutor AI.

### 🌐 Translations and Internationalization

Help us make Open Tutor AI available to a wider audience. In this section, we'll guide you through the process of adding new translations to the project.

We use JSON files to store translations. You can find the existing translation files in the `ui/src/lib/i18n/locales` directory. Each directory corresponds to a specific language, for example, `en-US` for English (US), `fr-FR` for French (France) and so on. You can refer to [ISO 639 Language Codes](http://www.lingoes.net/en/translator/langcode.htm) to find the appropriate code for a specific language.

To add a new language:

- Create a new directory in the `ui/src/lib/i18n/locales` path with the appropriate language code as its name. For instance, if you're adding translations for Spanish (Spain), create a new directory named `es-ES`.
- Copy the American English translation file(s) (from `en-US` directory in `src/lib/i18n/locale`) to this new directory and update the string values in JSON format according to your language. Make sure to preserve the structure of the JSON object.
- Add the language code and its respective title to languages file at `src/lib/i18n/locales/languages.json`.

### 🤔 Questions & Feedback

Got questions or feedback? Join our [Discord community](https://discord.gg/BTQtE2deEm) or open an issue. We're here to help!

## 🙏 Thank You!

Your contributions, big or small, make a significant impact on Open Tutor AI. We're excited to see what you bring to the project!

Together, let's create an even more powerful tool for the community. 🌟
