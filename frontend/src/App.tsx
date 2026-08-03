import { FormEvent, useMemo, useState } from 'react';
import axios, { AxiosError } from 'axios';
import { generateStory, StoryRequest, StoryResponse } from './api';

type FormState = {
  childName: string;
  age: string;
  animal: string;
  themes: string[];
  favoriteColor: string;
};

const initialForm: FormState = {
  childName: 'Elif',
  age: '5',
  animal: 'kedi',
  themes: ['orman'],
  favoriteColor: 'mor',
};

const themeOptions = [
  { key: 'orman', label: '🌳 Orman' },
  { key: 'deniz_alti', label: '🐠 Deniz Altı' },
  { key: 'uzay', label: '🚀 Uzay' },
  { key: 'dinozorlar', label: '🦖 Dinozorlar' },
  { key: 'prenses_ve_sato', label: '🏰 Prenses ve Şato' },
  { key: 'sihirli_dunya', label: '🧙 Sihirli Dünya' },
  { key: 'tek_boynuzlu_atlar', label: '🦄 Tek Boynuzlu Atlar' },
  { key: 'ejderhalar', label: '🐉 Ejderhalar' },
  { key: 'periler', label: '🧚 Periler' },
  { key: 'korsanlar', label: '🏴‍☠️ Korsanlar' },
  { key: 'robotlar', label: '🤖 Robotlar' },
  { key: 'trenler', label: '🚂 Trenler' },
  { key: 'ciftlik', label: '🚜 Çiftlik' },
  { key: 'gokkusagi', label: '🌈 Gökkuşağı' },
  { key: 'bulutlar', label: '☁️ Bulutlar' },
  { key: 'karlar_ulkesi', label: '❄️ Karlar Ülkesi' },
  { key: 'cicek_bahcesi', label: '🌸 Çiçek Bahçesi' },
  { key: 'kamp_macerasi', label: '🏕️ Kamp Macerası' },
  { key: 'gizemli_ada', label: '🏝️ Gizemli Ada' },
  { key: 'sirk', label: '🎪 Sirk' },
];

const storySections: Array<[keyof StoryResponse, string]> = [
  ['baslangic', 'Başlangıç'],
  ['macera', 'Macera'],
  ['sonuc', 'Sonuç'],
  ['moral', 'Moral'],
];

function getErrorMessage(caughtError: unknown): string {
  if (!isAxiosStoryError(caughtError)) {
    return 'Masal oluşturulamadı. Lütfen tekrar deneyin.';
  }

  const detail = caughtError.response?.data.detail;
  if (typeof detail === 'string') {
    return detail;
  }

  if (typeof caughtError.response?.data === 'string') {
    return caughtError.response.data;
  }

  return 'Masal oluşturulamadı. Lütfen bilgileri kontrol edip tekrar deneyin.';
}

function isAxiosStoryError(error: unknown): error is AxiosError<{ detail?: unknown }> {
  return axios.isAxiosError(error);
}

