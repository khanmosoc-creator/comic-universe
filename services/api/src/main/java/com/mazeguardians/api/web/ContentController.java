package com.mazeguardians.api.web;

import com.mazeguardians.api.content.ContentRepository;
import com.mazeguardians.api.content.Model.ComicCharacter;
import com.mazeguardians.api.content.Model.Issue;
import com.mazeguardians.api.content.Model.IssueSummary;
import java.time.Duration;
import java.util.List;
import org.springframework.http.CacheControl;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;
import org.springframework.web.server.ResponseStatusException;

/** Read-only endpoints. Contract: docs/api/openapi.yaml. */
@RestController
@RequestMapping(path = "/api/v1", produces = MediaType.APPLICATION_JSON_VALUE)
public class ContentController {

    private static final CacheControl CACHE = CacheControl.maxAge(Duration.ofMinutes(10)).cachePublic();

    private final ContentRepository repository;

    public ContentController(ContentRepository repository) {
        this.repository = repository;
    }

    @GetMapping("/issues")
    public ResponseEntity<List<IssueSummary>> issues() {
        return ok(repository.issues().stream().map(IssueSummary::of).toList());
    }

    @GetMapping("/issues/{slug}")
    public ResponseEntity<Issue> issue(@PathVariable String slug) {
        return ok(repository.issue(slug).orElseThrow(() -> notFound("Issue not found")));
    }

    @GetMapping("/characters/{kind}")
    public ResponseEntity<List<ComicCharacter>> characters(@PathVariable String kind) {
        return ok(repository.characters(kind).orElseThrow(() -> notFound("Unknown character kind")));
    }

    @GetMapping("/characters/{kind}/{id}")
    public ResponseEntity<ComicCharacter> character(@PathVariable String kind, @PathVariable String id) {
        return ok(repository.character(kind, id).orElseThrow(() -> notFound("Character not found")));
    }

    private static <T> ResponseEntity<T> ok(T body) {
        return ResponseEntity.ok().cacheControl(CACHE).body(body);
    }

    private static ResponseStatusException notFound(String reason) {
        return new ResponseStatusException(HttpStatus.NOT_FOUND, reason);
    }
}
