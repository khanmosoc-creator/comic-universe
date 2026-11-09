export interface Stat {
  label: string;
  value: number;
}

export interface Character {
  id: string;
  name: string;
  role: string;
  tagline: string;
  image: string;
  imageAlt: string;
  colors: { primary: string; accent: string; ink: string };
  powers: string[];
  personality: string;
  catchphrase: string;
  funFacts: string[];
  stats: Stat[];
  /** Slug of the owner sketch that inspired this character, if any. */
  inspiredBy: string | null;
  scheme?: string;
  weakness?: string;
}

export type CharacterKind = 'heroes' | 'villains';

export interface ImageRef {
  src: string;
  /** PNG fallback when src is WebP. */
  fallback?: string;
  width: number;
  height: number;
}

export type DialogueKind = 'speech' | 'shout' | 'thought';

export interface Dialogue {
  speaker: string;
  text: string;
  kind: DialogueKind;
}

export interface Panel {
  id: string;
  image: ImageRef;
  alt: string;
  /** owner = hand-drawn sketch supplied by the site owner; studio = original vector art made for the site */
  source: 'owner' | 'studio';
  caption?: string;
  sfx?: string;
  dialogue: Dialogue[];
}

export interface Issue {
  id: string;
  slug: string;
  number: number;
  title: string;
  tagline: string;
  synopsis: string;
  readingTime: string;
  ageNote: string;
  cover: ImageRef & { alt: string };
  panels: Panel[];
  nextIssue: { number: number; title: string; teaser: string };
}

export interface GalleryItem extends ImageRef {
  id: string;
  title: string;
  alt: string;
  note: string;
  usedIn: string;
}

export interface Place {
  name: string;
  color: string;
  text: string;
}

export interface Universe {
  intro: string;
  map: ImageRef & { alt: string };
  places: Place[];
  code: { title: string; rules: string[] };
  timeline: { label: string; title: string; status: string }[];
}