function App() {
  const [form, setForm] = useState<FormState>(initialForm);
  const [story, setStory] = useState<StoryResponse | null>(null);
  const [error, setError] = useState('');
  const [isLoading, setIsLoading] = useState(false);

  const isFormValid = useMemo(() => {
    const age = Number(form.age);
    return (
      form.childName.trim().length > 0 &&
      form.animal.trim().length > 0 &&
      form.themes.length >= 1 &&
      form.themes.length <= 3 &&
      form.favoriteColor.trim().length > 0 &&
      Number.isInteger(age) &&
      age >= 2 &&
      age <= 12
    );
  }, [form]);

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setError('');
    setStory(null);

    const age = Number(form.age);
    if (!isFormValid) {
      setError('Lütfen tüm alanları doldurun, yaşı 2 ile 12 arasında girin ve 1-3 tema seçin.');
      return;
    }

    const payload: StoryRequest = {
      child_name: form.childName.trim(),
      age,
      animal: form.animal.trim(),
      themes: form.themes,
      favorite_color: form.favoriteColor.trim(),
    };

    try {
      setIsLoading(true);
      const generatedStory = await generateStory(payload);
      setStory(generatedStory);
    } catch (caughtError) {
      setError(getErrorMessage(caughtError));
    } finally {
      setIsLoading(false);
    }
  }

  function toggleTheme(themeKey: string) {
    if (form.themes.includes(themeKey)) {
      setForm({ ...form, themes: form.themes.filter((selectedTheme) => selectedTheme !== themeKey) });
      return;
    }

    if (form.themes.length === 3) {
      setError('En fazla 3 tema seçebilirsiniz.');
      return;
    }

    setError('');
    setForm({ ...form, themes: [...form.themes, themeKey] });
  }

  return (
    <main className="page-shell">
      <section className="hero-card" aria-labelledby="page-title">
        <div className="hero-copy">
          <p className="eyebrow">Türkçe kişisel uyku masalı</p>
          <h1 id="page-title">Senin Masalın</h1>
          <p className="hero-text">
            Çocuğunuzun adını, sevdiği hayvanı ve hayalindeki temayı yazın; yumuşak,
            güvenli ve uyku öncesine uygun bir masal hazırlayalım.
          </p>
        </div>
        <div className="moon-badge" aria-hidden="true">
          <span>☾</span>
        </div>
      </section>

      <section className="workspace" aria-label="Masal oluşturma alanı">
        <form className="story-form" onSubmit={handleSubmit} noValidate>
          <div className="form-heading">
            <span>Masal bilgileri</span>
            <strong>20 tema, en fazla 3 seçim</strong>
          </div>

          <label>
            Çocuğun adı
            <input
              value={form.childName}
              onChange={(event) => setForm({ ...form, childName: event.target.value })}
              placeholder="Elif"
              required
            />
          </label>

          <label>
            Yaş
            <input
              value={form.age}
              onChange={(event) => setForm({ ...form, age: event.target.value })}
              min="2"
              max="12"
              type="number"
              required
            />
          </label>

          <label>
            Sevdiği hayvan
            <input
              value={form.animal}
              onChange={(event) => setForm({ ...form, animal: event.target.value })}
              placeholder="kedi"
              required
            />
          </label>

          <label>
            Sevdiği renk
            <input
              value={form.favoriteColor}
              onChange={(event) => setForm({ ...form, favoriteColor: event.target.value })}
              placeholder="mor"
              required
            />
          </label>

          <section className="theme-picker" aria-labelledby="theme-picker-title">
            <div className="theme-picker-heading">
              <div>
                <h2 id="theme-picker-title">Masal temaları</h2>
                <p>1 ila 3 tema seçin; ilk seçiminiz ana dünya olur.</p>
              </div>
              <span>{form.themes.length}/3</span>
            </div>

            <div className="theme-grid" role="group" aria-label="Masal teması seçenekleri">
              {themeOptions.map((theme) => {
                const isSelected = form.themes.includes(theme.key);
                return (
                  <button
                    aria-pressed={isSelected}
                    className={`theme-option${isSelected ? ' selected' : ''}`}
                    key={theme.key}
                    onClick={() => toggleTheme(theme.key)}
                    type="button"
                  >
                    {theme.label}
                  </button>
                );
              })}
            </div>
          </section>

          {error && <p className="form-error" role="alert">{error}</p>}

          <button type="submit" disabled={isLoading}>
            {isLoading ? 'Masal yazılıyor...' : 'Masalımı oluştur'}
          </button>
        </form>

        <article className="story-preview" aria-live="polite">
          {story ? (
            <>
              <p className="preview-label">Hazır masal</p>
              <h2>{story.title}</h2>
              <div className="story-pages">
                {storySections.map(([key, label]) => (
                  <section className="story-page" key={key}>
                    <h3>{label}</h3>
                    <p>{story[key]}</p>
                  </section>
                ))}
              </div>
            </>
          ) : (
            <div className="empty-preview">
              <span aria-hidden="true">✦</span>
              <h2>Masal burada belirecek</h2>
              <p>
                Formu doldurup gönderdiğinizde başlangıç, macera, sonuç ve moral bölümleri
                ayrı ayrı okunabilir şekilde gösterilir.
              </p>
            </div>
          )}
        </article>
      </section>
    </main>
  );
}

export default App;
