package com.mazeguardians.api;

import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.header;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.test.autoconfigure.web.servlet.AutoConfigureMockMvc;
import org.springframework.boot.test.context.SpringBootTest;
import org.springframework.test.web.servlet.MockMvc;

@SpringBootTest
@AutoConfigureMockMvc
class ContentControllerTest {

    @Autowired
    private MockMvc mvc;

    @Test
    void listsIssues() throws Exception {
        mvc.perform(get("/api/v1/issues"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$[0].slug").value("issue-1"))
                .andExpect(jsonPath("$[0].panelCount").value(12));
    }

    @Test
    void returnsIssueWithPanels() throws Exception {
        mvc.perform(get("/api/v1/issues/issue-1"))
                .andExpect(status().isOk())
                .andExpect(header().string("Cache-Control", "max-age=600, public"))
                .andExpect(jsonPath("$.title").value("The Great Maze Scramble"))
                .andExpect(jsonPath("$.panels.length()").value(12));
    }

    @Test
    void returnsHeroesAndVillains() throws Exception {
        mvc.perform(get("/api/v1/characters/heroes")).andExpect(status().isOk()).andExpect(jsonPath("$.length()").value(5));
        mvc.perform(get("/api/v1/characters/villains")).andExpect(status().isOk()).andExpect(jsonPath("$.length()").value(3));
        mvc.perform(get("/api/v1/characters/heroes/zayd")).andExpect(status().isOk()).andExpect(jsonPath("$.name").value("Super Zayd"));
    }

    @Test
    void unknownThingsAre404() throws Exception {
        mvc.perform(get("/api/v1/issues/issue-99")).andExpect(status().isNotFound());
        mvc.perform(get("/api/v1/characters/sidekicks")).andExpect(status().isNotFound());
        mvc.perform(get("/api/v1/characters/heroes/nobody")).andExpect(status().isNotFound());
    }
}
