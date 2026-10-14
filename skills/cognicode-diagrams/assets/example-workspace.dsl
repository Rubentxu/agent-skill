workspace "Sistema de ejemplo" {
    model {
        user = person "Usuario"
        system = softwareSystem "Sistema de ejemplo" {
            api = container "API" "Procesa solicitudes" "Rust"
            db = container "Base de datos" "Guarda información" "PostgreSQL"
        }
        user -> api "Usa" "HTTPS"
        api -> db "Consulta" "SQL"
    }
    views {
        systemContext system "Context" {
            include *
            autoLayout lr
        }
        container system "Containers" {
            include *
            autoLayout lr
        }
    }
}
