# Class Diagram — Teacher Classroom Management

```mermaid
classDiagram

    class User {
        +String id
        +String name
        +String email
        +String role
        +String profile_image_url
        +String hashed_password
        +DateTime created_at
    }

    class Classroom {
        +String id
        +String name
        +String subject
        +String course
        +String objectives
        +String level
        +String description
        +DateTime created_at
        +String owner_id
    }

    class Enrollment {
        +String id
        +String classroom_id
        +String student_id
        +Date enrolled_at
    }

    class Invite {
        +String id
        +String code
        +String classroom_id
        +String created_by
        +DateTime created_at
        +DateTime expires_at
        +Integer max_uses
        +Integer uses
        +Boolean is_primary
    }

    class ClassSession {
        +String id
        +String classroom_id
        +DateTime scheduled_at
        +String subject
        +String objectives
        +Boolean auto_recorded
        +DateTime ended_at
    }

    class Presence {
        +String id
        +String session_id
        +String student_id
        +PresenceStatus status
        +DateTime recorded_at
    }

    class PresenceStatus {
        <<enumeration>>
        PRESENT
        ABSENT
        LATE
    }

    class Announcement {
        +String id
        +String classroom_id
        +String author_id
        +String content
        +DateTime created_at
    }

    %% Relationships
    User "1" --> "0..*" Classroom        : owns (teacher)
    User "0..*" --> "0..*" Classroom     : enrolled in (student)
    Classroom "1" *-- "0..*" Enrollment  : has
    Enrollment "0..*" --> "1" User       : student
    Classroom "1" *-- "0..*" Invite      : has
    Invite "0..*" --> "1" User           : created_by
    Classroom "1" *-- "0..*" ClassSession: has
    ClassSession "1" *-- "0..*" Presence : records
    Presence "0..*" --> "1" User         : student
    Presence --> PresenceStatus           : status
    Classroom "1" *-- "0..*" Announcement: has
    Announcement "0..*" --> "1" User     : author
```

## Description des classes

| Classe | Rôle |
|--------|------|
| `User` | Compte utilisateur (teacher ou student). Le champ `role` distingue les deux. |
| `Classroom` | Salle de classe appartenant à un enseignant (`owner_id`). |
| `Enrollment` | Table d'association liant un étudiant à une salle de classe avec la date d'inscription. |
| `Invite` | Code d'invitation permettant à un étudiant de rejoindre une salle. `is_primary = true` = code permanent de la classe. |
| `ClassSession` | Séance de prise de présences. `ended_at = null` signifie que la séance est en cours. |
| `Presence` | Statut de présence d'un étudiant pour une séance donnée (PRESENT / ABSENT / LATE). |
| `Announcement` | Message posté par l'enseignant dans le fil de la salle, visible par tous les inscrits. |
