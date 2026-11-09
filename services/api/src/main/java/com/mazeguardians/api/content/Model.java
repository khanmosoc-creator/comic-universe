package com.mazeguardians.api.content;

import java.util.List;

/** JSON contract shared with apps/web/src/types.ts. Field names must stay in sync. */
public final class Model {
    private Model() {
    }

    public record Colors(String primary, String accent, String ink) {
    }

    public record Stat(String label, int value) {
    }

    public record ComicCharacter(
            String id,
            String name,
            String role,
            String tagline,
            String image,
            String imageAlt,
            Colors colors,
            List<String> powers,
            String personality,
            String catchphrase,
            List<String> funFacts,
            List<Stat> stats,
            String inspiredBy,
            String scheme,
            String weakness) {
    }

    public record Minions(String name, String description) {
    }

    public record CharacterCatalog(List<ComicCharacter> heroes, List<ComicCharacter> villains, Minions minions) {
    }

    public record ImageRef(String src, String fallback, int width, int height, String alt) {
    }

    public record Dialogue(String speaker, String text, String kind) {
    }

    public record Panel(String id, ImageRef image, String alt, String source, String caption, String sfx, List<Dialogue> dialogue) {
    }

    public record NextIssue(int number, String title, String teaser) {
    }

    public record Issue(
            String id,
            String slug,
            int number,
            String title,
            String tagline,
            String synopsis,
            String readingTime,
            String ageNote,
            ImageRef cover,
            List<Panel> panels,
            NextIssue nextIssue) {
    }

    public record IssueSummary(String slug, int number, String title, String tagline, ImageRef cover, int panelCount) {
        public static IssueSummary of(Issue issue) {
            return new IssueSummary(issue.slug(), issue.number(), issue.title(), issue.tagline(), issue.cover(), issue.panels().size());
        }
    }
}
