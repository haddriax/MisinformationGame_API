# Database Design Overview

For the database table nomenclature, we use snake_case.
For the ORM Python classes, we use CamelCase.
ex:

- Database table: `study_basic_settings`
- Python class: `StudyBasicSettings`

# Pydantic Class for JSON

- `json_study_models.py`
    - Contains the Python classes used to build the JSON for a full study in the right format.
- `json_result_models.py`
    - Contains the Python classes used to build the JSON with the results of a study in the right format.

## Study Object Composition

A `Study` object consists of four main tables:

- `study_basic_settings`
- `study_advanced_settings`
- `study_pages_settings`
- `study_ui_settings`

Although these components maintain a [1:1] relationship with the `Study`, they are separated to preserve the logic from
the legacy application.

## Key Tables

The following tables represent the structure and components of a Study template, which will be shown to participants:

- `study`
- `avatar`
- `comments`
- `posts`
- `sources`
- `source_style`

## Unused tables (commented in model)

- `comment_interactions`
- `post_interactions`

Those two table are unused in the code yet, but they would fulfill a role if:

- We keep interactions between participant and the `Study`, thus being able to have reactions affecting other
  participants `Study`
- Decomposing the results that are stored in the same JSON legacy format, allowing for more precise querying.

## Participants

Participants are "burner" accounts, meaning they are relevant only for the duration of a single Study. This design
ensures that each participant's data is isolated and specific to one Study.

## Summary

- **Study Object**: Composed of basic, advanced, and page settings.
- **Tables**: Include study, avatar, comments, posts, sources, and source_style, forming the Study template.
- **Participants**: Temporary accounts tied to a single Study for data isolation and relevance.
- 