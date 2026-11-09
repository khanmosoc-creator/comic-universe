package com.mazeguardians.api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;

/**
 * Optional, read-only content API for a future commercial platform (apps, partner feeds, CMS).
 * Stateless: no accounts, no sessions, no cookies, no personal data.
 */
@SpringBootApplication
public class ComicApiApplication {
    public static void main(String[] args) {
        SpringApplication.run(ComicApiApplication.class, args);
    }
}
