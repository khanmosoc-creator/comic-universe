// All comic content is static JSON bundled at build time. Nothing is fetched at runtime.
import charactersJson from '../content/characters.json';
import galleryJson from '../content/gallery.json';
import issue1Json from '../content/issue-001.json';
import universeJson from '../content/universe.json';
import type { Character, CharacterKind, GalleryItem, Issue, Universe } from '../types';

export const SITE_NAME = "Super Zayd's Maze Guardians";

export const heroes = charactersJson.heroes as Character[];
export const villains = charactersJson.villains as Character[];
export const minions = charactersJson.minions;

export const issues = [issue1Json as Issue];
export const universe = universeJson as Universe;
export const gallery = galleryJson as { intro: string; items: GalleryItem[] };

export function charactersOf(kind: CharacterKind): Character[] {
  return kind === 'heroes' ? heroes : villains;
}

export function findCharacter(kind: CharacterKind, id: string): Character | undefined {
  return charactersOf(kind).find((c) => c.id === id);
}

export function findIssue(slug: string): Issue | undefined {
  return issues.find((i) => i.slug === slug);
}

export function findSketch(id: string | null): GalleryItem | undefined {
  return id ? gallery.items.find((g) => g.id === id) : undefined;
}
