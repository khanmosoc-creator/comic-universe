package com.mazeguardians.api.content;

import com.fasterxml.jackson.databind.ObjectMapper;
import com.mazeguardians.api.content.Model.CharacterCatalog;
import com.mazeguardians.api.content.Model.ComicCharacter;
import com.mazeguardians.api.content.Model.Issue;
import java.io.IOException;
import java.io.InputStream;
import java.util.List;
import java.util.Optional;
import org.springframework.core.io.ClassPathResource;
import org.springframework.stereotype.Component;

/** Loads the packaged content JSON once at start-up. Swap for a CMS/database later behind the same methods. */
@Component
public class ContentRepository {

    private static final List<String> ISSUE_FILES = List.of("content/issue-001.json");

    private final CharacterCatalog catalog;
    private final List<Issue> issues;

    public ContentRepository(ObjectMapper mapper) throws IOException {
        this.catalog = read(mapper, "content/characters.json", CharacterCatalog.class);
        this.issues = ISSUE_FILES.stream().map(path -> readUnchecked(mapper, path)).toList();
    }

    public List<Issue> issues() {
        return issues;
    }

    public Optional<Issue> issue(String slug) {
        return issues.stream().filter(i -> i.slug().equals(slug)).findFirst();
    }

    public Optional<List<ComicCharacter>> characters(String kind) {
        return switch (kind) {
            case "heroes" -> Optional.of(catalog.heroes());
            case "villains" -> Optional.of(catalog.villains());
            default -> Optional.empty();
        };
    }

    public Optional<ComicCharacter> character(String kind, String id) {
        return characters(kind).flatMap(list -> list.stream().filter(c -> c.id().equals(id)).findFirst());
    }

    private static <T> T read(ObjectMapper mapper, String path, Class<T> type) throws IOException {
        try (InputStream in = new ClassPathResource(path).getInputStream()) {
            return mapper.readValue(in, type);
        }
    }

    private static Issue readUnchecked(ObjectMapper mapper, String path) {
        try {
            return read(mapper, path, Issue.class);
        } catch (IOException e) {
            throw new IllegalStateException("Could not load " + path, e);
        }
    }
}
